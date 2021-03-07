# pylint: disable=invalid-name
"""
Send keystrokes to active window

time.sleep -> gevent.sleep for rf2settingswidget
"""
# https://www.reddit.com/r/learnpython/comments/22tke1/use_python_to_send_keystrokes_to_games_in_windows/
# It works in rF2!

import ctypes
import gevent

# DirectInput Key Code Table
#  Macro,           Value, # Symbol, Remarks
DirectInputKeyCodeTable = {
    'DIK_ESCAPE':     (0x01, 0x1B), # Esc
    'DIK_1':          (0x02, 0x31), # 1
    'DIK_2':          (0x03, 0x32), # 2
    'DIK_3':          (0x04, 0x33), # 3
    'DIK_4':          (0x05, 0x34), # 4
    'DIK_5':          (0x06, 0x35), # 5
    'DIK_6':          (0x07, 0x36), # 6
    'DIK_7':          (0x08, 0x37), # 7
    'DIK_8':          (0x09, 0x38), # 8
    'DIK_9':          (0x0A, 0x39), # 9
    'DIK_0':          (0x0B, 0x30), # 0
    'DIK_MINUS':      (0x0C, 0xBD), # -
    'DIK_EQUALS':     (0x0D, 0xB8), # =
    'DIK_BACK':       (0x0E, 0x08), # Back Space
    'DIK_TAB':        (0x0F, 0x09), # Tab
    'DIK_Q':          (0x10, 0x51), # Q
    'DIK_W':          (0x11, 0x57), # W
    'DIK_E':          (0x12, 0x45), # E
    'DIK_R':          (0x13, 0x52), # R
    'DIK_T':          (0x14, 0x54), # T
    'DIK_Y':          (0x15, 0x59), # Y
    'DIK_U':          (0x16, 0x55), # U
    'DIK_I':          (0x17, 0x49), # I
    'DIK_O':          (0x18, 0x4F), # O
    'DIK_P':          (0x19, 0x50), # P
    'DIK_LBRACKET':   (0x1A, 0xDB), # [
    'DIK_RBRACKET':   (0x1B, 0xDD), # ]
    'DIK_RETURN':     (0x1C, 0x0D), # Enter
    'DIK_LCONTROL':   (0x1D, 0x11), # Ctrl (Left)
    'DIK_A':          (0x1E, 0x41), # A
    'DIK_S':          (0x1F, 0x53), # S
    'DIK_D':          (0x20, 0x44), # D
    'DIK_F':          (0x21, 0x46), # F
    'DIK_G':          (0x22, 0x47), # G
    'DIK_H':          (0x23, 0x48), # H
    'DIK_J':          (0x24, 0x4A), # J
    'DIK_K':          (0x25, 0x4B), # K
    'DIK_L':          (0x26, 0x4C), # L
    'DIK_SEMICOLON':  (0x27, 0xBA), # ;
    'DIK_APOSTROPHE': (0x28, 0xC0), #
    'DIK_GRAVE':      (0x29, 0xDF), # `
    'DIK_LSHIFT':     (0x2A, 0xA0), # Shift (Left)
    'DIK_BACKSLASH':  (0x2B, 0xDC), # \
    'DIK_Z':          (0x2C, 0x5A), # Z
    'DIK_X':          (0x2D, 0x58), # X
    'DIK_C':          (0x2E, 0x43), # C
    'DIK_V':          (0x2F, 0x56), # V
    'DIK_B':          (0x30, 0x42), # B
    'DIK_N':          (0x31, 0x4E), # N
    'DIK_M':          (0x32, 0x4D), # M
    'DIK_COMMA':      (0x33, 0xBC), # "# "
    'DIK_PERIOD':     (0x34, 0xBE), # .
    'DIK_SLASH':      (0x35, 0xBF), # /
    'DIK_RSHIFT':     (0x36, 0xA1), # Shift (Right)
    'DIK_MULTIPLY':   (0x37, 0x6A), # * (Numpad)
    'DIK_LMENU':      (0x38, 0x12), # Alt (Left)
    'DIK_SPACE':      (0x39, 0x20), # Space
    'DIK_CAPITAL':    (0x3A, 0x14), # Caps Lock
    'DIK_F1':         (0x3B, 0x70), # F1
    'DIK_F2':         (0x3C, 0x71), # F2
    'DIK_F3':         (0x3D, 0x72), # F3
    'DIK_F4':         (0x3E, 0x73), # F4
    'DIK_F5':         (0x3F, 0x74), # F5
    'DIK_F6':         (0x40, 0x75), # F6
    'DIK_F7':         (0x41, 0x76), # F7
    'DIK_F8':         (0x42, 0x77), # F8
    'DIK_F9':         (0x43, 0x78), # F9
    'DIK_F10':        (0x44, 0x79), # F10
    'DIK_NUMLOCK':    (0x45, 0x90), # Num Lock
    'DIK_SCROLL':     (0x46, 0x91), # Scroll Lock
    'DIK_NUMPAD7':    (0x47, 0x67), # 7 (Numpad)
    'DIK_NUMPAD8':    (0x48, 0x68), # 8 (Numpad)
    'DIK_NUMPAD9':    (0x49, 0x69), # 9 (Numpad)
    'DIK_SUBTRACT':   (0x4A, 0x6D), # - (Numpad)
    'DIK_NUMPAD4':    (0x4B, 0x64), # 4 (Numpad)
    'DIK_NUMPAD5':    (0x4C, 0x65), # 5 (Numpad)
    'DIK_NUMPAD6':    (0x4D, 0x66), # 6 (Numpad)
    'DIK_ADD':        (0x4E, 0x6B), # + (Numpad)
    'DIK_NUMPAD1':    (0x4F, 0x61), # 1 (Numpad)
    'DIK_NUMPAD2':    (0x50, 0x62), # 2 (Numpad)
    'DIK_NUMPAD3':    (0x51, 0x63), # 3 (Numpad)
    'DIK_NUMPAD0':    (0x52, 0x60), # 0 (Numpad)
    'DIK_DECIMAL':    (0x53, 0x6E), # . (Numpad)
    'DIK_F11':        (0x57, 0x7A), # F11
    'DIK_F12':        (0x58, 0x7B), # F12
    'DIK_F13':        (0x64, 0x7C), # F13 # NEC PC-98
    'DIK_F14':        (0x65, 0x7D), # F14 # NEC PC-98
    'DIK_F15':        (0x66, 0x7E), # F15 # NEC PC-98
    'DIK_KANA':       (0x70, 0x0), # Kana # Japanese Keyboard
    'DIK_CONVERT':    (0x79, 0x0), # Convert # Japanese Keyboard
    'DIK_NOCONVERT':  (0x7B, 0x0), # No Convert # Japanese Keyboard
    'DIK_YEN':        (0x7D, 0x0), # ¥, # Japanese Keyboard
    'DIK_NUMPADEQUALS': (0x8D, 0x0), # =,# NEC PC-98
    'DIK_CIRCUMFLEX': (0x90, 0x0), # ^, # Japanese Keyboard
    'DIK_AT':         (0x91, 0x0), # @, # NEC PC-98
    'DIK_COLON':      (0x92, 0x0), # :  # NEC PC-98
    'DIK_UNDERLINE':  (0x93, 0x0), # _, # NEC PC-98
    'DIK_KANJI':      (0x94, 0x0), # Kanji # Japanese Keyboard
    'DIK_STOP':       (0x95, 0x0), # Stop # NEC PC-98
    'DIK_AX':         (0x96, 0x0), # (Japan AX)
    'DIK_UNLABELED':  (0x97, 0x0), # (J3100)
    'DIK_NUMPADENTER':(0x9C, 0x0D), # Enter (Numpad)
    'DIK_RCONTROL':   (0x9D, 0x0), # Ctrl (Right)
    'DIK_NUMPADCOMMA':(0xB3, 0x0), # " #  (Numpad)" # NEC PC-98
    'DIK_DIVIDE':     (0xB5, 0x6F), # / (Numpad)
    'DIK_SYSRQ':      (0xB7, 0x91), # Sys Rq
    'DIK_RMENU':      (0xB8, 0x0), # Alt (Right)
    'DIK_PAUSE':      (0xC5, 0x13), # Pause
    'DIK_HOME':       (0xC7, 0x24), # Home
    'DIK_UP':         (0xC8, 0x26), # Cursor up
    'DIK_PRIOR':      (0xC9, 0x21), # Page Up
    'DIK_LEFT':       (0xCB, 0x25), # Cursor left
    'DIK_RIGHT':      (0xCD, 0x27), # Cursor right
    'DIK_END':        (0xCF, 0x23), # End
    'DIK_DOWN':       (0xD0, 0x28), # Cursor down
    'DIK_NEXT':       (0xD1, 0x22), # Page Down
    'DIK_INSERT':     (0xD2, 0x2D), # Insert
    'DIK_DELETE':     (0xD3, 0x2E), # Delete
    'DIK_LWIN':       (0xDB, 0x5B), # Windows
    'DIK_RWIN':       (0xDC, 0x5D), # Windows
    'DIK_APPS':       (0xDD, 0x0), # Menu
    'DIK_POWER':      (0xDE, 0x0), # Power
    'DIK_SLEEP':      (0xDF, 0x0), # Windows
    }

SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)
# pylint: disable=missing-docstring,too-few-public-methods
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actual Functions

def PressKey(keyStr):
    """
    Press a key
    """
    try:
        hexKeyCode = DirectInputKeyCodeTable[keyStr][0]
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        # pylint: disable=attribute-defined-outside-init
        ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        return True
    except: # pylint: disable=bare-except
        return False

def ReleaseKey(keyStr):
    """
    Release a key
    """
    try:
        hexKeyCode = DirectInputKeyCodeTable[keyStr][0]
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        # pylint: disable=attribute-defined-outside-init
        ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        return True
    except: # pylint: disable=bare-except
        return False

def PressReleaseKey(keyStr):
    """
    Press and release a key
    """
    PressKey(keyStr)
    gevent.sleep(.05)
    ReleaseKey(keyStr)

def KeycodeToDIK(keycode):
    """
    Convert a (Tkinter) keycode to a DirectInput Key code
    If not in table, return keycode as hex
    """
    _res = f'0x{keycode:02x}'
    for dik, entry in DirectInputKeyCodeTable.items():
        if entry[1] == keycode:
            _res = dik
            break
    return _res

def rfKeycodeToDIK(keycode):
    """
    Convert an rFactor keycode to a DirectInput Key code
    If not in table, return keycode as hex
    """
    _res = f'0x{keycode:02x}'
    for dik, entry in DirectInputKeyCodeTable.items():
        if entry[0] == keycode:
            _res = dik
            break
    return _res

if __name__ == "__main__":
    gevent.sleep(3)
    PressKey('DIK_Q')   # press Q
    gevent.sleep(.05)
    ReleaseKey('DIK_Q') # release Q


    from pynput import keyboard

    kc = keyboard.Controller()
    def on_press(key):
        try:
            #print('alphanumeric key {0} pressed'.format(
            #    key.char))
            print(KeycodeToDIK(key.vk))
            kc.press(key)

        except AttributeError:
            #print('special key {0} pressed'.format(
            #   key))
            print(KeycodeToDIK(key.value.vk))
            kc.press(key)

    def on_release(key):
        #print('{0} released'.format(
        #    key))
        if key == keyboard.Key.esc:
            # Stop listener
            return False

    x = keyboard.KeyCode.from_char('abc')

    print('Start pressing keys:')
    # Collect events until released
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()

    # ...or, in a non-blocking fashion:
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()



    from pynput.keyboard import Key, Controller

    keyboard = Controller()

    # Press and release space
    keyboard.press(Key.space)
    keyboard.release(Key.space)

    # Type a lower case A; this will work even if no key on the
    # physical keyboard is labelled 'A'
    keyboard.press('a')
    keyboard.release('a')

    # Type two upper case As
    keyboard.press('A')
    keyboard.release('A')
    with keyboard.pressed(Key.shift):
        keyboard.press('a')
        keyboard.release('a')

    # Type 'Hello World' using the shortcut type method
    keyboard.type('Hello World')