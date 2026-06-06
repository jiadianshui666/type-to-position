import argparse
import ctypes
import msvcrt
import sys
import time
from ctypes import wintypes


user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

SM_CXSCREEN = 0
SM_CYSCREEN = 1
CF_UNICODETEXT = 13

DEFAULT_CONSOLE_COLS = 20
DEFAULT_CONSOLE_LINES = 30


LAST_MOUSE_POSITION: tuple[int, int] | None = None


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class _INPUTunion(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTunion)]


user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
user32.SendInput.restype = wintypes.UINT

user32.SetCursorPos.argtypes = (wintypes.INT, wintypes.INT)
user32.SetCursorPos.restype = wintypes.BOOL

user32.GetSystemMetrics.argtypes = (ctypes.c_int,)
user32.GetSystemMetrics.restype = ctypes.c_int

user32.GetCursorPos.argtypes = (ctypes.POINTER(POINT),)
user32.GetCursorPos.restype = wintypes.BOOL

kernel32.GetConsoleWindow.argtypes = ()
kernel32.GetConsoleWindow.restype = wintypes.HWND

kernel32.GetStdHandle.argtypes = (wintypes.DWORD,)
kernel32.GetStdHandle.restype = wintypes.HANDLE


class COORD(ctypes.Structure):
    _fields_ = [("X", wintypes.SHORT), ("Y", wintypes.SHORT)]


class SMALL_RECT(ctypes.Structure):
    _fields_ = [
        ("Left", wintypes.SHORT),
        ("Top", wintypes.SHORT),
        ("Right", wintypes.SHORT),
        ("Bottom", wintypes.SHORT),
    ]


kernel32.SetConsoleScreenBufferSize.argtypes = (wintypes.HANDLE, COORD)
kernel32.SetConsoleScreenBufferSize.restype = wintypes.BOOL

kernel32.SetConsoleWindowInfo.argtypes = (wintypes.HANDLE, wintypes.BOOL, ctypes.POINTER(SMALL_RECT))
kernel32.SetConsoleWindowInfo.restype = wintypes.BOOL

user32.OpenClipboard.argtypes = (wintypes.HWND,)
user32.OpenClipboard.restype = wintypes.BOOL

user32.CloseClipboard.argtypes = ()
user32.CloseClipboard.restype = wintypes.BOOL

user32.GetClipboardData.argtypes = (wintypes.UINT,)
user32.GetClipboardData.restype = wintypes.HANDLE

kernel32.GlobalLock.argtypes = (wintypes.HGLOBAL,)
kernel32.GlobalLock.restype = wintypes.LPVOID

kernel32.GlobalUnlock.argtypes = (wintypes.HGLOBAL,)
kernel32.GlobalUnlock.restype = wintypes.BOOL


def _press_mouse_left() -> None:
    """模拟鼠标左键按下并松开（一次完整点击）。"""
    extra = ctypes.c_ulong(0)
    inputs = (INPUT * 2)()
    inputs[0] = INPUT(
        type=INPUT_MOUSE,
        u=_INPUTunion(
            mi=MOUSEINPUT(
                dx=0,
                dy=0,
                mouseData=0,
                dwFlags=MOUSEEVENTF_LEFTDOWN,
                time=0,
                dwExtraInfo=ctypes.pointer(extra),
            )
        ),
    )
    inputs[1] = INPUT(
        type=INPUT_MOUSE,
        u=_INPUTunion(
            mi=MOUSEINPUT(
                dx=0,
                dy=0,
                mouseData=0,
                dwFlags=MOUSEEVENTF_LEFTUP,
                time=0,
                dwExtraInfo=ctypes.pointer(extra),
            )
        ),
    )
    sent = user32.SendInput(2, inputs, ctypes.sizeof(INPUT))
    if sent != 2:
        raise ctypes.WinError(ctypes.get_last_error())


def click_at(x: int, y: int) -> None:
    """移动鼠标到 (x, y) 并执行一次左键点击。"""
    if not user32.SetCursorPos(x, y):
        raise ctypes.WinError(ctypes.get_last_error())
    time.sleep(0.05)
    _press_mouse_left()


def type_text(text: str, interval: float = 0.01) -> None:
    """通过 SendInput 逐字模拟键盘输入，支持 Unicode 字符。"""
    extra = ctypes.c_ulong(0)
    for ch in text:
        code = ord(ch)
        down = INPUT(
            type=INPUT_KEYBOARD,
            u=_INPUTunion(
                ki=KEYBDINPUT(
                    wVk=0,
                    wScan=code,
                    dwFlags=KEYEVENTF_UNICODE,
                    time=0,
                    dwExtraInfo=ctypes.pointer(extra),
                )
            ),
        )
        up = INPUT(
            type=INPUT_KEYBOARD,
            u=_INPUTunion(
                ki=KEYBDINPUT(
                    wVk=0,
                    wScan=code,
                    dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP,
                    time=0,
                    dwExtraInfo=ctypes.pointer(extra),
                )
            ),
        )
        sent = user32.SendInput(2, (INPUT * 2)(down, up), ctypes.sizeof(INPUT))
        if sent != 2:
            raise ctypes.WinError(ctypes.get_last_error())
        if interval > 0:
            time.sleep(interval)


def get_clipboard_text() -> str:
    """从系统剪贴板读取 Unicode 文本并返回。"""
    if not user32.OpenClipboard(None):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        handle = user32.GetClipboardData(CF_UNICODETEXT)
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())

        ptr = kernel32.GlobalLock(handle)
        if not ptr:
            raise ctypes.WinError(ctypes.get_last_error())

        try:
            return ctypes.wstring_at(ptr)
        finally:
            kernel32.GlobalUnlock(handle)
    finally:
        user32.CloseClipboard()


def shrink_console_window() -> None:
    """将控制台窗口调整为固定的 20×30。"""
    handle = kernel32.GetStdHandle(wintypes.DWORD(-11))
    if not handle or handle == wintypes.HANDLE(-1):
        return

    # 先把缓冲区设到不小于窗口的尺寸，再把窗口固定为 20×30。
    try:
        buffer_size = COORD(DEFAULT_CONSOLE_COLS, DEFAULT_CONSOLE_LINES)
        window_rect = SMALL_RECT(
            0,
            0,
            DEFAULT_CONSOLE_COLS - 1,
            DEFAULT_CONSOLE_LINES - 1,
        )
        if not kernel32.SetConsoleScreenBufferSize(handle, buffer_size):
            return
        if not kernel32.SetConsoleWindowInfo(handle, True, ctypes.byref(window_rect)):
            return
    except Exception:
        return


def show_mouse_position() -> tuple[int, int] | None:
    """实时显示鼠标坐标，按 Enter 返回当前坐标，按 Ctrl+C 返回 None。"""
    print("## 鼠标坐标监视")
    print("")
    print("- 移动鼠标到目标位置")
    print("- 按 Enter 返回菜单并保留当前坐标")
    print("- 按 Ctrl+C 退出")
    try:
        last_point: tuple[int, int] | None = None
        while True:
            pt = POINT()
            if user32.GetCursorPos(ctypes.byref(pt)):
                print(f"\r- 当前鼠标坐标：X={pt.x}  Y={pt.y}   ", end="", flush=True)
                last_point = (pt.x, pt.y)

            while msvcrt.kbhit():
                key = msvcrt.getwch()
                if key == "\r":
                    print("\n- 已返回菜单。")
                    return last_point
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n- 已退出。")
        return None


def interactive_menu() -> None:
    """交互式功能菜单循环，支持文本输入、剪贴板输入、鼠标坐标查看。"""
    global LAST_MOUSE_POSITION

    while True:
        try:
            print("# 键盘输入工具")
            print("")
            print("## 功能菜单")
            print("1：输入指定文本到指定坐标")
            print("2：从剪贴板输入到指定坐标")
            print("3：查看当前鼠标坐标")
            print("0：退出")
            print("")

            choice = input("**请选择模式(0/1/2/3)： ").strip()
            if choice == "1":
                try:
                    text = input("**请输入内容：** ")
                    if LAST_MOUSE_POSITION is None:
                        x = int(input("**请输入目标 X：** ").strip())
                        y = int(input("**请输入目标 Y：** ").strip())
                    else:
                        x, y = LAST_MOUSE_POSITION
                        print(f"**已使用上次坐标：X={x}，Y={y}")
                    main_with_values(text=text, x=x, y=y, clipboard=False,
                                     delay=1.0, interval=0.01)
                    print("- 已完成，返回菜单。")
                except KeyboardInterrupt:
                    print("\n- 已取消，返回菜单。")
            elif choice == "2":
                try:
                    if LAST_MOUSE_POSITION is None:
                        x = int(input("**请输入目标 X：** ").strip())
                        y = int(input("**请输入目标 Y：** ").strip())
                    else:
                        x, y = LAST_MOUSE_POSITION
                        print(f"**已使用上次坐标：X={x}，Y={y}")
                    main_with_values(text=None, x=x, y=y, clipboard=True,
                                     delay=1.0, interval=0.01)
                    print("- 已完成，返回菜单。")
                except KeyboardInterrupt:
                    print("\n- 已取消，返回菜单。")
            elif choice == "3":
                LAST_MOUSE_POSITION = show_mouse_position()
                print("- 已返回菜单。")
            elif choice == "0":
                print("- 已退出。")
                return
            else:
                print("- 选择无效。")
        except KeyboardInterrupt:
            print("\n- 已取消，返回菜单。")
        except Exception as exc:
            print(f"- 执行失败：{exc}")
            print("- 已返回菜单。")


def main_with_values(*, text: str | None, x: int, y: int, clipboard: bool, delay: float, interval: float) -> None:
    """交互菜单调用的入口：点击坐标后输入文本。"""
    if clipboard:
        text = get_clipboard_text()
    else:
        if text is None:
            raise ValueError("未提供输入内容；请传入 text 或使用 clipboard。")

    screen_w = user32.GetSystemMetrics(SM_CXSCREEN)
    screen_h = user32.GetSystemMetrics(SM_CYSCREEN)
    if not (0 <= x < screen_w and 0 <= y < screen_h):
        raise ValueError(f"坐标超出屏幕范围：({x}, {y})，屏幕为 {screen_w}x{screen_h}")

    click_at(x, y)
    time.sleep(max(0.0, delay))
    type_text(text, interval)


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="点击指定坐标后，模拟键盘输入文本到当前位置。"
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="位置参数：普通模式为 text x y；剪贴板模式为 x y。",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="点击后开始输入前等待的秒数，默认 1.0",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.01,
        help="逐字输入间隔秒数，默认 0.01",
    )
    parser.add_argument(
        "--no-click",
        action="store_true",
        help="只输入，不点击坐标。",
    )
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="从剪贴板读取文本并输入。",
    )
    parser.add_argument(
        "--show-mouse",
        action="store_true",
        help="仅显示当前鼠标坐标，不执行输入。",
    )
    args = parser.parse_args()

    if args.show_mouse:
        return args

    if args.clipboard:
        if len(args.args) != 2:
            parser.error("--clipboard 模式下需要提供 x y，例如：python type_to_position.py --clipboard 500 300")
        args.text = None
        args.x = int(args.args[0])
        args.y = int(args.args[1])
    else:
        if len(args.args) < 3:
            parser.error("普通模式下需要提供 text x y，例如：python type_to_position.py \"你好\" 500 300")
        args.text = " ".join(args.args[:-2])
        args.x = int(args.args[-2])
        args.y = int(args.args[-1])

    return args


def main() -> None:
    """命令行模式入口。"""
    args = parse_args()

    if args.show_mouse:
        show_mouse_position()
        return

    if args.clipboard:
        text = get_clipboard_text()
    else:
        if args.text is None:
            raise ValueError("未提供输入内容；请传入 text 或使用 --clipboard。")
        text = args.text

    screen_w = user32.GetSystemMetrics(SM_CXSCREEN)
    screen_h = user32.GetSystemMetrics(SM_CYSCREEN)
    if not (0 <= args.x < screen_w and 0 <= args.y < screen_h):
        raise ValueError(f"坐标超出屏幕范围：({args.x}, {args.y})，屏幕为 {screen_w}x{screen_h}")

    if not args.no_click:
        click_at(args.x, args.y)
        time.sleep(max(0.0, args.delay))
    type_text(text, args.interval)


if __name__ == "__main__":
    shrink_console_window()
    if len(sys.argv) == 1:
        interactive_menu()
    else:
        main()