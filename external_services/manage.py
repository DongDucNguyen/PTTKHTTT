"""Quản lý các dịch vụ bên ngoài chạy NỀN (không cửa sổ, không cần giữ terminal). Chỉ dùng thư viện chuẩn.

    python manage.py setup [--ai]        tạo môi trường ảo + cài thư viện (--ai: cả dịch vụ AI, nặng ~4 GB)
    python manage.py start  [tên ...]    khởi động nền (mặc định: tất cả dịch vụ đã cài)
    python manage.py stop   [tên ...]
    python manage.py restart [tên ...]
    python manage.py status
    python manage.py logs <tên> [-n 40]
    python manage.py reset [tên ...]     xoá trạng thái (giao dịch, vận đơn, thư) của dịch vụ mô phỏng
    python manage.py autostart install | remove     tự chạy khi đăng nhập Windows (Task Scheduler) — chỉ chạy khi bạn gọi

Tên dịch vụ: payment (ngân hàng, mô phỏng) · shipping (vận chuyển, mô phỏng) · notify (e-mail/SMS, mô phỏng) · ai (THẬT).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(ROOT, "run")
IS_WIN = sys.platform == "win32"
HOST = "127.0.0.1"

# tên: (module uvicorn, cổng mặc định, biến cổng, thư mục venv, biến khoá API, khoá mặc định, thời gian chờ khởi động)
SERVICES = {
    "payment": ("payment_bank.server:app", 8101, ".venv", "EXT_PAYMENT_KEY", "dev-payment-key", 30),
    "shipping": ("shipping.server:app", 8102, ".venv", "EXT_SHIPPING_KEY", "dev-shipping-key", 30),
    "notify": ("notify.server:app", 8103, ".venv", "EXT_NOTIFY_KEY", "dev-notify-key", 30),
    "ai": ("ai_service.server:app", 8104, os.path.join("ai_service", ".venv"), "EXT_AI_KEY", "dev-ai-key", 240),
}


def port_of(name: str) -> int:
    return int(os.environ.get(f"EXT_{name.upper()}_PORT", SERVICES[name][1]))


def key_of(name: str) -> str:
    return os.environ.get(SERVICES[name][3], SERVICES[name][4])


def venv_python(name: str) -> str:
    sub = SERVICES[name][2]
    return os.path.join(ROOT, sub, "Scripts" if IS_WIN else "bin", "python.exe" if IS_WIN else "python")


def pid_file(name: str) -> str:
    return os.path.join(RUN, f"{name}.pid")


def log_file(name: str) -> str:
    return os.path.join(RUN, f"{name}.log")


def read_pid(name: str) -> int | None:
    try:
        return int(open(pid_file(name)).read().strip())
    except (OSError, ValueError):
        return None


def alive(pid: int | None) -> bool:
    if not pid:
        return False
    if IS_WIN:
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout
        return str(pid) in out
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def health(name: str, timeout: float = 2.0) -> dict | None:
    try:
        with urllib.request.urlopen(f"http://{HOST}:{port_of(name)}/health", timeout=timeout) as r:
            return json.load(r)
    except (urllib.error.URLError, OSError, ValueError):
        return None


def installed(name: str) -> bool:
    return os.path.exists(venv_python(name))


def pick(names: list[str]) -> list[str]:
    if not names:
        return [n for n in SERVICES if installed(n)]
    bad = [n for n in names if n not in SERVICES]
    if bad:
        sys.exit(f"Không có dịch vụ: {', '.join(bad)} (có: {', '.join(SERVICES)})")
    return names


def cmd_start(names: list[str]) -> int:
    os.makedirs(RUN, exist_ok=True)
    failed = 0
    for name in pick(names):
        if health(name):
            print(f"{name:9} đã chạy sẵn (cổng {port_of(name)})")
            continue
        if not installed(name):
            print(f"{name:9} CHƯA CÀI: chạy `python manage.py setup{' --ai' if name == 'ai' else ''}`")
            failed += 1
            continue
        module = SERVICES[name][0]
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        log = open(log_file(name), "ab")
        kwargs = {}
        if IS_WIN:
            kwargs["creationflags"] = (subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
                                       | subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            kwargs["start_new_session"] = True
        proc = subprocess.Popen([venv_python(name), "-m", "uvicorn", module, "--host", HOST, "--port", str(port_of(name)),
                                 "--log-level", "info"], cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=log,
                                stderr=subprocess.STDOUT, **kwargs)
        open(pid_file(name), "w").write(str(proc.pid))
        deadline, last = time.time() + SERVICES[name][5], None
        while time.time() < deadline and alive(proc.pid):
            h = health(name)
            if h:
                last = h
                break
            time.sleep(0.5)
        if last is None:
            print(f"{name:9} KHÔNG khởi động được (xem `python manage.py logs {name}`)")
            failed += 1
        else:
            extra = f" · {last['models']}" if "models" in last else ""
            print(f"{name:9} đã chạy nền · cổng {port_of(name)} · pid {proc.pid}{extra}")
    return 1 if failed else 0


def cmd_stop(names: list[str]) -> int:
    for name in pick(names) if names else list(SERVICES):
        pid = read_pid(name)
        if not alive(pid):
            print(f"{name:9} không chạy")
        else:
            if IS_WIN:
                subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
            else:
                os.kill(pid, 15)
            print(f"{name:9} đã dừng (pid {pid})")
        try:
            os.remove(pid_file(name))
        except OSError:
            pass
    return 0


def cmd_status() -> int:
    print(f"{'dịch vụ':9} {'loại':10} {'cổng':5} {'pid':7} trạng thái")
    for name in SERVICES:
        kind = "THẬT" if name == "ai" else "mô phỏng"
        pid, h = read_pid(name), health(name)
        state = "đang chạy" if h else ("đã cài, chưa chạy" if installed(name) else "chưa cài")
        if h and "models" in h:
            state += f" · mô hình: {h['models']}"
        print(f"{name:9} {kind:10} {port_of(name):<5} {str(pid) if alive(pid) else '-':7} {state}")
    return 0


def cmd_logs(name: str, n: int) -> int:
    pick([name])
    try:
        lines = open(log_file(name), encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        sys.exit("Chưa có log")
    print("\n".join(lines[-n:]))
    return 0


def cmd_reset(names: list[str]) -> int:
    for name in pick(names) or []:
        if name == "ai":
            continue
        req = urllib.request.Request(f"http://{HOST}:{port_of(name)}/__admin/reset", method="POST",
                                     headers={"Authorization": f"Bearer {key_of(name)}"})
        try:
            urllib.request.urlopen(req, timeout=5).read()
            print(f"{name:9} đã xoá trạng thái")
        except (urllib.error.URLError, OSError) as e:
            print(f"{name:9} không reset được: {e}")
    return 0


def run(cmd: list[str], **kw) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True, **kw)


def cmd_setup(ai: bool) -> int:
    base = sys.executable
    if not installed("payment"):
        run([base, "-m", "venv", os.path.join(ROOT, ".venv")])
    run([venv_python("payment"), "-m", "pip", "install", "-q", "-r", os.path.join(ROOT, "requirements-sim.txt")])
    print("Đã cài 3 dịch vụ mô phỏng.")
    if ai:
        if not installed("ai"):
            run([base, "-m", "venv", os.path.join(ROOT, "ai_service", ".venv")])
        py = venv_python("ai")
        run([py, "-m", "pip", "install", "-q", "torch", "--index-url", "https://download.pytorch.org/whl/cu128"])
        run([py, "-m", "pip", "install", "-q", "-r", os.path.join(ROOT, "ai_service", "requirements-ai.txt")])
        print("Đã cài thư viện AI. Mô hình CLIP / Whisper tự tải về lần chạy đầu; LLM dùng Ollama "
              "(`ollama pull qwen2.5:3b`).")
    return 0


def cmd_autostart(action: str) -> int:
    if not IS_WIN:
        sys.exit("autostart chỉ hỗ trợ Windows")
    task = "ABCFashionExternalServices"
    if action == "install":
        run(["schtasks", "/Create", "/F", "/SC", "ONLOGON", "/TN", task, "/TR",
             f'"{sys.executable}" "{os.path.join(ROOT, "manage.py")}" start'])
        print("Đã đăng ký tự chạy khi đăng nhập Windows.")
    elif action == "remove":
        run(["schtasks", "/Delete", "/F", "/TN", task])
    else:
        sys.exit("autostart install | remove")
    return 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "setup":
        return cmd_setup("--ai" in rest)
    if cmd == "start":
        return cmd_start(rest)
    if cmd == "stop":
        return cmd_stop(rest)
    if cmd == "restart":
        cmd_stop(rest)
        return cmd_start(rest)
    if cmd == "status":
        return cmd_status()
    if cmd == "logs":
        n = int(rest[rest.index("-n") + 1]) if "-n" in rest else 40
        return cmd_logs([a for a in rest if a != "-n" and not a.isdigit()][0], n)
    if cmd == "reset":
        return cmd_reset(rest)
    if cmd == "autostart":
        return cmd_autostart(rest[0] if rest else "")
    print(__doc__)
    return 2


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    sys.exit(main(sys.argv[1:]))
