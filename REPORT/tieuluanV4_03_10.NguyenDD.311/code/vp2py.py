"""Forward engineering: generate the Python package abc_fashion from the Visual Paradigm
model (Project > Export > XML).  Usage: python3 vp2py.py project.xml out_dir"""
import sys, re, os, collections
from lxml import etree as ET

N = '{http://www.visual-paradigm.com/product/vpuml/modelexporter}'
SRC, OUT = sys.argv[1], sys.argv[2]
R = ET.parse(SRC).getroot()
M = {m.get('id'): m for m in R.iter(N + 'Model')}


def prop(m, name):
    mp = m.find(N + 'ModelProperties')
    if mp is None:
        return None
    for p in mp:
        if p.get('name') == name:
            return p


def sval(m, name):
    p = prop(m, name)
    return None if p is None else p.get('value')


def tval(m, name='type'):
    p = prop(m, name)
    if p is None:
        return ''
    sv = p.find(N + 'StringValue')
    if sv is not None:
        return sv.get('value')
    mr = p.find(N + 'ModelRef')
    if mr is not None and mr.get('id') in M:
        return M[mr.get('id')].get('name')
    return ''


def ftype(m, name='type'):
    t = tval(m, name)
    mod = sval(m, 'typeModifier') or ''
    return (t + mod) if t else ''


def kids(m, t=None):
    ch = m.find(N + 'ChildModels')
    if ch is None:
        return []
    return [x for x in ch if x.tag == N + 'Model' and (t is None or x.get('modelType') == t)]


def stereos(m):
    p = prop(m, 'stereotypes')
    if p is None:
        return []
    return [M[r.get('id')].get('name') for r in p if r.get('id') in M]


root = [m for m in M.values() if m.get('modelType') == 'Package' and m.get('name') == 'abc_fashion'][0]

# ---- owner of each attribute: an attribute listed under two classes belongs to the newest
owners = collections.defaultdict(list)
for c in R.iter(N + 'Model'):
    if c.get('modelType') == 'Class':
        for a in kids(c, 'Attribute'):
            owners[a.get('id')].append(c.get('name'))
SHARED = {aid: own for aid, own in owners.items() if len(own) > 1}
OWNER_FIX = {'tblReview': {'quantity_sold', 'revenue'}}   # moved to StyleStat in the model

# ---- collect classes with their package path
classes = {}          # name -> dict


def walk(pkg, path):
    for k in kids(pkg):
        if k.get('modelType') == 'Package':
            walk(k, path + [k.get('name')])
        elif k.get('modelType') == 'Class':
            classes[k.get('name')] = {'m': k, 'path': path, 'id': k.get('id')}


walk(root, [])
byid = {v['id']: n for n, v in classes.items()}


def is_enum(c):
    return bool(kids(c, 'EnumerationLiteral')) or 'enumeration' in [s.lower() for s in stereos(c)]


# ---- relationships
supers = collections.defaultdict(list)     # sub -> [super]
assocs = collections.defaultdict(list)     # from-class -> [(to-class, aggregation, multiplicity)]
for g in R.iter(N + 'Model'):
    t = g.get('modelType')
    if t == 'Generalization':
        f, to = prop(g, 'from'), prop(g, 'to')
        fi = f.find(N + 'ModelRef').get('id'); ti = to.find(N + 'ModelRef').get('id')
        if fi in byid and ti in byid:
            if byid[fi] not in supers[byid[ti]]:
                supers[byid[ti]].append(byid[fi])          # "from" = super class
    elif t == 'Association':
        mp = g.find(N + 'ModelProperties')
        ends = []
        for tag in ('FromEnd', 'ToEnd'):
            e = mp.find(N + tag) if mp is not None else None
            if e is None:
                e = g.find('.//' + N + tag)
            em = e.find(N + 'Model') if e is not None else None
            if em is None:
                ends.append(None); continue
            ref = prop(em, 'EndModelElement').find(N + 'ModelRef').get('id')
            ends.append((byid.get(ref), sval(em, 'aggregationKind'), sval(em, 'multiplicity')))
        if None in ends or ends[0][0] is None or ends[1][0] is None:
            continue
        (a, agg_a, mul_a), (b, agg_b, mul_b) = ends
        if b not in [x[0] for x in assocs[a]]:
            assocs[a].append((b, agg_a, mul_b))

PYTYPES = {'str', 'int', 'float', 'bool', 'bytes', 'date', 'datetime', 'list', 'dict', 'None'}


def entity_name(t):
    return 'tbl' + t if 'tbl' + t in classes else t


def fix_type(t):
    t = (t or '').strip()
    if not t:
        return ''
    t = re.sub(r'list\s*\[', 'list[', t)
    t = re.sub(r'\s*\|\s*', ' | ', t)
    t = re.sub(r'\b([A-Z]\w*)\b', lambda m: entity_name(m.group(1)), t)
    return t


def names_in(t):
    return {w for w in re.findall(r'\b[A-Za-z_]\w*\b', t) if w in classes}


def snake(n):
    n = n[3:] if n.startswith('tbl') else n
    return re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', n).lower()


# ---- module of every class
module = {}
for n, v in classes.items():
    p = v['path']
    if p[0] == 'model':
        module[n] = 'abc_fashion.model.' + p[1]
    elif p[0] == 'view':
        module[n] = 'abc_fashion.view.%s.%s' % (p[1], snake(n))
    else:  # control.dao / control.gateway
        module[n] = 'abc_fashion.control.%s.%s' % (p[1], snake(n) if n != 'DAO' else 'dao')


def imports_for(mod, used):
    out = collections.defaultdict(set)
    for u in used:
        if u in module and module[u] != mod:
            out[module[u]].add(u)
    return ['from %s import %s' % (k, ', '.join(sorted(v))) for k, v in sorted(out.items())]


def params(op):
    ps = []
    for p in kids(op, 'Parameter'):
        nm, ty = p.get('name'), fix_type(ftype(p))
        ps.append(nm if nm == 'self' or not ty else '%s: %s' % (nm, ty))
    if not ps or not ps[0].startswith('self'):
        ps.insert(0, 'self')
    return ps


def attrs_of(c, name):
    out = []
    for a in kids(c, 'Attribute'):
        if a.get('name') in OWNER_FIX.get(name, ()):
            continue
        out.append((a.get('name'), fix_type(ftype(a)) or 'object', sval(a, 'visibility')))
    return out


HEADER = '# Generated from the Visual Paradigm model "Design" (package %s) -- do not edit the signatures.\n'
files = {}


def doc(name, extra):
    v = classes[name]
    st = stereos(v['m'])
    lines = ['"""%s%s -- layer %s.' % (('<<%s>> ' % ', '.join(st)) if st else '', name,
                                         '.'.join(['abc_fashion'] + v['path']))]
    lines += extra
    if len(lines) == 1:
        return lines[0] + '"""'
    return '\n    '.join(lines) + '\n    """'


# ---------------- model layer: one module per package
for pkg in sorted({v['path'][1] for v in classes.values() if v['path'][0] == 'model'}):
    mod = 'abc_fashion.model.' + pkg
    names = [n for n, v in classes.items() if v['path'] == ['model', pkg]]
    enums = sorted(n for n in names if is_enum(classes[n]['m']))
    ents = [n for n in names if n not in enums]
    # super classes first
    order, seen = [], set()

    def add(n):
        if n in seen or n not in ents:
            return
        for s in supers.get(n, []):
            add(s)
        seen.add(n); order.append(n)
    for n in sorted(ents):
        add(n)
    used = set()
    body = []
    for e in enums:
        body.append('\n\nclass %s(Enum):\n    %s\n' % (e, doc(e, [])))
        for lit in kids(classes[e]['m'], 'EnumerationLiteral'):
            nm = lit.get('name').strip()
            body.append('    %s = "%s"\n' % (nm, nm.lower()))
    for e in order:
        c = classes[e]['m']
        sup = supers.get(e, [])
        used |= set(sup)
        rel = ['%s (%s, %s)' % (b, 'composition' if (agg or '').startswith('Composite') else 'aggregation' if agg == 'Shared' else 'association',
                                mul or '1') for b, agg, mul in assocs.get(e, []) if b in classes]
        body.append('\n\n@dataclass(kw_only=True)\nclass %s%s:\n    %s\n' % (
            e, '(%s)' % ', '.join(sup) if sup else '', doc(e, (['Relationships: ' + '; '.join(rel)] if rel else []))))
        ats = attrs_of(c, e)
        for an, at, vis in ats:
            used |= names_in(at)
            body.append('    %s: %s | None = None\n' % (an, at))
        for op in kids(c, 'Operation'):
            ps = params(op); rt = fix_type(tval(op, 'returnType'))
            for p in ps: used |= names_in(p)
            body.append('\n    def %s(%s)%s:\n        raise NotImplementedError\n' % (op.get('name'), ', '.join(ps), ' -> ' + rt if rt else ''))
        if not ats and not kids(c, 'Operation'):
            body.append('    pass\n')
    imps = [i for i in imports_for(mod, used - set(names))]
    head = HEADER % mod + 'from __future__ import annotations\n\nfrom dataclasses import dataclass\nfrom datetime import date, datetime\nfrom enum import Enum\n'
    if imps:
        head += '\n' + '\n'.join(imps) + '\n'
    files[mod] = head + ''.join(body)

# ---------------- control and view layers: one module per class
for n, v in classes.items():
    if v['path'][0] == 'model':
        continue
    mod = module[n]
    c = v['m']
    used = set(supers.get(n, []))
    sup = supers.get(n, [])
    is_view = v['path'][0] == 'view'
    targets = [(b, agg, mul) for b, agg, mul in assocs.get(n, []) if b in classes]
    daos = [b for b, _, _ in targets if classes[b]['path'][0] == 'control']
    views = [b for b, _, _ in targets if classes[b]['path'][0] == 'view']
    ents = [b for b, _, _ in targets if classes[b]['path'][0] == 'model']
    extra = []
    if daos: extra.append('Uses (control layer): ' + ', '.join(daos))
    if views: extra.append('Opens (view layer): ' + ', '.join(views))
    if ents: extra.append('Holds (model layer): ' + ', '.join(ents))
    base = ', '.join(sup) if sup else ('tk.Toplevel' if is_view else '')
    out = ['\n\nclass %s%s:\n    %s\n' % (n, '(%s)' % base if base else '', doc(n, extra))]
    ats = attrs_of(c, n)
    for an, at, vis in ats:
        used |= names_in(at)
    if ats:
        out.append('\n')
        for an, at, vis in ats:
            out.append('    %s: %s\n' % (an, at))
    for op in kids(c, 'Operation'):
        ps = params(op); rt = fix_type(tval(op, 'returnType'))
        for p in ps: used |= names_in(p)
        sig = '\n    def %s(%s)%s:\n' % (op.get('name'), ', '.join(ps), ' -> ' + rt if rt else '')
        if op.get('name') == '__init__' and is_view:
            lines = ['        super().__init__()\n']
            for p in kids(op, 'Parameter'):
                if p.get('name') != 'self':
                    lines.append('        self.%s = %s\n' % (p.get('name'), p.get('name')))
            for d in daos:
                used.add(d)
                lines.append('        self.%s = %s()\n' % (snake(d), d))
            lines.append('        raise NotImplementedError  # create and place the ttk widgets\n')
            out.append(sig + ''.join(lines))
        elif op.get('name') == '__init__' and n == 'DAO':
            out.append(sig + '        self.con = psycopg.connect(DSN)\n')
        else:
            out.append(sig + '        raise NotImplementedError\n')
    used |= set(daos)
    head = HEADER % mod + 'from __future__ import annotations\n\n'
    if is_view:
        head += 'import tkinter as tk\nfrom tkinter import ttk\n'
    if n == 'DAO':
        head += 'import psycopg\n\nDSN = "dbname=abc_fashion_v2 user=postgres host=localhost port=5432"\n'
    if any(re.search(r'\bdate(time)?\b', l) for l in out):
        head += 'from datetime import date, datetime\n'
    imps = imports_for(mod, used - {n})
    if imps:
        head += '\n' + '\n'.join(imps) + '\n'
    files[mod] = head + ''.join(out)

files['abc_fashion.main'] = (HEADER % 'abc_fashion' +
    'from abc_fashion.view.account.login_frm import LoginFrm\n\n\n'
    'def main() -> None:\n    """Start the desktop application with the login screen (UC02)."""\n'
    '    app = LoginFrm()\n    app.mainloop()\n\n\nif __name__ == "__main__":\n    main()\n')

# ---------------- write
pkgs = set()
for mod, text in files.items():
    parts = mod.split('.')
    path = os.path.join(OUT, *parts) + '.py'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(text)
    for i in range(1, len(parts)):
        pkgs.add(os.path.join(OUT, *parts[:i]))
for p in pkgs:
    ip = os.path.join(p, '__init__.py')
    if not os.path.exists(ip):
        open(ip, 'w').write('')

kinds = collections.Counter()
for n, v in classes.items():
    k = v['path'][0] if v['path'][0] != 'control' else 'control.' + v['path'][1]
    if v['path'][0] == 'model':
        k += '.enum' if is_enum(v['m']) else '.entity'
    kinds[k] += 1
print('modules', len(files), dict(kinds))
print('shared attributes', SHARED)

# ---- statistics for the report
if os.environ.get('STATS'):
    lay = lambda n: classes[n]['path'][0] + ('.' + classes[n]['path'][1] if classes[n]['path'][0] == 'control' else '')
    st = collections.Counter()
    for a, lst in assocs.items():
        for b, agg, mul in lst:
            st[(lay(a), lay(b), agg)] += 1
    for k, v in sorted(st.items()): print(k, v)
    g = collections.Counter((lay(s), lay(p)) for s, ps in supers.items() for p in ps)
    print('generalisations', dict(g))
    us = collections.Counter()
    for u in R.iter(N + 'Model'):
        if u.get('modelType') in ('Usage', 'Dependency', 'Realization'):
            f, t = prop(u, 'from'), prop(u, 'to')
            if f is None or t is None or f.find(N+'ModelRef') is None: continue
            fi, ti = f.find(N + 'ModelRef').get('id'), t.find(N + 'ModelRef').get('id')
            fm, tm = M.get(fi), M.get(ti)
            us[(u.get('modelType'), fm.get('modelType') if fm is not None else None, tm.get('modelType') if tm is not None else None,
                lay(byid[fi]) if fi in byid else '', lay(byid[ti]) if ti in byid else '')] += 1
    for k, v in sorted(us.items(), key=str): print(k, v)
    print('packages', [(p.get('name')) for p in R.iter(N+'Model') if p.get('modelType')=='Package'])
    print('components', [(p.get('name'), stereos(p)) for p in R.iter(N+'Model') if p.get('modelType')=='Component'])
    print('interfaces', [(c.get('name'), [o.get('name') for o in kids(c,'Operation')]) for c in R.iter(N+'Model') if c.get('modelType')=='Class' and 'Interface' in stereos(c)])
