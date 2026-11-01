"""Verification of the generated code: import, layer rules, conformance counts."""
import ast, importlib, pathlib, sys, inspect, enum, collections, types
try:
    import tkinter  # noqa
except ImportError:                       # headless server: replace tkinter by a stub
    tk = types.ModuleType('tkinter'); ttk = types.ModuleType('tkinter.ttk')
    class Toplevel:
        def __init__(self, *a, **k): pass
    tk.Toplevel = Toplevel; tk.ttk = ttk
    ttk.__getattr__ = lambda n: type(n, (), {})
    sys.modules['tkinter'] = tk; sys.modules['tkinter.ttk'] = ttk
root = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(root))
mods = sorted('.'.join(p.relative_to(root).with_suffix('').parts) for p in root.rglob('*.py') if p.name != '__init__.py')
for m in mods:
    importlib.import_module(m)
print('imported modules:', len(mods))
ALLOWED = {'view': {'view', 'control', 'model'}, 'control': {'control', 'model'}, 'model': {'model'}}
viol = []
for p in root.rglob('*.py'):
    parts = p.relative_to(root).parts
    if len(parts) < 3: continue
    layer = parts[1]
    for node in ast.walk(ast.parse(p.read_text())):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith('abc_fashion.'):
            if node.module.split('.')[1] not in ALLOWED[layer]: viol.append((str(p), node.module))
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] + [getattr(node, 'module', '') or '']
            if layer != 'control' and any(n.startswith('psycopg') for n in names): viol.append((str(p), 'psycopg'))
            if layer != 'view' and any(n.startswith('tkinter') for n in names): viol.append((str(p), 'tkinter'))
print('layer violations:', len(viol), viol[:5])
cnt = collections.Counter()
for m in mods:
    for n, c in vars(sys.modules[m]).items():
        if inspect.isclass(c) and c.__module__ == m:
            sp = m.split('.')
            layer = sp[1] + ('.' + sp[2] if sp[1] == 'control' else '')
            cnt[layer + (' enum' if issubclass(c, enum.Enum) else ' class')] += 1
            cnt['operations'] += sum(1 for v in vars(c).values() if inspect.isfunction(v))
print(dict(cnt))
