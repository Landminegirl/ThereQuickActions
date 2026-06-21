
import ctypes
from ctypes import wintypes
import json
import os
import queue
import re
import sys
import threading
import time
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import pystray
    from PIL import Image
    TRAY_AVAILABLE = True
except Exception:
    pystray = None
    Image = None
    TRAY_AVAILABLE = False


APP_NAME = "ThereQuickActions"
CONFIG_FILE = "therequickactions.json"

def is_removed_sample_dance_name(name):
    text = str(name or "").strip().lower()
    squished = re.sub(r"[^a-z0-9]+", "", text)
    return (
        "sailorjupiter" in squished
        or ("sailor" in text and "jupiter" in text)
        or ("jupiter" in text and ("transform" in text or "transformation" in text))
    )


def remove_removed_sample_dances(cfg):
    if isinstance(cfg.get("dance_lists"), list):
        cfg["dance_lists"] = [
            item for item in cfg["dance_lists"]
            if not is_removed_sample_dance_name(item.get("name", ""))
        ]

    if isinstance(cfg.get("dance_hotkey_bindings"), dict):
        for key, dance_name in list(cfg["dance_hotkey_bindings"].items()):
            if is_removed_sample_dance_name(dance_name):
                cfg["dance_hotkey_bindings"][key] = ""

    return cfg


DEFAULT_CONFIG = json.loads('{"chat_key": "Enter", "input_mode": "ScanCode", "focus_delay_ms": 150, "submit_delay_ms": 90, "type_delay_ms": 10, "opacity": 0.92, "slash_open_inserts_slash": true, "auto_lock_last_title": "", "dance_hotkeys_enabled": true, "dance_hotkey_bindings": {"F1": "", "F2": "", "F3": "", "F4": "", "F5": "", "F6": "", "F7": "", "F8": "", "F9": "", "F10": "", "F11": "", "F12": "", "Shift+F1": "", "Shift+F2": "", "Shift+F3": "", "Shift+F4": "", "Shift+F5": "", "Shift+F6": "", "Shift+F7": "", "Shift+F8": "", "Shift+F9": "", "Shift+F10": ""}, "giggles_options": {"page_up_sleep": true, "camera_functions": true, "performers_mode": true, "follow_avatar_name": "", "follow_avatar_names": []}, "dance_lists": [{"name": "Simple Party Loop", "script": "\'wave\\n%delay=\\"700\\"%\\n\'nightfever\\n%delay=\\"1200\\"%\\n\'woohoo\\n%delay=\\"800\\"%\\n\'clap"}], "tabs": [{"id": "emotes", "label": "Emotes", "icon": "☺", "commands": [{"label": "aha", "command": "\'aha"}, {"label": "away", "command": "\'away"}, {"label": "brb", "command": "\'brb"}, {"label": "boo", "command": "\'boo"}, {"label": "burp", "command": "burp"}, {"label": "bye", "command": "\'bye"}, {"label": "cash", "command": "\'cash"}, {"label": "chicken", "command": "\'chicken"}, {"label": "clap", "command": "\'clap"}, {"label": "comehere", "command": "\'comehere"}, {"label": "crickets", "command": "\'crickets"}, {"label": "cuss", "command": "\'cuss"}, {"label": "cutepoints", "command": "\'cutepoints"}, {"label": "dagger", "command": "\'dagger"}, {"label": "doh", "command": "\'doh"}, {"label": "drat", "command": "\'drat"}, {"label": "endkiss", "command": "\'endkiss"}, {"label": "flower", "command": "\'flower"}, {"label": "flowers", "command": "\'flowers"}, {"label": "forward", "command": "\'forward"}, {"label": "frown", "command": "\'frown"}, {"label": "grin", "command": "\'grin"}, {"label": "hearts", "command": "\'hearts"}, {"label": "hmmm", "command": "\'hmmm"}, {"label": "idea", "command": "\'idea"}, {"label": "kiss", "command": "\'kiss"}, {"label": "laugh", "command": "\'laugh"}, {"label": "love", "command": "\'love"}, {"label": "mad", "command": "\'mad"}, {"label": "money", "command": "\'money"}, {"label": "monkey", "command": "\'monkey"}, {"label": "no", "command": "\'no"}, {"label": "nod", "command": "\'nod"}, {"label": "paper", "command": "\'paper"}, {"label": "point", "command": "\'point"}, {"label": "rock", "command": "\'rock"}, {"label": "rolleyes", "command": "\'rolleyes"}, {"label": "scissors", "command": "\'scissors"}, {"label": "sad", "command": "\'sad"}, {"label": "shrug", "command": "\'shrug"}, {"label": "smile", "command": "\'smile"}, {"label": "snake", "command": "\'snake"}, {"label": "surprise", "command": "\'surprise"}, {"label": "swear", "command": "\'swear"}, {"label": "takemic", "command": "\'takemic"}, {"label": "td", "command": "\'td"}, {"label": "tongue", "command": "\'tongue"}, {"label": "towards", "command": "\'towards"}, {"label": "tu", "command": "\'tu"}, {"label": "wave", "command": "\'wave"}, {"label": "what", "command": "\'what"}, {"label": "what 2", "command": "\'\'what"}, {"label": "what 3", "command": "\'\'\'what"}, {"label": "whatever", "command": "\'whatever"}, {"label": "welcome", "command": "\'welcome"}, {"label": "wow", "command": "\'wow"}, {"label": "wow 2", "command": "\'\'wow"}, {"label": "wow 3", "command": "\'\'\'wow"}, {"label": "woohoo", "command": "\'woohoo"}, {"label": "yawn", "command": "\'yawn"}, {"label": "yes", "command": "\'yes"}, {"label": "zzz", "command": "\'zzz"}]}, {"id": "avatar", "label": "Avatar", "icon": "♙", "commands": [{"label": "backpose", "command": "\'backpose"}, {"label": "blowkiss", "command": "\'blowkiss"}, {"label": "bow", "command": "\'bow"}, {"label": "bluesteel", "command": "\'bluesteel"}, {"label": "blush", "command": "\'blush"}, {"label": "clap", "command": "\'clap"}, {"label": "coy", "command": "\'coy"}, {"label": "handup", "command": "\'handup"}, {"label": "hi5", "command": "\'hi5"}, {"label": "hi", "command": "\'hi"}, {"label": "hole", "command": "\'hole"}, {"label": "leftpose", "command": "\'leftpose"}, {"label": "rightpose", "command": "\'rightpose"}, {"label": "rtr", "command": "\'rtr"}, {"label": "sexy", "command": "\'sexy"}, {"label": "td", "command": "\'td"}, {"label": "tada", "command": "\'tada"}, {"label": "ttth", "command": "\'ttth"}, {"label": "wave", "command": "\'wave"}, {"label": "wink", "command": "\'wink"}, {"label": "yada", "command": "\'yada"}, {"label": "yay", "command": "\'yay"}, {"label": "yay 2", "command": "\'\'yay"}, {"label": "yay 3", "command": "\'\'\'yay"}]}, {"id": "dance", "label": "Dance", "icon": "♪", "commands": [{"label": "nightfever", "command": "\'nightfever"}, {"label": "heyhey", "command": "\'heyhey"}, {"label": "twist", "command": "\'twist"}, {"label": "handstand", "command": "\'handstand"}, {"label": "bodywave", "command": "\'bodywave"}, {"label": "yessir", "command": "\'yessir"}, {"label": "giddyup", "command": "\'giddyup"}, {"label": "toehop", "command": "\'toehop"}, {"label": "jig", "command": "\'jig"}, {"label": "irishdance", "command": "\'irishdance"}, {"label": "patch", "command": "\'patch"}, {"label": "clucky", "command": "\'clucky"}, {"label": "chickendance", "command": "\'chickendance"}]}, {"id": "chat", "label": "Chat", "icon": "▣", "commands": [{"label": "rofl", "command": "rofl"}, {"label": "lol", "command": "lol"}, {"label": ":O", "command": ":O"}, {"label": ":P", "command": ":P"}, {"label": ":(", "command": ":("}, {"label": ":)", "command": ":)"}, {"label": "AFK", "command": "AFK"}, {"label": "BRB", "command": "BRB"}, {"label": "LOL", "command": "LOL"}]}, {"id": "slash", "label": "Slash", "icon": "/", "commands": [{"label": "/wave", "command": "/wave"}, {"label": "/sit", "command": "/sit"}, {"label": "/lay", "command": "/lay"}, {"label": "/dance", "command": "/dance"}, {"label": "/laugh", "command": "/laugh"}, {"label": "/cry", "command": "/cry"}, {"label": "/shrug", "command": "/shrug"}, {"label": "/zzz", "command": "/zzz"}, {"label": "/help", "command": "/help"}, {"label": "/respawn", "command": "/respawn"}, {"label": "/store", "command": "/store"}, {"label": "/shout", "command": "/shout ", "needs_text": true, "placeholder": "Message"}, {"label": "/emote", "command": "/emote ", "needs_text": true, "placeholder": "Action"}, {"label": "/friend", "command": "/friend ", "needs_text": true, "placeholder": "Username"}, {"label": "/ignore", "command": "/ignore ", "needs_text": true, "placeholder": "Username"}]}, {"id": "hotkeys", "label": "Keys", "icon": "⌘", "commands": [{"label": "Sector/Zone", "hotkey": ["ctrl", "shift", "h"], "description": "Ctrl + Shift + H"}, {"label": "Offer Ride", "hotkey": ["ctrl", "r"], "description": "Ctrl + R"}]}, {"id": "custom", "label": "Custom", "icon": "✎", "commands": []}, {"id": "autodance", "label": "Auto Dance", "icon": "♫", "commands": []}, {"id": "edgeextras", "label": "Edge Extras", "icon": "✦", "commands": [{"label": "Special thanks to TheChaz for these commands", "url": "https://www.hmph.us/", "description": "hmph.us"}, {"label": "/actionbar /ab", "command": "/actionbar", "description": "Display ActionBar"}, {"label": "/actionmode /am", "command": "/actionmode", "description": "Switch to Action Mode"}, {"label": "/activity /flag", "command": "/activity", "description": "List an activity"}, {"label": "/alltags /tags /allnames /names", "command": "/alltags", "description": "Show all visible nametags"}, {"label": "/arcade", "command": "/arcade", "description": "Turn on arcade mode while track building"}, {"label": "/auctions /auction /ac", "command": "/auctions", "description": "Open auctions page"}, {"label": "/avsearch /avatar", "command": "/avsearch", "description": "Open avatar search page"}, {"label": "/barrel", "command": "/barrel", "description": "Take out a barrel while track building"}, {"label": "/bids", "command": "/bids", "description": "Open bid history page"}, {"label": "/black", "command": "/black", "description": "Use default text color"}, {"label": "/blog /blogs", "command": "/blog", "description": "Open blog page"}, {"label": "/body", "command": "/body", "description": "Use body mirror view"}, {"label": "/brightblue", "command": "/brightblue", "description": "Use bright blue text color"}, {"label": "/brightgreen", "command": "/brightgreen", "description": "Use bright green text color"}, {"label": "/brightred", "command": "/brightred", "description": "Use bright red text color"}, {"label": "/brown", "command": "/brown", "description": "Use brown text color"}, {"label": "/burgundy", "command": "/burgundy", "description": "Use burgundy text color"}, {"label": "/cam", "command": "/cam", "description": "Toggle UserCam+"}, {"label": "/changeme /cm /wear", "command": "/changeme", "description": "Open ChangeMe"}, {"label": "/chatgroup /aj", "command": "/chatgroup", "description": "Toggle Auto-Join Chat Groups"}, {"label": "/chathistory /log /ch", "command": "/chathistory", "description": "Open chat history"}, {"label": "/colview", "command": "/colview", "description": "Show collisions"}, {"label": "/commercehistory /th /thist", "command": "/commercehistory", "description": "Open transaction history page"}, {"label": "/communicator /com", "command": "/communicator", "description": "Open Communicator"}, {"label": "/compass /c /minimap", "command": "/compass", "description": "Open compass or minimap"}, {"label": "/completed /compl", "command": "/completed", "description": "Open completed auctions page"}, {"label": "/crate", "command": "/crate", "description": "Take out a crate while track building"}, {"label": "/cruisecontrol /cc", "command": "/cruisecontrol", "description": "Toggle cruise control"}, {"label": "/darkblue /blue", "command": "/darkblue", "description": "Use dark blue text color"}, {"label": "/darkgreen /green", "command": "/darkgreen", "description": "Use dark green text color"}, {"label": "/darkorange", "command": "/darkorange", "description": "Use dark orange text color"}, {"label": "/darkred /red", "command": "/darkred", "description": "Use dark red text color"}, {"label": "/darkyellow", "command": "/darkyellow", "description": "Use dark yellow text color"}, {"label": "/date", "command": "/date", "description": "Say the current date"}, {"label": "/designer /designs", "command": "/designer", "description": "Open developer auctions page"}, {"label": "/dev", "command": "/dev", "description": "Open developer home page"}, {"label": "/edge /ver /version", "command": "/edge", "description": "Open ThereEdge settings page"}, {"label": "/emote /emotes", "command": "/emote", "description": "Turn on mimic emote mode"}, {"label": "/events", "command": "/events", "description": "Open event schedule page"}, {"label": "/exit", "command": "/exit", "description": "Exit There"}, {"label": "/face", "command": "/face", "description": "Use face mirror view"}, {"label": "/favorite /add", "command": "/favorite", "description": "Add favorite place"}, {"label": "/finishgate /fg", "command": "/finishgate", "description": "Take out a finish gate while track building"}, {"label": "/first", "command": "/first", "description": "Use first person view"}, {"label": "/forcefield /ff /f", "command": "/forcefield", "description": "Toggle forcefield"}, {"label": "/forum /forums", "command": "/forum", "description": "Open member fan sites page"}, {"label": "/fps", "command": "/fps", "description": "Show FPS and PPS hud"}, {"label": "/gate", "command": "/gate", "description": "Take out a gate while track building"}, {"label": "/goto", "command": "/goto", "description": "Open real estate page"}, {"label": "/grandstand /gs", "command": "/grandstand", "description": "Take out a grandstand gate while track building"}, {"label": "/gray /grey", "command": "/gray", "description": "Use grey text color"}, {"label": "/handsfree /hf", "command": "/handsfree", "description": "Toggle hands free"}, {"label": "/happening /hn /now", "command": "/happening", "description": "Open Happening Now page"}, {"label": "/help", "command": "/help", "description": "Open help page"}, {"label": "/hide", "command": "/hide", "description": "Hide huds"}, {"label": "/high /3", "command": "/high", "description": "Use high zoom view"}, {"label": "/home", "command": "/home", "description": "Teleport to your home location"}, {"label": "/ignore", "command": "/ignore", "description": "Open ignore dialog"}, {"label": "/im", "command": "/im", "description": "Open IM dialog"}, {"label": "/joinrace /join /race", "command": "/joinrace", "description": "Join the current race"}, {"label": "/labels", "command": "/labels", "description": "Show object labels"}, {"label": "/leaverace /lr /l", "command": "/leaverace", "description": "Leave the current race"}, {"label": "/local /debug /localhost", "command": "/local", "description": "Open system cockpit page"}, {"label": "/lod", "command": "/lod ", "description": "Adjust LOD distance delta", "needs_text": true, "placeholder": "Value"}, {"label": "/logout /bye", "command": "/logout", "description": "Log out of There"}, {"label": "/low /1", "command": "/low", "description": "Use low zoom view"}, {"label": "/map", "command": "/map", "description": "Open map"}, {"label": "/medium /2", "command": "/medium", "description": "Use medium zoom view"}, {"label": "/music", "command": "/music", "description": "Toggle music"}, {"label": "/mute", "command": "/mute", "description": "Mute audio"}, {"label": "/myitems", "command": "/myitems", "description": "Open auction items page"}, {"label": "/nearesttags /nearestnames", "command": "/nearesttags", "description": "Show 10 nearest nametags"}, {"label": "/neartags /nearnames", "command": "/neartags", "description": "Show all nearby nametags"}, {"label": "/nocolview", "command": "/nocolview", "description": "Hide collisions"}, {"label": "/noemote /noemotes", "command": "/noemote", "description": "Turn off mimic emote mode"}, {"label": "/nofps", "command": "/nofps", "description": "Hide FPS and PPS hud"}, {"label": "/nolabels", "command": "/nolabels", "description": "Hide object labels"}, {"label": "/noquality", "command": "/noquality", "description": "Use normal render settings"}, {"label": "/nospeech", "command": "/nospeech", "description": "Hide speech waveform"}, {"label": "/notags /nonames", "command": "/notags", "description": "Hide all nametags"}, {"label": "/nozones", "command": "/nozones", "description": "Hide zone boundaries"}, {"label": "/orange", "command": "/orange", "description": "Use orange text color"}, {"label": "/organize /o", "command": "/organize", "description": "Open Organizer"}, {"label": "/perf /pk", "command": "/perf", "description": "Open performance knob manager page"}, {"label": "/photo /pic", "command": "/photo", "description": "Take photo"}, {"label": "/pink", "command": "/pink", "description": "Use pink text color"}, {"label": "/places", "command": "/places", "description": "Open real estate page"}, {"label": "/profile /pf", "command": "/profile", "description": "Open profile page"}, {"label": "/purple", "command": "/purple", "description": "Use purple text color"}, {"label": "/quality", "command": "/quality", "description": "Use high performance render settings"}, {"label": "/ramp", "command": "/ramp", "description": "Take out a ramp gate while track building"}, {"label": "/random /rnd", "command": "/random", "description": "Say a random number"}, {"label": "/record", "command": "/record", "description": "Record while track building"}, {"label": "/results /rr", "command": "/results", "description": "Open race results"}, {"label": "/review /reviews /r", "command": "/review", "description": "Open developer reviews page"}, {"label": "/seller /sales", "command": "/seller", "description": "Open sales page"}, {"label": "/settings", "command": "/settings", "description": "Open settings"}, {"label": "/shop", "command": "/shop", "description": "Open Shop Central page"}, {"label": "/show", "command": "/show", "description": "Show huds"}, {"label": "/speech", "command": "/speech", "description": "Show speech waveform"}, {"label": "/standard /0", "command": "/standard", "description": "Use standard view"}, {"label": "/startgate /sg", "command": "/startgate", "description": "Take out a start gate while track building"}, {"label": "/status /avman", "command": "/status", "description": "Open avman status page"}, {"label": "/submissions /subs", "command": "/submissions", "description": "Open developer management tool"}, {"label": "/summon /sm /get", "command": "/summon", "description": "Open summon dialog"}, {"label": "/super /4", "command": "/super", "description": "Use super zoom view"}, {"label": "/tbux /tb", "command": "/tbux", "description": "Open Therebucks purchase page"}, {"label": "/teal", "command": "/teal", "description": "Use teal text color"}, {"label": "/time /t /tt", "command": "/time", "description": "Say the current time"}, {"label": "/tracks", "command": "/tracks", "description": "Open track management tool"}, {"label": "/undo /goback", "command": "/undo", "description": "Undo last teleport"}, {"label": "/unmute", "command": "/unmute", "description": "Unmute audio"}, {"label": "/url", "command": "/url", "description": "Open the last URL typed in chat by anyone"}, {"label": "/var", "command": "/var ", "description": "Set environment variable", "needs_text": true, "placeholder": "Name Value"}, {"label": "/viewscale /vs", "command": "/viewscale ", "description": "Adjust view scale", "needs_text": true, "placeholder": "Scale"}, {"label": "/voice /v", "command": "/voice", "description": "Toggle voice chat"}, {"label": "/voicetrainer /vt", "command": "/voicetrainer", "description": "Open voice trainer page"}, {"label": "/volume /vol", "command": "/volume", "description": "Open volume control"}, {"label": "/weather", "command": "/weather", "description": "Toggle weather"}, {"label": "/web", "command": "/web", "description": "Open the client browser"}, {"label": "/whoami", "command": "/whoami", "description": "Say the avatar\'s name"}, {"label": "/world /5", "command": "/world", "description": "Use world zoom view"}, {"label": "/worldchat /wc", "command": "/worldchat", "description": "Open world chat"}, {"label": "/xsl", "command": "/xsl", "description": "Open profile page without stylesheet"}, {"label": "/yellow", "command": "/yellow", "description": "Use yellow text color"}, {"label": "/zones", "command": "/zones", "description": "Show zone boundaries"}]}, {"id": "bedican", "label": "Bedican", "icon": "⌖", "commands": [{"label": "Bedican Compass command source", "url": "https://www.bedican.co.uk/apps/compass/user-commands.html", "description": "bedican.co.uk"}, {"label": "/utime", "command": "/utime", "description": "Display time in London"}, {"label": "/utime {location}", "command": "/utime ", "needs_text": true, "placeholder": "Location", "description": "Display time in a location"}, {"label": "/ignoring", "command": "/ignoring", "description": "Display how many ignores you have"}, {"label": "/ignoring {avname}", "command": "/ignoring ", "needs_text": true, "placeholder": "Avatar name", "description": "Display ignores for avatar"}, {"label": "/online {avname}", "command": "/online ", "needs_text": true, "placeholder": "Avatar name", "description": "Display if avatar is online"}, {"label": "/weather", "command": "/weather", "description": "Display weather in London"}, {"label": "/weather {location}", "command": "/weather ", "needs_text": true, "placeholder": "Location", "description": "Display weather in location"}, {"label": "/rg /riot", "command": "/rg", "description": "Open Riot_Girl_1 sales"}, {"label": "/guidelines /dg", "command": "/guidelines", "description": "Open developer guidelines"}, {"label": "/submit /sub", "command": "/submit", "description": "Open developer submissions"}, {"label": "/undotele", "command": "/undotele", "description": "Undo teleport"}, {"label": "/schedule", "command": "/schedule", "description": "Open MySchedule"}, {"label": "/decor", "command": "/decor", "description": "View decor"}, {"label": "/schedule /sch /sc", "command": "/schedule", "description": "Open MySchedule"}, {"label": "/devprice", "command": "/devprice", "description": "Open developer prices"}, {"label": "/tagcolor /tagcolour", "command": "/tagcolor", "description": "Open nametag colour chooser"}, {"label": "/spa", "command": "/spa", "description": "Open list of spa locations"}, {"label": "/fr", "command": "/fr", "description": "Open pending friend requests"}, {"label": "/history", "command": "/history", "description": "Open transaction history"}, {"label": "/messagebar /mb", "command": "/messagebar", "description": "Open message bar"}, {"label": "/scbar", "command": "/scbar", "description": "Open shortcut bar"}, {"label": "/buy", "command": "/buy", "description": "Open page to buy more tbux"}, {"label": "/pop", "command": "/pop", "description": "Open population chart"}]}], "dance_loop_default": false, "show_tooltips": true, "always_on_top": true, "custom_buttons": [{"label": "Custom 1", "command": "\'wave", "target_tab": "custom"}, {"label": "Say Hi", "command": "hi", "target_tab": "custom"}], "builder_geometry": "", "show_edge_extras": true, "show_bedican_compass": true, "hide_dance_text": false, "hidden_tabs": [], "topmost_mode": "always", "hide_button_emote_text": false, "tutorial_seen": false, "show_admin_warning": true, "enabled": true, "show_tutorial_on_start": true}')

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

SW_RESTORE = 9
INPUT_KEYBOARD = 1

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008
MAPVK_VK_TO_VSC = 0

WM_HOTKEY = 0x0312
WM_QUIT = 0x0012
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000

VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12
VK_RETURN = 0x0D
VK_SPACE = 0x20
VK_TAB = 0x09
VK_PRIOR = 0x21  # Page Up
VK_OEM_2 = 0xBF

VK_CODES = {
    "None": None,
    "Enter": VK_RETURN,
    "T": 0x54,
    "Y": 0x59,
    "Slash": VK_OEM_2,
    "Space": VK_SPACE,
}

INPUT_MODES = ["ScanCode", "VirtualKey", "Unicode", "ClipboardPaste"]

VK_FKEYS = {
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73,
    "F5": 0x74, "F6": 0x75, "F7": 0x76, "F8": 0x77,
    "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B,
}

HOTKEY_VK = {
    "ctrl": VK_CONTROL,
    "control": VK_CONTROL,
    "shift": VK_SHIFT,
    "alt": VK_MENU,
    "h": 0x48,
    "r": 0x52,
}

ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong



def is_running_as_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


def relaunch_as_admin_if_needed():
    """Relaunch this app with a UAC prompt if it is not already elevated."""
    try:
        if is_running_as_admin():
            return
    except Exception:
        return

    # Avoid retry storms if Windows/user refuses UAC.
    if "--no-admin-relaunch" in sys.argv:
        return

    try:
        if getattr(sys, "frozen", False):
            exe = sys.executable
            params = " ".join([f'"{arg}"' for arg in sys.argv[1:] + ["--no-admin-relaunch"]])
        else:
            exe = sys.executable
            script = os.path.abspath(sys.argv[0])
            params = " ".join([f'"{script}"'] + [f'"{arg}"' for arg in sys.argv[1:] + ["--no-admin-relaunch"]])

        result = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1)

        # ShellExecute returns >32 on success. If UAC is accepted, close this unelevated copy.
        if int(result) > 32:
            raise SystemExit
    except SystemExit:
        raise
    except Exception:
        # If elevation fails, continue and let the red warning explain it.
        pass



class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUTUNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", INPUTUNION),
    ]


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", POINT),
    ]


EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

user32.EnumWindows.argtypes = [EnumWindowsProc, wintypes.LPARAM]
user32.EnumWindows.restype = wintypes.BOOL
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.IsWindow.argtypes = [wintypes.HWND]
user32.IsWindow.restype = wintypes.BOOL
user32.IsIconic.argtypes = [wintypes.HWND]
user32.IsIconic.restype = wintypes.BOOL
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.ShowWindow.restype = wintypes.BOOL
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.BringWindowToTop.argtypes = [wintypes.HWND]
user32.BringWindowToTop.restype = wintypes.BOOL
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
user32.AttachThreadInput.restype = wintypes.BOOL
kernel32.GetCurrentThreadId.restype = wintypes.DWORD
user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT
user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
user32.MapVirtualKeyW.restype = wintypes.UINT
user32.VkKeyScanW.argtypes = [wintypes.WCHAR]
user32.VkKeyScanW.restype = ctypes.c_short
user32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
user32.RegisterHotKey.restype = wintypes.BOOL
user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
user32.UnregisterHotKey.restype = wintypes.BOOL
user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostThreadMessageW.restype = wintypes.BOOL
user32.GetMessageW.argtypes = [ctypes.POINTER(MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = wintypes.BOOL


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(filename):
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return os.path.join(base, filename)
    return os.path.join(app_dir(), filename)


def config_path():
    return os.path.join(app_dir(), CONFIG_FILE)


def ensure_defaults(cfg):
    merged = json.loads(json.dumps(DEFAULT_CONFIG, ensure_ascii=False))
    for key, value in cfg.items():
        merged[key] = value

    tab_ids = [tab.get("id") for tab in merged.get("tabs", []) if isinstance(tab, dict)]
    if "autodance" not in tab_ids and "sets" not in tab_ids:
        merged.setdefault("tabs", []).append({"id": "autodance", "label": "Auto Dance", "icon": "♫", "commands": []})

    for tab in merged.get("tabs", []):
        if isinstance(tab, dict) and tab.get("id") == "sets":
            tab["id"] = "autodance"
            tab["label"] = "Auto Dance"
            tab["icon"] = "♫"

    if "dance_loop_default" not in merged:
        merged["dance_loop_default"] = False

    if "hide_dance_text" not in merged:
        merged["hide_dance_text"] = False

    if "hide_button_emote_text" not in merged:
        merged["hide_button_emote_text"] = False

    if "tutorial_seen" not in merged:
        merged["tutorial_seen"] = False
    if "show_tutorial_on_start" not in merged:
        merged["show_tutorial_on_start"] = True

    if "show_admin_warning" not in merged:
        merged["show_admin_warning"] = True

    if "enabled" not in merged:
        merged["enabled"] = True

    if "hidden_tabs" not in merged or not isinstance(merged.get("hidden_tabs"), list):
        merged["hidden_tabs"] = []

    if "show_tooltips" not in merged:
        merged["show_tooltips"] = True

    if "always_on_top" not in merged:
        merged["always_on_top"] = True

    if "topmost_mode" not in merged:
        merged["topmost_mode"] = "always" if bool(merged.get("always_on_top", True)) else "off"

    if "builder_geometry" not in merged:
        merged["builder_geometry"] = ""

    if "custom_buttons" not in merged or not isinstance(merged.get("custom_buttons"), list):
        merged["custom_buttons"] = [
            {"label": "Custom 1", "command": "'wave", "target_tab": "custom"},
            {"label": "Say Hi", "command": "hi", "target_tab": "custom"}
        ]

    for custom_item in merged.get("custom_buttons", []):
        if isinstance(custom_item, dict):
            custom_item.setdefault("target_tab", "custom")

    tab_ids = [tab.get("id") for tab in merged.get("tabs", []) if isinstance(tab, dict)]
    if "custom" not in tab_ids:
        merged.setdefault("tabs", []).append({"id": "custom", "label": "Custom", "icon": "✎", "commands": []})

    ensure_command_tabs_current(merged)
    reorder_tabs_in_config(merged)

    if "show_edge_extras" not in merged:
        merged["show_edge_extras"] = True

    if "show_bedican_compass" not in merged:
        merged["show_bedican_compass"] = True

    tab_ids = [tab.get("id") for tab in merged.get("tabs", []) if isinstance(tab, dict)]
    if "edgeextras" not in tab_ids:
        merged.setdefault("tabs", []).append({"id": "edgeextras", "label": "Edge Extras", "icon": "✦", "commands": DEFAULT_CONFIG.get("tabs", [])[-2].get("commands", [])})
    if "bedican" not in tab_ids:
        merged.setdefault("tabs", []).append({"id": "bedican", "label": "Bedican", "icon": "⌖", "commands": DEFAULT_CONFIG.get("tabs", [])[-1].get("commands", [])})

    if "dance_lists" in merged and isinstance(merged.get("dance_lists"), list):
        merged["dance_lists"] = [
            item for item in merged["dance_lists"]
            if str(item.get("name", "")).strip().lower() != "sailor jupiter transform"
        ]

    if "dance_lists" not in merged or not isinstance(merged["dance_lists"], list):
        merged["dance_lists"] = DEFAULT_CONFIG["dance_lists"]

    if "dance_hotkey_bindings" not in merged or not isinstance(merged["dance_hotkey_bindings"], dict):
        merged["dance_hotkey_bindings"] = DEFAULT_CONFIG["dance_hotkey_bindings"]

    if "giggles_options" not in merged or not isinstance(merged["giggles_options"], dict):
        merged["giggles_options"] = DEFAULT_CONFIG["giggles_options"]

    merged = remove_removed_sample_dances(merged)
    return merged


def load_config():
    path = config_path()
    if not os.path.exists(path):
        save_config(DEFAULT_CONFIG)
        return ensure_defaults({})

    try:
        with open(path, "r", encoding="utf-8") as f:
            return ensure_defaults(json.load(f))
    except Exception:
        return ensure_defaults({})


def save_config(cfg):
    cfg = remove_removed_sample_dances(cfg)
    with open(config_path(), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)


TAB_ORDER = ["emotes", "avatar", "dance", "chat", "slash", "hotkeys", "custom", "edgeextras", "bedican", "autodance", "sets"]
CUSTOM_TARGETS = [
    ("custom", "Custom"),
    ("emotes", "Emotes"),
    ("avatar", "Avatar"),
    ("dance", "Dance"),
    ("chat", "Chat"),
    ("slash", "Slash"),
    ("hotkeys", "Keys"),
    ("edgeextras", "Edge Extras"),
    ("bedican", "Bedican"),
]


def ensure_command_tabs_current(cfg):
    default_by_id = {tab.get("id"): tab for tab in DEFAULT_CONFIG.get("tabs", []) if isinstance(tab, dict)}
    existing = {tab.get("id"): tab for tab in cfg.get("tabs", []) if isinstance(tab, dict)}
    for tab_id in ("edgeextras", "bedican"):
        if tab_id in default_by_id:
            if tab_id not in existing:
                cfg.setdefault("tabs", []).append(json.loads(json.dumps(default_by_id[tab_id], ensure_ascii=False)))
            else:
                existing[tab_id]["label"] = default_by_id[tab_id].get("label", existing[tab_id].get("label", tab_id))
                existing[tab_id]["icon"] = default_by_id[tab_id].get("icon", existing[tab_id].get("icon", "?"))
                existing[tab_id]["commands"] = default_by_id[tab_id].get("commands", [])
    return cfg


def reorder_tabs_in_config(cfg):
    tabs = cfg.get("tabs", [])
    by_id = {}
    for tab in tabs:
        if isinstance(tab, dict):
            by_id[tab.get("id")] = tab

    ordered = []
    for tab_id in TAB_ORDER:
        if tab_id in by_id and by_id[tab_id] not in ordered:
            ordered.append(by_id[tab_id])

    for tab in tabs:
        if tab not in ordered:
            ordered.append(tab)

    cfg["tabs"] = ordered
    return cfg


def custom_target_label_to_id(label):
    for target_id, target_label in CUSTOM_TARGETS:
        if target_label == label:
            return target_id
    return "custom"


def custom_target_id_to_label(target_id):
    for tid, label in CUSTOM_TARGETS:
        if tid == target_id:
            return label
    return "Custom"


def last_win_error_text():
    err = ctypes.get_last_error()
    if not err:
        return "No Windows error code was returned."
    try:
        return f"Windows error {err}: {ctypes.FormatError(err)}"
    except Exception:
        return f"Windows error {err}"


def get_window_title(hwnd):
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value.strip()


def list_windows(exclude_titles=None):
    exclude_titles = exclude_titles or set()
    results = []

    def callback(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        title = get_window_title(hwnd)
        if not title:
            return True
        if title in exclude_titles:
            return True
        lowered = title.lower()
        if lowered in {"program manager", "settings"}:
            return True
        results.append((int(hwnd), title))
        return True

    user32.EnumWindows(EnumWindowsProc(callback), 0)
    return results


def make_key_input(vk=0, scan=0, flags=0):
    item = INPUT()
    item.type = INPUT_KEYBOARD
    item.u.ki = KEYBDINPUT(wVk=vk, wScan=scan, dwFlags=flags, time=0, dwExtraInfo=0)
    return item


def send_inputs(inputs):
    if not inputs:
        return
    arr = (INPUT * len(inputs))(*inputs)
    ctypes.set_last_error(0)
    sent = user32.SendInput(len(inputs), arr, ctypes.sizeof(INPUT))
    if sent != len(inputs):
        raise OSError(
            "SendInput failed.\n\n"
            f"Sent {sent} of {len(inputs)} input events.\n"
            f"INPUT struct size: {ctypes.sizeof(INPUT)} bytes.\n"
            f"{last_win_error_text()}\n\n"
            "Try Input Mode = ClipboardPaste or VirtualKey. "
            "If every mode fails, the game is blocking injected input."
        )


def vk_to_scan(vk):
    return int(user32.MapVirtualKeyW(vk, MAPVK_VK_TO_VSC))


def key_down(vk, mode="ScanCode"):
    if vk is None:
        return
    if mode == "ScanCode":
        send_inputs([make_key_input(0, vk_to_scan(vk), KEYEVENTF_SCANCODE)])
    else:
        send_inputs([make_key_input(vk, 0, 0)])


def key_up(vk, mode="ScanCode"):
    if vk is None:
        return
    if mode == "ScanCode":
        send_inputs([make_key_input(0, vk_to_scan(vk), KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP)])
    else:
        send_inputs([make_key_input(vk, 0, KEYEVENTF_KEYUP)])


def press_vk(vk, mode="ScanCode", hold_ms=12):
    if vk is None:
        return
    key_down(vk, mode)
    time.sleep(hold_ms / 1000.0)
    key_up(vk, mode)


def send_unicode_text(text, type_delay_ms=0):
    raw = text.encode("utf-16-le", errors="surrogatepass")
    for i in range(0, len(raw), 2):
        code_unit = raw[i] | (raw[i + 1] << 8)
        send_inputs([
            make_key_input(0, code_unit, KEYEVENTF_UNICODE),
            make_key_input(0, code_unit, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP),
        ])
        if type_delay_ms:
            time.sleep(type_delay_ms / 1000.0)


def char_to_vk_and_mods(ch):
    result = user32.VkKeyScanW(ch)
    if result == -1:
        return None, []
    vk = result & 0xFF
    shift_state = (result >> 8) & 0xFF
    mods = []
    if shift_state & 1:
        mods.append(VK_SHIFT)
    if shift_state & 2:
        mods.append(VK_CONTROL)
    if shift_state & 4:
        mods.append(VK_MENU)
    return vk, mods


def send_key_text(text, mode="ScanCode", type_delay_ms=0):
    for ch in text:
        if ch == "\n":
            press_vk(VK_RETURN, mode)
            continue
        if ch == "\t":
            press_vk(VK_TAB, mode)
            continue

        vk, mods = char_to_vk_and_mods(ch)
        if vk is None:
            send_unicode_text(ch, type_delay_ms)
            continue

        for mod in mods:
            key_down(mod, mode)
        press_vk(vk, mode)
        for mod in reversed(mods):
            key_up(mod, mode)

        if type_delay_ms:
            time.sleep(type_delay_ms / 1000.0)


def set_clipboard_text(text):
    root = tk._default_root
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()


def paste_clipboard_text(text, mode="ScanCode"):
    set_clipboard_text(text)
    time.sleep(0.05)
    key_down(VK_CONTROL, mode)
    press_vk(0x56, mode)
    key_up(VK_CONTROL, mode)


def focus_window(hwnd):
    if not hwnd or not user32.IsWindow(hwnd):
        return False

    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, SW_RESTORE)

    fg = user32.GetForegroundWindow()
    current_thread = kernel32.GetCurrentThreadId()
    target_thread = user32.GetWindowThreadProcessId(hwnd, None)
    fg_thread = user32.GetWindowThreadProcessId(fg, None) if fg else 0

    try:
        user32.AttachThreadInput(current_thread, target_thread, True)
        if fg_thread:
            user32.AttachThreadInput(current_thread, fg_thread, True)
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
    finally:
        if fg_thread:
            user32.AttachThreadInput(current_thread, fg_thread, False)
        user32.AttachThreadInput(current_thread, target_thread, False)

    time.sleep(0.05)
    return True


def parse_delay_ms(line):
    nums = re.findall(r"\d+", line)
    if not nums:
        return 500
    return max(0, min(600000, int(nums[0])))


def normalize_dance_script_text(text):
    """Repair scripts that accidentally contain literal backslash-n from older builds."""
    text = str(text or "")
    if "\\n" in text:
        text = text.replace("\\n", "\n")
    return text



def maybe_hide_dance_text(line, enabled):
    """Hide There emote/action word by adding an apostrophe after the emote token."""
    if not enabled:
        return line

    text = str(line or "")
    if not text.strip():
        return text

    leading_len = len(text) - len(text.lstrip(" "))
    leading = text[:leading_len]
    rest = text[leading_len:]

    # Only apostrophe emotes/actions. Slash commands and normal chat are not modified.
    if not rest.startswith("'"):
        return text

    parts = rest.split(" ", 1)
    token = parts[0]
    tail = (" " + parts[1]) if len(parts) > 1 else ""

    # Already hidden, e.g. 'wave' or ''wow'
    if len(token) > 1 and token.endswith("'"):
        return text

    return leading + token + "'" + tail




def draw_round_rect(canvas, x1, y1, x2, y2, r, fill, outline, width=1):
    canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline=fill)
    canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=fill, outline=fill)
    canvas.create_arc(x1, y1, x1 + 2*r, y1 + 2*r, start=90, extent=90, fill=fill, outline=fill)
    canvas.create_arc(x2 - 2*r, y1, x2, y1 + 2*r, start=0, extent=90, fill=fill, outline=fill)
    canvas.create_arc(x1, y2 - 2*r, x1 + 2*r, y2, start=180, extent=90, fill=fill, outline=fill)
    canvas.create_arc(x2 - 2*r, y2 - 2*r, x2, y2, start=270, extent=90, fill=fill, outline=fill)

    if outline:
        canvas.create_line(x1+r, y1, x2-r, y1, fill=outline, width=width)
        canvas.create_line(x1+r, y2, x2-r, y2, fill=outline, width=width)
        canvas.create_line(x1, y1+r, x1, y2-r, fill=outline, width=width)
        canvas.create_line(x2, y1+r, x2, y2-r, fill=outline, width=width)


def blend_hex_color(a, b, t):
    a = a.lstrip("#")
    b = b.lstrip("#")
    ar, ag, ab = int(a[0:2], 16), int(a[2:4], 16), int(a[4:6], 16)
    br, bg, bb = int(b[0:2], 16), int(b[2:4], 16), int(b[4:6], 16)
    r = int(ar + (br - ar) * t)
    g = int(ag + (bg - ag) * t)
    bl = int(ab + (bb - ab) * t)
    return f"#{r:02x}{g:02x}{bl:02x}"


class AquaButton(tk.Canvas):
    def __init__(
        self,
        parent,
        text,
        command=None,
        height=25,
        width=90,
        font=("Arial", 8, "bold"),
        icon=None,
        top_color="#dffcff",
        bottom_color="#72ddea",
        hover_top="#ffffff",
        hover_bottom="#8ef2ff",
        outline="#397b8c",
        text_color="#06313a",
    ):
        super().__init__(parent, height=height, width=width, bg="#c7f3fb", highlightthickness=0, bd=0, cursor="hand2")
        self.text = text
        self.icon = icon
        self.command = command
        self.font = font
        self.top_color = top_color
        self.bottom_color = bottom_color
        self.hover_top = hover_top
        self.hover_bottom = hover_bottom
        self.outline = outline
        self.text_color = text_color
        self._hover = False
        self._redraw_job = None
        self.bind("<Configure>", self.schedule_redraw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", lambda e: self.press())
        self.after_idle(lambda: self.redraw(False))

    def schedule_redraw(self, event=None):
        # Debounce resize storms so scaling/opening windows stays smooth.
        if self._redraw_job is None:
            self._redraw_job = self.after(40, self._do_scheduled_redraw)

    def _do_scheduled_redraw(self):
        self._redraw_job = None
        self.redraw(self._hover)

    def on_enter(self, event=None):
        self._hover = True
        self.redraw(True)

    def on_leave(self, event=None):
        self._hover = False
        self.redraw(False)

    def redraw(self, hover=False):
        try:
            w = max(10, self.winfo_width())
            h = max(10, self.winfo_height())
        except tk.TclError:
            return

        self.delete("all")
        top = self.hover_top if hover else self.top_color
        bottom = self.hover_bottom if hover else self.bottom_color

        draw_round_rect(self, 1, 1, w - 2, h - 2, 7, bottom, self.outline, 1)

        # Fast gradient: 8 bands instead of a line for every pixel.
        bands = 8
        inner_top = 3
        inner_bottom = max(inner_top + 1, h - 4)
        band_h = max(1, (inner_bottom - inner_top) // bands)
        for i in range(bands):
            y1 = inner_top + i * band_h
            y2 = inner_bottom if i == bands - 1 else min(inner_bottom, y1 + band_h)
            color = blend_hex_color(top, bottom, i / max(1, bands - 1))
            self.create_rectangle(4, y1, w - 5, y2, fill=color, outline=color)

        draw_round_rect(self, 1, 1, w - 2, h - 2, 7, "", self.outline, 1)
        self.create_line(6, 3, w - 7, 3, fill="#f2ffff")
        self.create_line(7, 4, w - 8, 4, fill="#cfffff")

        label = f"{self.icon} {self.text}" if self.icon else self.text
        self.create_text(w / 2, h / 2, text=label, fill=self.text_color, font=self.font)

    def press(self):
        if self.command:
            self.command()


class ScrollableCommandPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#ffffff", bd=1, relief="solid")
        self.app = app
        self.canvas = tk.Canvas(self, bg="#ffffff", highlightthickness=0, bd=0)
        self.scroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview, width=16)
        self.inner = tk.Frame(self.canvas, bg="#ffffff")
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")

        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel, add="+")
        self.canvas.bind_all("<Button-4>", self.on_mousewheel_linux, add="+")
        self.canvas.bind_all("<Button-5>", self.on_mousewheel_linux, add="+")

    def pointer_inside(self):
        x, y = self.winfo_pointerxy()
        return (
            self.winfo_rootx() <= x <= self.winfo_rootx() + self.winfo_width()
            and self.winfo_rooty() <= y <= self.winfo_rooty() + self.winfo_height()
        )

    def on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.inner_id, width=event.width)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        if self.pointer_inside():
            step = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(step * 3, "units")
            return "break"

    def on_mousewheel_linux(self, event):
        if self.pointer_inside():
            self.canvas.yview_scroll(-3 if event.num == 4 else 3, "units")
            return "break"

    def clear(self):
        for child in self.inner.winfo_children():
            child.destroy()

    def set_commands(self, commands):
        self.clear()
        if not commands:
            tk.Label(self.inner, text="No commands here.", bg="#ffffff", fg="#333333").pack(padx=8, pady=8)
            return

        for item in commands:
            row = tk.Frame(self.inner, bg="#ffffff")
            row.pack(fill="x", padx=4, pady=3)

            name = str(item.get("label", "Command"))
            desc = str(item.get("description", ""))
            text = f"{name}   {desc}".strip() if "hotkey" in item else name

            if "url" in item:
                btn = AquaButton(
                    row,
                    text=text,
                    command=lambda i=item: self.app.command_clicked(i),
                    height=28,
                    width=180,
                    top_color="#92dcff",
                    bottom_color="#2f93c5",
                    hover_top="#c9f2ff",
                    hover_bottom="#4fb4df",
                    outline="#1c668d",
                    text_color="#002c40",
                )
            else:
                btn = AquaButton(row, text=text, command=lambda i=item: self.app.command_clicked(i), height=28, width=180)
            btn.pack(fill="x")

        self.canvas.yview_moveto(0)


class GlobalHotkeyManager:
    def __init__(self, app):
        self.app = app
        self.thread = None
        self.thread_id = None
        self.running = False
        self.id_to_key = {}

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.thread_main, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread_id:
            try:
                user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)
            except Exception:
                pass

    def restart(self):
        self.stop()
        time.sleep(0.15)
        self.start()

    def thread_main(self):
        self.thread_id = kernel32.GetCurrentThreadId()
        self.id_to_key = {}

        if (not self.app.cfg.get("enabled", True)) or (not self.app.cfg.get("dance_hotkeys_enabled", True)):
            self.running = False
            return

        next_id = 1000
        for key_name, dance_name in self.app.cfg.get("dance_hotkey_bindings", {}).items():
            if not dance_name:
                continue

            mods = MOD_NOREPEAT
            base_key = key_name

            if key_name.startswith("Shift+"):
                mods |= MOD_SHIFT
                base_key = key_name.split("+", 1)[1]

            vk = VK_FKEYS.get(base_key)
            if not vk:
                continue

            if user32.RegisterHotKey(None, next_id, mods, vk):
                self.id_to_key[next_id] = key_name
                next_id += 1
            else:
                self.app.status_queue.put(f"Could not register {key_name}. Another app may own it.")

        if self.app.cfg.get("giggles_options", {}).get("page_up_sleep", True):
            if user32.RegisterHotKey(None, next_id, MOD_NOREPEAT, VK_PRIOR):
                self.id_to_key[next_id] = "__STOP_DANCE__"
                next_id += 1
            else:
                self.app.status_queue.put("Could not register PageUp Stop. Another app may own it.")

        msg = MSG()
        while self.running:
            result = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if result == 0:
                break
            if msg.message == WM_HOTKEY:
                key_name = self.id_to_key.get(int(msg.wParam))
                if key_name:
                    self.app.hotkey_queue.put(key_name)

        for hotkey_id in list(self.id_to_key.keys()):
            try:
                user32.UnregisterHotKey(None, hotkey_id)
            except Exception:
                pass

        self.id_to_key = {}
        self.running = False


class DancePlayer:
    def __init__(self, app):
        self.app = app
        self.thread = None
        self.stop_flag = threading.Event()
        self.generation = 0
        self.current_name = ""
        self.current_loop = False
        self.active = False

    def play(self, name, script, loop=False):
        # Starting any new dance breaks the old loop/player.
        self.stop()
        self.generation += 1
        generation = self.generation
        self.stop_flag.clear()
        self.current_name = name or "Untitled"
        self.current_loop = bool(loop)
        self.active = True
        self.thread = threading.Thread(target=self.run_script, args=(name, script, loop, generation), daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_flag.set()
        self.active = False
        self.current_loop = False

    def wait_interruptible(self, seconds, generation):
        end = time.time() + seconds
        while time.time() < end:
            if self.stop_flag.is_set() or generation != self.generation:
                return False
            time.sleep(0.03)
        return True

    def run_script(self, name, script, loop, generation):
        script = normalize_dance_script_text(script)
        self.app.status_queue.put(f"Playing: {name}" + ("  LOOP" if loop else ""))

        while not self.stop_flag.is_set() and generation == self.generation:
            for raw in script.splitlines():
                if self.stop_flag.is_set() or generation != self.generation:
                    self.app.status_queue.put("Dance stopped.")
                    return

                line = raw.strip()
                if not line or line.startswith("#"):
                    continue

                if line.lower().startswith("%delay") or line.lower().startswith("delay ") or line.lower().startswith("/delay "):
                    ms = parse_delay_ms(line)
                    self.app.status_queue.put(f"Delay {ms} ms")
                    if not self.wait_interruptible(ms / 1000.0, generation):
                        self.app.status_queue.put("Dance stopped.")
                        return
                    continue

                send_line = maybe_hide_dance_text(line, bool(self.app.cfg.get("hide_dance_text", False)))
                self.app.status_queue.put(f"Sending: {send_line}")
                self.app.send_text_to_game(send_line, from_thread=True)

                if not self.wait_interruptible(0.12, generation):
                    self.app.status_queue.put("Dance stopped.")
                    return

            if not loop:
                if generation == self.generation:
                    self.active = False
                    self.current_loop = False
                    self.app.active_hotkey_key = None
                self.app.status_queue.put(f"Done: {name}")
                return

            self.app.status_queue.put(f"Looping: {name}")
            if not self.wait_interruptible(0.25, generation):
                self.app.status_queue.put("Dance stopped.")
                return

        if generation == self.generation:
            self.active = False
            self.current_loop = False
            self.app.active_hotkey_key = None


def gather_builder_actions(cfg):
    actions = []
    seen = set()

    for item in cfg.get("custom_buttons", []):
        if not isinstance(item, dict):
            continue
        label = str(item.get("label", "Custom"))
        command = str(item.get("command", ""))
        if not command:
            continue
        key = (label, command)
        if key not in seen:
            seen.add(key)
            actions.append({"label": label, "command": command, "tab": custom_target_id_to_label(str(item.get("target_tab", "custom")))})

    for tab in cfg.get("tabs", []):
        tab_id = tab.get("id")
        if tab_id in ("autodance", "sets", "hotkeys", "custom"):
            continue
        for item in tab.get("commands", []):
            if "command" not in item:
                continue
            label = str(item.get("label", "Command"))
            command = str(item.get("command", ""))
            if not command:
                continue
            key = (label, command)
            if key in seen:
                continue
            seen.add(key)
            actions.append({"label": label, "command": command, "tab": tab.get("label", "")})
    return actions


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show, add="+")
        widget.bind("<Leave>", self.hide, add="+")
        widget.bind("<ButtonPress>", self.hide, add="+")

    def show(self, event=None):
        if self.tip is not None:
            return
        try:
            owner = getattr(self.widget.winfo_toplevel(), "_there_app", None)
            if owner is not None and not bool(owner.cfg.get("show_tooltips", True)):
                return
        except Exception:
            pass
        try:
            x = self.widget.winfo_rootx() + 12
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
            self.tip = tk.Toplevel(self.widget)
            self.tip.overrideredirect(True)
            self.tip.attributes("-topmost", True)
            self.tip.geometry(f"+{x}+{y}")
            label = tk.Label(
                self.tip,
                text=self.text,
                bg="#ffffd7",
                fg="#00343b",
                bd=1,
                relief="solid",
                padx=6,
                pady=4,
                wraplength=280,
                font=("Arial", 8)
            )
            label.pack()
        except Exception:
            self.tip = None

    def hide(self, event=None):
        if self.tip is not None:
            try:
                self.tip.destroy()
            except Exception:
                pass
            self.tip = None


class DanceListEditor(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#ffffff", bd=1, relief="solid")
        self.app = app
        self.current_name = tk.StringVar(value="")
        self.hotkey_var = tk.StringVar(value="None")
        self.loop_var = tk.BooleanVar(value=bool(self.app.cfg.get("dance_loop_default", False)))
        self.builder_open = False
        self.builder_items = []
        self.builder_category_var = tk.StringVar(value="All")
        self.builder_collapsed_categories = set()
        self.current_loaded_name = ""
        self._loading_selection = False
        self._autosave_job = None
        self.drag_index = None
        self.drop_index = None
        self.drag_ghost = None
        self.drag_payload = None
        self.build()

    def build(self):
        topbar = tk.Frame(self, bg="#d8fbff")
        topbar.pack(fill="x")
        tk.Label(topbar, text="Auto Dance", bg="#d8fbff", fg="#00343b", font=("Arial", 9, "bold")).pack(side="left", padx=6, pady=3)
        AquaButton(topbar, "Create Dance", command=self.toggle_builder, height=24, width=115).pack(side="right", padx=4, pady=2)

        follow_box = tk.Frame(self, bg="#eefcff", bd=1, relief="solid")
        follow_box.pack(fill="x", padx=5, pady=(4, 2))
        follow_box.columnconfigure(1, weight=1)
        follow_box.columnconfigure(4, weight=0)

        tk.Label(
            follow_box,
            text="Follow Moves:",
            bg="#eefcff",
            fg="#00343b",
            font=("Arial", 8, "bold")
        ).grid(row=0, column=0, sticky="w", padx=(6, 4), pady=(4, 2))

        self.follow_avatar_var = tk.StringVar(
            value=str(self.app.cfg.get("giggles_options", {}).get("follow_avatar_name", ""))
        )
        self.follow_avatar_entry = tk.Entry(
            follow_box,
            textvariable=self.follow_avatar_var,
            bg="#ffffff",
            relief="sunken",
            bd=1,
            font=("Arial", 8)
        )
        self.follow_avatar_entry.grid(row=0, column=1, sticky="ew", padx=(0, 4), pady=(4, 2))
        self.follow_avatar_entry.bind("<Return>", lambda e: self.send_follow_moves())
        self.follow_avatar_entry.bind("<FocusOut>", lambda e: self.save_follow_avatar_name())

        AquaButton(follow_box, "Follow", command=self.send_follow_moves, height=24, width=72).grid(row=0, column=2, sticky="e", padx=(0, 4), pady=(3, 2))
        AquaButton(follow_box, "Stop Follow", command=self.stop_follow_moves, height=24, width=92).grid(row=0, column=3, sticky="e", padx=(0, 6), pady=(3, 2))

        tk.Label(
            follow_box,
            text="Saved Names:",
            bg="#eefcff",
            fg="#00343b",
            font=("Arial", 8, "bold")
        ).grid(row=1, column=0, sticky="nw", padx=(6, 4), pady=(2, 5))

        saved_names_frame = tk.Frame(follow_box, bg="#eefcff")
        saved_names_frame.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(0, 4), pady=(2, 5))
        saved_names_frame.columnconfigure(0, weight=1)

        self.follow_names_listbox = tk.Listbox(
            saved_names_frame,
            bg="#ffffff",
            fg="#000000",
            relief="sunken",
            bd=1,
            exportselection=False,
            height=3,
            font=("Arial", 8)
        )
        self.follow_names_listbox.grid(row=0, column=0, sticky="ew")
        self.follow_names_scroll = tk.Scrollbar(saved_names_frame, orient="vertical", command=self.follow_names_listbox.yview, width=12)
        self.follow_names_scroll.grid(row=0, column=1, sticky="ns")
        self.follow_names_listbox.configure(yscrollcommand=self.follow_names_scroll.set)
        self.follow_names_listbox.bind("<<ListboxSelect>>", lambda e: self.use_selected_follow_name())
        self.follow_names_listbox.bind("<Double-Button-1>", lambda e: self.send_follow_moves())

        saved_name_buttons = tk.Frame(follow_box, bg="#eefcff")
        saved_name_buttons.grid(row=1, column=3, sticky="nsew", padx=(0, 6), pady=(2, 5))
        AquaButton(saved_name_buttons, "Add Name", command=self.add_follow_name, height=24, width=92).pack(fill="x", pady=(0, 3))
        AquaButton(saved_name_buttons, "Remove", command=self.remove_follow_name, height=24, width=92).pack(fill="x")

        ToolTip(self.follow_avatar_entry, "Type an avatar name, then Follow sends: /emote AvatarName")
        ToolTip(follow_box, "Giggles-style move following. Stop Follow sends: /emote stop")
        self.refresh_follow_names_list(select_name=self.follow_avatar_var.get().strip())

        options = tk.Frame(self, bg="#eefcff", bd=1, relief="solid")
        options.pack(fill="x", padx=5, pady=(4, 2))
        options.columnconfigure(1, weight=1)

        tk.Label(options, text="Options:", bg="#eefcff", fg="#00343b", font=("Arial", 8, "bold")).grid(row=0, column=0, sticky="nw", padx=(5, 3), pady=2)

        options_rows = tk.Frame(options, bg="#eefcff")
        options_rows.grid(row=0, column=1, sticky="ew")
        row_a = tk.Frame(options_rows, bg="#eefcff")
        row_b = tk.Frame(options_rows, bg="#eefcff")
        row_a.pack(fill="x", anchor="w")
        row_b.pack(fill="x", anchor="w")

        self.hotkeys_enabled = tk.BooleanVar(value=bool(self.app.cfg.get("dance_hotkeys_enabled", True)))
        self.page_sleep = tk.BooleanVar(value=bool(self.app.cfg.get("giggles_options", {}).get("page_up_sleep", True)))
        self.camera_functions = tk.BooleanVar(value=bool(self.app.cfg.get("giggles_options", {}).get("camera_functions", True)))
        self.performers_mode = tk.BooleanVar(value=bool(self.app.cfg.get("giggles_options", {}).get("performers_mode", True)))
        self.hide_dance_text_var = tk.BooleanVar(value=bool(self.app.cfg.get("hide_dance_text", False)))

        cb_hotkeys = tk.Checkbutton(row_a, text="F-Keys", variable=self.hotkeys_enabled, bg="#eefcff", fg="#00343b", command=self.save_options)
        cb_loop = tk.Checkbutton(row_a, text="Loop", variable=self.loop_var, bg="#eefcff", fg="#00343b", command=self.save_loop_default)
        cb_hide_text = tk.Checkbutton(row_a, text="Hide Dance Text", variable=self.hide_dance_text_var, bg="#eefcff", fg="#00343b", command=self.save_options)
        cb_page = tk.Checkbutton(row_b, text="PageUp Stop", variable=self.page_sleep, bg="#eefcff", fg="#00343b", command=self.save_options)
        cb_camera = tk.Checkbutton(row_b, text="Builder Top", variable=self.camera_functions, bg="#eefcff", fg="#00343b", command=self.save_options)
        cb_performers = tk.Checkbutton(row_b, text="Performers", variable=self.performers_mode, bg="#eefcff", fg="#00343b", command=self.save_options)

        for cb in (cb_hotkeys, cb_loop, cb_hide_text):
            cb.pack(side="left", padx=(0, 7))
        for cb in (cb_page, cb_camera, cb_performers):
            cb.pack(side="left", padx=(0, 7))

        ToolTip(cb_hotkeys, "Registers saved Auto Dance sets to F1-F12 / Shift+F1-F10. Turn off if another app needs those keys.")
        ToolTip(cb_loop, "Loops the selected dance until you hit Stop, PageUp Stop, or press the same mapped F-key again.")
        ToolTip(cb_hide_text, "Adds an apostrophe after the emote/action word while Auto Dancing, like 'wave' or 'handup' Name, so nearby chat does not see emote spam.")
        ToolTip(cb_page, "When enabled, PageUp acts like a panic/sleep key and stops the current Auto Dance loop.")
        ToolTip(cb_camera, "Keeps the Create Dance builder window always-on-top. Turn off if you want it behind the game/window.")
        ToolTip(cb_performers, "Performance mode: pressing the same F-key again stops the current loop; a different F-key switches dances.")

        main = tk.Frame(self, bg="#ffffff")
        main.pack(fill="both", expand=True, padx=5, pady=5)
        main.columnconfigure(0, weight=0, minsize=175)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        left = tk.Frame(main, bg="#ffffff")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left.rowconfigure(2, weight=1)
        left.columnconfigure(0, weight=0)
        left.columnconfigure(1, weight=1)

        tk.Label(left, text="Key", bg="#ffffff", fg="#00343b", font=("Arial", 8, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(left, text="Saved Dances", bg="#ffffff", fg="#00343b", font=("Arial", 8, "bold")).grid(row=0, column=1, columnspan=2, sticky="w")

        self.key_listbox = tk.Listbox(left, bg="#eefcff", fg="#00343b", relief="sunken", bd=1, exportselection=False, font=("Arial", 8, "bold"), width=7)
        self.listbox = tk.Listbox(left, bg="#ffffff", fg="#000000", relief="sunken", bd=1, exportselection=False, font=("Arial", 8), width=18)
        self.list_scroll = tk.Scrollbar(left, orient="vertical", command=self.dance_list_yview, width=14)

        self.key_listbox.configure(yscrollcommand=self.sync_dance_list_scroll)
        self.listbox.configure(yscrollcommand=self.sync_dance_list_scroll)

        self.key_listbox.grid(row=2, column=0, sticky="nsew")
        self.listbox.grid(row=2, column=1, sticky="nsew")
        self.list_scroll.grid(row=2, column=2, sticky="ns")

        self.key_listbox.bind("<<ListboxSelect>>", self.on_key_list_selection)
        self.listbox.bind("<<ListboxSelect>>", self.on_list_selection)
        self.key_listbox.bind("<Button-1>", self.on_key_list_click)
        self.key_listbox.bind("<ButtonRelease-1>", self.on_key_list_click)
        self.listbox.bind("<Button-1>", self.on_name_list_click)
        self.listbox.bind("<ButtonRelease-1>", self.on_name_list_click)
        self.key_listbox.bind("<MouseWheel>", lambda e: self.dance_list_mousewheel(e))
        self.listbox.bind("<MouseWheel>", lambda e: self.dance_list_mousewheel(e))

        left_buttons = tk.Frame(left, bg="#ffffff")
        left_buttons.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(5, 0))
        AquaButton(left_buttons, "New", command=self.new_list, height=24, width=70).pack(side="left", fill="x", expand=True, padx=(0, 3))
        AquaButton(left_buttons, "Delete", command=self.delete_list, height=24, width=70).pack(side="left", fill="x", expand=True)

        right = tk.Frame(main, bg="#ffffff")
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(3, weight=1)

        name_row = tk.Frame(right, bg="#ffffff")
        name_row.grid(row=0, column=0, sticky="ew")
        name_row.columnconfigure(1, weight=1)

        tk.Label(name_row, text="Name", bg="#ffffff", fg="#00343b", font=("Arial", 8, "bold")).grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(name_row, textvariable=self.current_name, bg="#ffffff", relief="sunken", bd=1, font=("Arial", 8))
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        key_row = tk.Frame(right, bg="#ffffff")
        key_row.grid(row=1, column=0, sticky="ew", pady=(3, 0))
        tk.Label(key_row, text="F-Key", bg="#ffffff", fg="#00343b", font=("Arial", 8, "bold")).pack(side="left")
        self.hotkey_button = AquaButton(key_row, self.hotkey_var.get() or "None", command=self.open_hotkey_popup, height=24, width=120)
        self.hotkey_button.pack(side="left", padx=(5, 4))
        self.name_entry.bind("<FocusOut>", lambda e: self.auto_save_current(restart_hotkeys=True, refresh=True))

        editor_frame = tk.Frame(right, bg="#ffffff")
        editor_frame.grid(row=3, column=0, sticky="nsew", pady=(5, 4))
        editor_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(0, weight=1)

        self.script_text = tk.Text(editor_frame, bg="#ffffff", fg="#000000", relief="sunken", bd=1, wrap="none", font=("Consolas", 9), undo=True, height=10)
        self.text_y = tk.Scrollbar(editor_frame, orient="vertical", command=self.script_text.yview, width=14)
        self.text_x = tk.Scrollbar(editor_frame, orient="horizontal", command=self.script_text.xview, width=14)
        self.script_text.configure(yscrollcommand=self.text_y.set, xscrollcommand=self.text_x.set)
        self.script_text.grid(row=0, column=0, sticky="nsew")
        self.text_y.grid(row=0, column=1, sticky="ns")
        self.text_x.grid(row=1, column=0, sticky="ew")
        self.script_text.bind("<KeyRelease>", lambda e: self.schedule_autosave())
        self.script_text.bind("<FocusOut>", lambda e: self.auto_save_current(refresh=False))

        # Delay buttons are only in Create Dance now.
        tool_row = tk.Frame(right, bg="#ffffff", height=1)
        tool_row.grid(row=4, column=0, sticky="ew")
        tool_row.grid_propagate(False)

        button_row = tk.Frame(right, bg="#ffffff")
        button_row.grid(row=5, column=0, sticky="ew", pady=(2, 0))
        AquaButton(button_row, "Play", command=self.play_current, height=26, width=80).pack(side="left", fill="x", expand=True, padx=(0, 3))
        AquaButton(button_row, "Stop", command=self.app.stop_dance, height=26, width=80).pack(side="left", fill="x", expand=True)

        self.builder_popup = tk.Toplevel(self)
        self.builder_popup._there_app = self.app
        self.builder_popup.title("Create Dance")
        self.builder_popup.configure(bg="#a5dbe4")
        self.builder_popup.withdraw()
        self.builder_popup.overrideredirect(True)
        self.apply_builder_window_options()
        self.builder_popup.protocol("WM_DELETE_WINDOW", self.hide_builder)

        self.builder_shell = tk.Frame(self.builder_popup, bg="#a5dbe4", bd=1, relief="solid")
        self.builder_shell.pack(fill="both", expand=True, padx=0, pady=0)

        self.builder_titlebar = tk.Frame(self.builder_shell, bg="#9be9f7", height=25)
        self.builder_titlebar.pack(fill="x")
        self.builder_titlebar.pack_propagate(False)
        self.builder_title = tk.Label(self.builder_titlebar, text=" Create Dance", bg="#9be9f7", fg="#002a32", font=("Arial", 9, "bold"), anchor="w")
        self.builder_title.pack(side="left", fill="both", expand=True)
        tk.Button(self.builder_titlebar, text="×", command=self.hide_builder, width=2, bg="#d8ffff", fg="#00434c", relief="ridge", bd=1, font=("Arial", 8, "bold")).pack(side="right", padx=(1, 3), pady=2)

        for widget in (self.builder_titlebar, self.builder_title):
            widget.bind("<ButtonPress-1>", self.start_builder_move)
            widget.bind("<B1-Motion>", self.do_builder_move)
            widget.bind("<ButtonRelease-1>", lambda e: self.save_builder_geometry())

        self.builder_frame = tk.Frame(self.builder_shell, bg="#dffbff", bd=1, relief="solid")
        self.builder_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        self.build_builder_ui()
        self.refresh_lists()

    def apply_builder_window_options(self):
        try:
            self.builder_popup.attributes("-topmost", bool(self.app.cfg.get("always_on_top", True)) and bool(self.camera_functions.get()))
        except Exception:
            pass
        try:
            self.builder_popup.attributes("-alpha", float(self.app.cfg.get("opacity", 0.92)))
        except Exception:
            pass

    def start_builder_move(self, event):
        self._builder_move_dx = event.x_root - self.builder_popup.winfo_x()
        self._builder_move_dy = event.y_root - self.builder_popup.winfo_y()

    def do_builder_move(self, event):
        self.builder_popup.geometry(f"+{event.x_root - self._builder_move_dx}+{event.y_root - self._builder_move_dy}")

    def save_builder_geometry(self):
        try:
            geom = self.builder_popup.geometry()
            if geom:
                self.app.cfg["builder_geometry"] = geom
                save_config(self.app.cfg)
        except Exception:
            pass

    def build_builder_ui(self):
        title = tk.Frame(self.builder_frame, bg="#dffbff")
        title.pack(fill="x")
        tk.Label(title, text="Drag bubbles to reorder. The text list updates live.", bg="#dffbff", fg="#00343b", font=("Arial", 8, "bold")).pack(side="left", padx=5, pady=3)
        AquaButton(title, "OK", command=self.builder_generate_script, height=23, width=55).pack(side="right", padx=(2, 4), pady=2)
        AquaButton(title, "Clear", command=self.builder_clear, height=23, width=55).pack(side="right", padx=2, pady=2)

        body = tk.Frame(self.builder_frame, bg="#dffbff")
        body.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        body.columnconfigure(0, weight=1, minsize=210)
        body.columnconfigure(1, weight=1, minsize=260)
        body.rowconfigure(0, weight=1)

        picker = tk.Frame(body, bg="#ffffff", bd=1, relief="solid")
        picker.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        picker.rowconfigure(3, weight=1)
        picker.columnconfigure(0, weight=1)
        tk.Label(picker, text="Actions", bg="#9be9f7", fg="#00343b", font=("Arial", 8, "bold")).grid(row=0, column=0, sticky="ew")

        category_row = tk.Frame(picker, bg="#ffffff")
        category_row.grid(row=1, column=0, sticky="ew", padx=3, pady=(3, 0))
        tk.Label(category_row, text="Category", bg="#ffffff", fg="#00343b", font=("Arial", 8, "bold")).pack(side="left", padx=(0, 4))
        self.builder_category_combo = ttk.Combobox(category_row, state="readonly", textvariable=self.builder_category_var, values=self.builder_category_values(), width=14)
        self.builder_category_combo.pack(side="left", fill="x", expand=True)
        self.builder_category_combo.bind("<<ComboboxSelected>>", lambda e: self.render_builder_actions())

        self.builder_search_var = tk.StringVar(value="")
        self.builder_search = tk.Entry(picker, textvariable=self.builder_search_var, bg="#ffffff", relief="sunken", bd=1, font=("Arial", 8))
        self.builder_search.grid(row=2, column=0, sticky="ew", padx=3, pady=3)
        self.builder_search.bind("<KeyRelease>", lambda e: self.render_builder_actions())

        action_canvas_frame = tk.Frame(picker, bg="#ffffff")
        action_canvas_frame.grid(row=3, column=0, sticky="nsew")
        action_canvas_frame.rowconfigure(0, weight=1)
        action_canvas_frame.columnconfigure(0, weight=1)
        self.builder_action_canvas = tk.Canvas(action_canvas_frame, bg="#ffffff", highlightthickness=0, height=120)
        self.builder_action_scroll = tk.Scrollbar(action_canvas_frame, orient="vertical", command=self.builder_action_canvas.yview, width=14)
        self.builder_action_inner = tk.Frame(self.builder_action_canvas, bg="#ffffff")
        self.builder_action_id = self.builder_action_canvas.create_window((0, 0), window=self.builder_action_inner, anchor="nw")
        self.builder_action_canvas.configure(yscrollcommand=self.builder_action_scroll.set)
        self.builder_action_canvas.grid(row=0, column=0, sticky="nsew")
        self.builder_action_scroll.grid(row=0, column=1, sticky="ns")
        self.builder_action_inner.bind("<Configure>", lambda e: self.builder_action_canvas.configure(scrollregion=self.builder_action_canvas.bbox("all")))
        self.builder_action_canvas.bind("<Configure>", lambda e: self.builder_action_canvas.itemconfigure(self.builder_action_id, width=e.width))
        self.builder_action_canvas.bind("<MouseWheel>", lambda e: self.builder_action_canvas.yview_scroll((-1 if e.delta > 0 else 1) * 3, "units"))

        bubbles = tk.Frame(body, bg="#ffffff", bd=1, relief="solid")
        bubbles.grid(row=0, column=1, sticky="nsew")
        bubbles.rowconfigure(1, weight=1)
        bubbles.columnconfigure(0, weight=1)
        tk.Label(bubbles, text="Dance Order", bg="#9be9f7", fg="#00343b", font=("Arial", 8, "bold")).grid(row=0, column=0, sticky="ew")

        bubble_canvas_row = tk.Frame(bubbles, bg="#ffffff")
        bubble_canvas_row.grid(row=1, column=0, sticky="nsew")
        bubble_canvas_row.rowconfigure(0, weight=1)
        bubble_canvas_row.columnconfigure(0, weight=1)
        self.bubble_canvas = tk.Canvas(bubble_canvas_row, bg="#ffffff", highlightthickness=0, height=150)
        self.bubble_scroll = tk.Scrollbar(bubble_canvas_row, orient="vertical", command=self.bubble_canvas.yview, width=14)
        self.bubble_inner = tk.Frame(self.bubble_canvas, bg="#ffffff")
        self.bubble_id = self.bubble_canvas.create_window((0, 0), window=self.bubble_inner, anchor="nw")
        self.bubble_canvas.configure(yscrollcommand=self.bubble_scroll.set)
        self.bubble_canvas.grid(row=0, column=0, sticky="nsew")
        self.bubble_scroll.grid(row=0, column=1, sticky="ns")
        self.bubble_inner.bind("<Configure>", lambda e: self.bubble_canvas.configure(scrollregion=self.bubble_canvas.bbox("all")))
        self.bubble_canvas.bind("<Configure>", lambda e: self.bubble_canvas.itemconfigure(self.bubble_id, width=e.width))
        self.bubble_canvas.bind("<MouseWheel>", lambda e: self.bubble_canvas.yview_scroll((-1 if e.delta > 0 else 1) * 3, "units"))

        bubble_tools = tk.Frame(self.builder_frame, bg="#dffbff")
        bubble_tools.pack(fill="x", padx=4, pady=(0, 4))
        AquaButton(bubble_tools, "+ Delay 500", command=lambda: self.builder_add_delay(500), height=23, width=90).pack(side="left", fill="x", expand=True, padx=(0, 3))
        AquaButton(bubble_tools, "+ Delay 1000", command=lambda: self.builder_add_delay(1000), height=23, width=95).pack(side="left", fill="x", expand=True, padx=(0, 3))
        AquaButton(bubble_tools, "+ Delay 2000", command=lambda: self.builder_add_delay(2000), height=23, width=95).pack(side="left", fill="x", expand=True, padx=(0, 3))
        AquaButton(bubble_tools, "Use Current List", command=self.builder_load_from_script, height=23, width=120).pack(side="left", fill="x", expand=True)

        custom_row = tk.Frame(self.builder_frame, bg="#dffbff")
        custom_row.pack(fill="x", padx=4, pady=(0, 4))
        tk.Label(custom_row, text="Custom:", bg="#dffbff", fg="#00343b", font=("Arial", 8, "bold")).pack(side="left", padx=(0, 4))
        self.builder_custom_var = tk.StringVar(value="")
        self.builder_custom_entry = tk.Entry(custom_row, textvariable=self.builder_custom_var, bg="#ffffff", relief="sunken", bd=1, font=("Arial", 8))
        self.builder_custom_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.builder_custom_entry.bind("<Return>", lambda e: self.builder_add_custom_step())
        AquaButton(custom_row, "+ Custom Step", command=self.builder_add_custom_step, height=23, width=110).pack(side="left")

        self.render_builder_actions()
        self.render_bubbles()

    def sync_hotkey_button_to_selected_list_row(self):
        """Force the F-key button to show the key bound to the currently selected saved dance row."""
        try:
            name = self.selected_name()
            if not name:
                name = self.current_name.get().strip()
            self.hotkey_var.set(self.hotkey_for_dance_name(name))
            self.update_hotkey_button()
        except Exception:
            pass

    def hotkey_for_dance_name(self, dance_name):
        for key, value in self.app.cfg.get("dance_hotkey_bindings", {}).items():
            if str(value) == str(dance_name):
                return key
        return "None"

    def open_hotkey_popup(self):
        try:
            if hasattr(self, "hotkey_popup") and self.hotkey_popup is not None and self.hotkey_popup.winfo_exists():
                self.hotkey_popup.destroy()
        except Exception:
            pass

        popup = tk.Toplevel(self)
        self.hotkey_popup = popup
        popup.overrideredirect(True)
        popup.configure(bg="#a5dbe4")
        try:
            popup.transient(self.app.root)
            popup.attributes("-topmost", bool(self.app.cfg.get("always_on_top", True)))
        except Exception:
            pass

        values = ["None"] + list(self.app.cfg.get("dance_hotkey_bindings", {}).keys())
        shell = tk.Frame(popup, bg="#a5dbe4", bd=1, relief="solid")
        shell.pack(fill="both", expand=True)

        max_visible = min(14, len(values))
        listbox = tk.Listbox(shell, bg="#ffffff", fg="#00343b", relief="sunken", bd=1, exportselection=False, font=("Arial", 8), height=max_visible, width=16)
        scroll = tk.Scrollbar(shell, orient="vertical", command=listbox.yview, width=14)
        listbox.configure(yscrollcommand=scroll.set)
        listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        for value in values:
            listbox.insert("end", value)

        current = self.hotkey_var.get() or "None"
        if current in values:
            idx = values.index(current)
            listbox.selection_set(idx)
            listbox.see(idx)

        def choose(event=None):
            sel = listbox.curselection()
            if not sel:
                return

            chosen_key = values[int(sel[0])]
            current_dance = self.current_name.get().strip() or self.selected_name()
            if chosen_key != "None":
                existing_dance = self.app.cfg.get("dance_hotkey_bindings", {}).get(chosen_key, "")
                if existing_dance and existing_dance != current_dance:
                    try:
                        popup.attributes("-topmost", False)
                    except Exception:
                        pass
                    answer = messagebox.askyesno(
                        APP_NAME,
                        f"{chosen_key} is already assigned to:\n\n{existing_dance}\n\nOverwrite it and assign {chosen_key} to:\n\n{current_dance}?",
                        parent=self.app.root
                    )
                    try:
                        popup.attributes("-topmost", bool(self.app.cfg.get("always_on_top", True)))
                        popup.lift(self.app.root)
                    except Exception:
                        pass
                    if not answer:
                        return

            self.hotkey_var.set(chosen_key)
            self.update_hotkey_button()
            try:
                popup.destroy()
            except Exception:
                pass
            self.auto_save_current(restart_hotkeys=True, refresh=True)
            self.sync_hotkey_button_to_selected_list_row()

        listbox.bind("<Double-Button-1>", choose)
        listbox.bind("<Return>", choose)
        listbox.bind("<ButtonRelease-1>", choose)
        listbox.bind("<Escape>", lambda e: popup.destroy())

        x = self.hotkey_button.winfo_rootx()
        y = self.hotkey_button.winfo_rooty() + self.hotkey_button.winfo_height() + 2
        popup.geometry(f"+{x}+{y}")
        try:
            popup.lift(self.app.root)
            popup.focus_force()
            listbox.focus_set()
        except Exception:
            pass

    def update_hotkey_button(self, sync_from_current=False):
        if sync_from_current:
            current_name = self.current_name.get().strip()
            self.hotkey_var.set(self.hotkey_for_dance_name(current_name))

        if hasattr(self, "hotkey_button"):
            self.hotkey_button.text = self.hotkey_var.get() or "None"
            self.hotkey_button.redraw(False)

    def dance_key_for_name(self, dance_name):
        for key, value in self.app.cfg.get("dance_hotkey_bindings", {}).items():
            if value == dance_name:
                return key
        return ""

    def sync_dance_list_scroll(self, first, last):
        try:
            self.list_scroll.set(first, last)
        except Exception:
            pass

    def dance_list_yview(self, *args):
        try:
            self.listbox.yview(*args)
            self.key_listbox.yview(*args)
        except Exception:
            pass

    def dance_list_mousewheel(self, event):
        delta = (-1 if event.delta > 0 else 1) * 3
        self.listbox.yview_scroll(delta, "units")
        self.key_listbox.yview_scroll(delta, "units")
        return "break"

    def sync_list_selection(self, index):
        try:
            self._loading_selection = True
            self.listbox.selection_clear(0, "end")
            self.key_listbox.selection_clear(0, "end")
            self.listbox.selection_set(index)
            self.key_listbox.selection_set(index)
            self.listbox.see(index)
            self.key_listbox.see(index)
        finally:
            self._loading_selection = False

    def select_dance_index(self, index):
        try:
            index = int(index)
        except Exception:
            return
        if index < 0 or index >= self.listbox.size():
            return
        if self.current_loaded_name:
            self.auto_save_current(restart_hotkeys=True, refresh=False)
        self.sync_list_selection(index)
        self.load_selected()
        try:
            self.after_idle(self.sync_hotkey_button_to_selected_list_row)
        except Exception:
            pass

    def on_name_list_click(self, event=None):
        try:
            index = self.listbox.nearest(event.y)
        except Exception:
            return
        self.select_dance_index(index)
        return "break"

    def on_key_list_click(self, event=None):
        try:
            index = self.key_listbox.nearest(event.y)
        except Exception:
            return
        self.select_dance_index(index)
        return "break"

    def on_key_list_selection(self, event=None):
        if self._loading_selection:
            return
        sel = self.key_listbox.curselection()
        if not sel:
            return
        self.select_dance_index(int(sel[0]))

    def refresh_lists(self, keep_name=None):
        keep_name = keep_name if keep_name is not None else (self.current_loaded_name or self.current_name.get())
        self.listbox.delete(0, "end")
        self.key_listbox.delete(0, "end")

        for item in self.app.cfg.get("dance_lists", []):
            name = item.get("name", "Untitled")
            key = self.dance_key_for_name(name)
            self.key_listbox.insert("end", key if key else "—")
            self.listbox.insert("end", name)

        if self.listbox.size() == 0:
            return

        index_to_pick = 0
        for i in range(self.listbox.size()):
            if self.listbox.get(i) == keep_name:
                index_to_pick = i
                break

        self.sync_list_selection(index_to_pick)

        if not self.current_loaded_name:
            self.load_selected()
        else:
            self.sync_hotkey_button_to_selected_list_row()

    def selected_name(self):
        sel = self.listbox.curselection()
        if not sel:
            return ""
        return self.listbox.get(sel[0])

    def find_index(self, name):
        for i, item in enumerate(self.app.cfg.get("dance_lists", [])):
            if item.get("name") == name:
                return i
        return -1

    def on_list_selection(self, event=None):
        if self._loading_selection:
            return
        sel = self.listbox.curselection()
        if not sel:
            return
        self.select_dance_index(int(sel[0]))

    def load_selected(self):
        name = self.selected_name()
        idx = self.find_index(name)
        if idx < 0:
            return
        self._loading_selection = True
        try:
            item = self.app.cfg["dance_lists"][idx]
            self.current_loaded_name = item.get("name", "Untitled")
            self.current_name.set(self.current_loaded_name)
            self.script_text.delete("1.0", "end")
            self.script_text.insert("1.0", normalize_dance_script_text(item.get("script", "")))
            bound = "None"
            for key, value in self.app.cfg.get("dance_hotkey_bindings", {}).items():
                if value == item.get("name"):
                    bound = key
                    break
            self.hotkey_var.set(bound)
            self.update_hotkey_button()
        finally:
            self._loading_selection = False
        self.sync_hotkey_button_to_selected_list_row()

        if self.builder_open:
            self.builder_load_from_script()

    def schedule_autosave(self, delay_ms=450):
        if self._loading_selection:
            return
        if self._autosave_job is not None:
            try:
                self.after_cancel(self._autosave_job)
            except Exception:
                pass
        self._autosave_job = self.after(delay_ms, lambda: self.auto_save_current(refresh=False))

    def auto_save_current(self, restart_hotkeys=False, refresh=False):
        if self._loading_selection:
            return False
        old_name = self.current_loaded_name or self.selected_name()
        name = self.current_name.get().strip() or old_name or "Untitled Dance"
        script = normalize_dance_script_text(self.script_text.get("1.0", "end-1c"))
        lists = self.app.cfg.setdefault("dance_lists", [])
        idx = self.find_index(old_name) if old_name else -1
        if idx < 0:
            idx = self.find_index(name)
        if idx < 0:
            lists.append({"name": name, "script": script})
            idx = len(lists) - 1
        else:
            lists[idx] = {"name": name, "script": script}

        bindings = self.app.cfg.setdefault("dance_hotkey_bindings", {})
        chosen = self.hotkey_var.get()
        if restart_hotkeys:
            for key, value in list(bindings.items()):
                if value == old_name or value == name:
                    bindings[key] = ""
            if chosen and chosen != "None":
                bindings[chosen] = name
        save_config(self.app.cfg)
        self.current_loaded_name = name
        try:
            if 0 <= idx < self.listbox.size():
                key_label = self.dance_key_for_name(name) or "—"
                if self.listbox.get(idx) != name:
                    self.listbox.delete(idx)
                    self.listbox.insert(idx, name)
                self.key_listbox.delete(idx)
                self.key_listbox.insert(idx, key_label)
                self.sync_list_selection(idx)
        except Exception:
            pass
        if restart_hotkeys:
            self.app.restart_hotkeys()
        if refresh:
            self.refresh_lists(keep_name=name)
            self.sync_hotkey_button_to_selected_list_row()  # after autosave
        return True

    def new_list(self):
        existing = {d.get("name") for d in self.app.cfg.get("dance_lists", [])}
        base = "New Dance Set"
        name = base
        n = 2
        while name in existing:
            name = f"{base} {n}"
            n += 1
        if self.current_loaded_name:
            self.auto_save_current(restart_hotkeys=True, refresh=False)
        self.app.cfg.setdefault("dance_lists", []).append({"name": name, "script": ""})
        save_config(self.app.cfg)
        self.current_loaded_name = name
        self.current_name.set(name)
        self.script_text.delete("1.0", "end")
        self.hotkey_var.set("None")
        self.refresh_lists(keep_name=name)
        if self.builder_open:
            self.builder_items = []
            self.render_bubbles()

    def delete_list(self):
        name = self.current_loaded_name or self.current_name.get().strip()
        if not name:
            return
        try:
            self.app.root.attributes("-topmost", False)
        except Exception:
            pass
        answer = messagebox.askyesno(APP_NAME, f"Delete dance list '{name}'?", parent=self.app.root)
        self.app.apply_runtime_settings(save=False)
        if not answer:
            return
        self.app.cfg["dance_lists"] = [d for d in self.app.cfg.get("dance_lists", []) if d.get("name") != name]
        for key, value in list(self.app.cfg.get("dance_hotkey_bindings", {}).items()):
            if value == name:
                self.app.cfg["dance_hotkey_bindings"][key] = ""
        save_config(self.app.cfg)
        self.app.restart_hotkeys()
        self.current_loaded_name = ""
        self.current_name.set("")
        self.script_text.delete("1.0", "end")
        self.hotkey_var.set("None")
        self.refresh_lists()
        if self.builder_open:
            self.builder_items = []
            self.render_bubbles()

    def save_current(self):
        self.auto_save_current(restart_hotkeys=True, refresh=True)

    def play_current(self):
        self.auto_save_current(restart_hotkeys=True, refresh=False)
        self.app.active_hotkey_key = None
        self.app.play_dance(self.current_name.get().strip(), normalize_dance_script_text(self.script_text.get("1.0", "end-1c")), loop=bool(self.loop_var.get()))

    def insert_delay(self, ms):
        self.script_text.insert("insert", f"%delay=\"{ms}\"%\\n")
        self.auto_save_current(refresh=False)

    def insert_edit_box(self):
        text = self.app.edit_var.get().strip()
        if text:
            self.script_text.insert("insert", text + "\\n")
            self.auto_save_current(refresh=False)

    def save_loop_default(self):
        self.app.cfg["dance_loop_default"] = bool(self.loop_var.get())
        self.app.cfg["hide_dance_text"] = bool(self.hide_dance_text_var.get())
        save_config(self.app.cfg)

    def hide_builder(self):
        self.save_builder_geometry()
        try:
            self.builder_popup.withdraw()
        except Exception:
            pass
        self.builder_open = False

    def toggle_builder(self):
        if self.builder_open:
            self.hide_builder()
            return
        self.apply_builder_window_options()
        geom = str(self.app.cfg.get("builder_geometry", "")).strip()
        if geom:
            self.builder_popup.geometry(geom)
        else:
            try:
                self.app.root.update_idletasks()
                x = self.app.root.winfo_rootx() + self.app.root.winfo_width() + 8
                y = self.app.root.winfo_rooty()
            except Exception:
                x, y = 120, 120
            self.builder_popup.geometry(f"650x540+{x}+{y}")
        self.builder_popup.minsize(500, 400)
        self.builder_popup.deiconify()
        try:
            self.app.show_popup_above_main(self.builder_popup)
        except Exception:
            self.builder_popup.lift()
        self.builder_popup.focus_force()
        self.builder_open = True
        self.render_builder_actions()
        self.builder_load_from_script()

    def script_from_builder_items(self):
        lines = []
        for item in self.builder_items:
            if item["type"] == "delay":
                lines.append(f"%delay=\"{int(item['value'])}\"%")
            else:
                lines.append(str(item["value"]))
        return "\n".join(lines)

    def sync_builder_to_script(self):
        script = self.script_from_builder_items()
        self.script_text.delete("1.0", "end")
        self.script_text.insert("1.0", script)
        self.auto_save_current(refresh=False)

    def builder_category_values(self):
        preferred = ["All", "Custom", "Emotes", "Avatar", "Dance", "Chat", "Slash", "Keys", "Edge Extras", "Bedican"]
        found = []
        for action in gather_builder_actions(self.app.cfg):
            tab = str(action.get("tab", "") or "Other")
            if tab not in found:
                found.append(tab)
        values = []
        for name in preferred:
            if name == "All" or name in found:
                values.append(name)
        for name in found:
            if name not in values:
                values.append(name)
        return values

    def toggle_builder_category(self, name):
        if name in self.builder_collapsed_categories:
            self.builder_collapsed_categories.remove(name)
        else:
            self.builder_collapsed_categories.add(name)
        self.render_builder_actions()

    def render_builder_actions(self):
        for child in self.builder_action_inner.winfo_children():
            child.destroy()
        if hasattr(self, "builder_category_combo"):
            values = self.builder_category_values()
            self.builder_category_combo["values"] = values
            if self.builder_category_var.get() not in values:
                self.builder_category_var.set("All")
        q = self.builder_search_var.get().strip().lower()
        category = self.builder_category_var.get().strip() if hasattr(self, "builder_category_var") else "All"
        actions = gather_builder_actions(self.app.cfg)
        if category and category != "All":
            actions = [a for a in actions if str(a.get("tab", "")) == category]
        if q:
            actions = [a for a in actions if q in (a["label"] + " " + a["command"] + " " + a["tab"]).lower()]

        last_tab = None
        for action in actions:
            tab_name = str(action.get("tab", "Other"))
            if category == "All" and tab_name != last_tab:
                collapsed = tab_name in self.builder_collapsed_categories
                header = tk.Label(
                    self.builder_action_inner,
                    text=("▸ " if collapsed else "▾ ") + tab_name,
                    bg="#d8fbff",
                    fg="#00343b",
                    font=("Arial", 8, "bold"),
                    anchor="w",
                    padx=5,
                    cursor="hand2"
                )
                header.pack(fill="x", padx=3, pady=(6, 2))
                header.bind("<Button-1>", lambda e, name=tab_name: self.toggle_builder_category(name))
                last_tab = tab_name
            if category == "All" and tab_name in self.builder_collapsed_categories:
                continue
            label = f"{action['label']}"
            btn = AquaButton(self.builder_action_inner, label, command=lambda a=action: self.builder_add_command(a["label"], a["command"]), height=25, width=190, font=("Arial", 7, "bold"))
            btn.pack(fill="x", padx=3, pady=2)

    def builder_add_command(self, label, command):
        self.builder_items.append({"type": "command", "label": label, "value": command})
        self.sync_builder_to_script()
        self.render_bubbles()
        self.app.status.configure(text=f"Added: {command}")

    def builder_add_delay(self, ms):
        self.builder_items.append({"type": "delay", "label": f"Delay {ms}ms", "value": ms})
        self.sync_builder_to_script()
        self.render_bubbles()
        self.app.status.configure(text=f"Added delay: {ms}ms")

    def builder_add_custom_step(self):
        text = self.builder_custom_var.get().strip() if hasattr(self, "builder_custom_var") else ""
        if not text:
            return
        self.builder_items.append({"type": "command", "label": text, "value": text})
        self.builder_custom_var.set("")
        self.sync_builder_to_script()
        self.render_bubbles()
        self.app.status.configure(text=f"Added custom step: {text}")

    def builder_clear(self):
        self.builder_items = []
        self.sync_builder_to_script()
        self.render_bubbles()

    def builder_delete(self, index):
        if 0 <= index < len(self.builder_items):
            del self.builder_items[index]
        self.sync_builder_to_script()
        self.render_bubbles()

    def start_bubble_drag(self, index, label_text, color, event):
        if not (0 <= index < len(self.builder_items)):
            return "break"
        self.drag_index = index
        self.drop_index = index
        self.drag_payload = self.builder_items[index]
        if self.drag_ghost is not None:
            try:
                self.drag_ghost.destroy()
            except Exception:
                pass
        self.drag_ghost = tk.Toplevel(self.builder_popup)
        self.drag_ghost.overrideredirect(True)
        self.drag_ghost.attributes("-topmost", True)
        try:
            self.drag_ghost.attributes("-alpha", 0.84)
        except Exception:
            pass
        tk.Label(self.drag_ghost, text="☰  " + label_text, bg=color, fg="#00343b", bd=1, relief="solid", padx=10, pady=5, font=("Arial", 8, "bold")).pack()
        self.drag_ghost.geometry(f"+{event.x_root + 12}+{event.y_root + 12}")
        self.render_bubbles()
        self.builder_popup.bind_all("<B1-Motion>", self.drag_bubble_motion, add="+")
        self.builder_popup.bind_all("<ButtonRelease-1>", self.end_bubble_drag, add="+")
        return "break"

    def drag_bubble_motion(self, event):
        if self.drag_index is None:
            return "break"
        if self.drag_ghost is not None:
            try:
                self.drag_ghost.geometry(f"+{event.x_root + 14}+{event.y_root + 14}")
            except Exception:
                pass
        new_index = self.index_for_pointer_y(event.y_root)
        if new_index != self.drop_index and 0 <= new_index < len(self.builder_items):
            item = self.builder_items.pop(self.drop_index)
            self.builder_items.insert(new_index, item)
            self.drop_index = new_index
            self.drag_index = new_index
            self.sync_builder_to_script()
            self.render_bubbles()
        return "break"

    def index_for_pointer_y(self, y_root):
        rows = [child for child in self.bubble_inner.winfo_children() if getattr(child, "_bubble_row", False)]
        if not rows:
            return 0
        target = len(self.builder_items) - 1
        for i, row in enumerate(rows):
            try:
                midpoint = row.winfo_rooty() + row.winfo_height() / 2
            except Exception:
                continue
            if y_root < midpoint:
                target = i
                break
        return max(0, min(target, len(self.builder_items) - 1))

    def end_bubble_drag(self, event=None):
        self.drag_index = None
        self.drop_index = None
        self.drag_payload = None
        try:
            self.builder_popup.unbind_all("<B1-Motion>")
            self.builder_popup.unbind_all("<ButtonRelease-1>")
        except Exception:
            pass
        if self.drag_ghost is not None:
            try:
                self.drag_ghost.destroy()
            except Exception:
                pass
            self.drag_ghost = None
        self.sync_builder_to_script()
        self.render_bubbles()
        return "break"

    def render_gap_row(self, parent):
        gap = tk.Frame(parent, bg="#ffffff")
        gap._bubble_row = True
        gap.pack(fill="x", padx=4, pady=4)
        inner = tk.Frame(gap, bg="#f8ffff", bd=2, relief="groove", height=32)
        inner.pack(fill="x")
        inner.pack_propagate(False)
        tk.Label(inner, text="Drop here", bg="#f8ffff", fg="#397b8c", font=("Arial", 8, "bold")).pack(expand=True)

    def render_bubbles(self):
        for child in self.bubble_inner.winfo_children():
            child.destroy()
        if not self.builder_items:
            tk.Label(self.bubble_inner, text="Click action buttons to build a dance.", bg="#ffffff", fg="#666666", font=("Arial", 8)).pack(padx=5, pady=8)
            return
        for idx, item in enumerate(self.builder_items):
            if self.drag_index is not None and idx == self.drop_index:
                self.render_gap_row(self.bubble_inner)
                continue
            row = tk.Frame(self.bubble_inner, bg="#ffffff")
            row._bubble_row = True
            row.pack(fill="x", padx=4, pady=3)
            bubble_color = "#fff4bd" if item["type"] == "delay" else "#a9f4ff"
            text = item["label"] if item["type"] == "delay" else f"{item['label']}  {item['value']}"
            lab = tk.Label(row, text="☰  " + text, bg=bubble_color, fg="#00343b", bd=1, relief="solid", anchor="w", font=("Arial", 8, "bold"), padx=6, pady=4, cursor="fleur")
            lab.pack(side="left", fill="x", expand=True)
            lab.bind("<ButtonPress-1>", lambda e, i=idx, t=text, c=bubble_color: self.start_bubble_drag(i, t, c, e))
            tk.Button(row, text="x", width=2, command=lambda i=idx: self.builder_delete(i), bg="#ffd8d8", relief="ridge", bd=1).pack(side="left")

    def builder_generate_script(self):
        self.sync_builder_to_script()
        self.auto_save_current(refresh=False)
        self.hide_builder()

    def builder_load_from_script(self):
        self.builder_items = []
        for raw in normalize_dance_script_text(self.script_text.get("1.0", "end-1c")).splitlines():
            line = raw.strip()
            if not line:
                continue
            if line.lower().startswith("%delay") or line.lower().startswith("delay ") or line.lower().startswith("/delay "):
                ms = parse_delay_ms(line)
                self.builder_items.append({"type": "delay", "label": f"Delay {ms}ms", "value": ms})
            else:
                self.builder_items.append({"type": "command", "label": line, "value": line})
        self.render_bubbles()

    def clean_follow_name(self, name):
        return " ".join(str(name or "").strip().split())

    def get_follow_names(self):
        opts = self.app.cfg.setdefault("giggles_options", {})
        names = opts.setdefault("follow_avatar_names", [])
        if not isinstance(names, list):
            names = []
        cleaned = []
        seen = set()
        for raw in names:
            name = self.clean_follow_name(raw)
            if not name:
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(name)
        opts["follow_avatar_names"] = cleaned
        return cleaned

    def save_follow_names(self, names):
        opts = self.app.cfg.setdefault("giggles_options", {})
        cleaned = []
        seen = set()
        for raw in names:
            name = self.clean_follow_name(raw)
            if not name:
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(name)
        opts["follow_avatar_names"] = cleaned
        save_config(self.app.cfg)
        return cleaned

    def refresh_follow_names_list(self, select_name=None):
        if not hasattr(self, "follow_names_listbox"):
            return
        select_name = self.clean_follow_name(select_name)
        self.follow_names_listbox.delete(0, "end")
        names = self.get_follow_names()
        select_index = None
        for i, name in enumerate(names):
            self.follow_names_listbox.insert("end", name)
            if select_name and name.lower() == select_name.lower():
                select_index = i
        if select_index is not None:
            self.follow_names_listbox.selection_clear(0, "end")
            self.follow_names_listbox.selection_set(select_index)
            self.follow_names_listbox.see(select_index)

    def save_follow_avatar_name(self):
        name = ""
        try:
            name = self.clean_follow_name(self.follow_avatar_var.get())
            self.follow_avatar_var.set(name)
        except Exception:
            pass
        self.app.cfg.setdefault("giggles_options", {})["follow_avatar_name"] = name
        save_config(self.app.cfg)
        return name

    def use_selected_follow_name(self):
        try:
            sel = self.follow_names_listbox.curselection()
            if not sel:
                return
            name = self.follow_names_listbox.get(sel[0])
            self.follow_avatar_var.set(name)
            self.save_follow_avatar_name()
        except Exception:
            pass

    def add_follow_name(self):
        name = self.save_follow_avatar_name()
        if not name:
            messagebox.showinfo(APP_NAME, "Type an avatar name first, then click Add Name.", parent=self.app.root)
            try:
                self.follow_avatar_entry.focus_set()
            except Exception:
                pass
            return

        names = self.get_follow_names()
        if all(existing.lower() != name.lower() for existing in names):
            names.append(name)
            self.save_follow_names(names)
            self.app.status.configure(text=f"Saved follow name: {name}")
        else:
            self.app.status.configure(text=f"Follow name already saved: {name}")
        self.refresh_follow_names_list(select_name=name)

    def remove_follow_name(self):
        names = self.get_follow_names()
        remove_name = ""
        try:
            sel = self.follow_names_listbox.curselection()
            if sel:
                remove_name = self.follow_names_listbox.get(sel[0])
        except Exception:
            pass

        if not remove_name:
            remove_name = self.clean_follow_name(self.follow_avatar_var.get())

        if not remove_name:
            messagebox.showinfo(APP_NAME, "Select a saved name to remove.", parent=self.app.root)
            return

        new_names = [name for name in names if name.lower() != remove_name.lower()]
        if len(new_names) == len(names):
            self.app.status.configure(text=f"Name not in saved list: {remove_name}")
            return

        self.save_follow_names(new_names)
        self.refresh_follow_names_list()
        self.app.status.configure(text=f"Removed follow name: {remove_name}")

    def send_follow_moves(self):
        name = self.save_follow_avatar_name()
        if not name:
            messagebox.showinfo(APP_NAME, "Type an avatar name first.", parent=self.app.root)
            try:
                self.follow_avatar_entry.focus_set()
            except Exception:
                pass
            return
        command = f"/emote {name}"
        self.app.edit_var.set(command)
        self.app.send_text_to_game(command)
        self.app.status.configure(text=f"Following moves: {name}")

    def stop_follow_moves(self):
        command = "/emote stop"
        self.app.edit_var.set(command)
        self.app.send_text_to_game(command)
        self.app.status.configure(text="Sent /emote stop.")

    def save_options(self):
        self.app.cfg["dance_hotkeys_enabled"] = bool(self.hotkeys_enabled.get())
        self.app.cfg["dance_loop_default"] = bool(self.loop_var.get())
        self.app.cfg["hide_dance_text"] = bool(self.hide_dance_text_var.get())
        giggles = dict(self.app.cfg.get("giggles_options", {}))
        giggles.update({
            "page_up_sleep": bool(self.page_sleep.get()),
            "camera_functions": bool(self.camera_functions.get()),
            "performers_mode": bool(self.performers_mode.get()),
            "follow_avatar_name": self.clean_follow_name(getattr(self, "follow_avatar_var", tk.StringVar(value="")).get()),
            "follow_avatar_names": self.get_follow_names(),
        })
        self.app.cfg["giggles_options"] = giggles
        save_config(self.app.cfg)
        self.apply_builder_window_options()
        self.app.restart_hotkeys()
        self.app.status.configure(text="Saved Options.")


class CustomButtonEditor(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#ffffff", bd=1, relief="solid")
        self.app = app
        self.selected_index = None
        self.label_var = tk.StringVar(value="")
        self.command_var = tk.StringVar(value="")
        self.needs_text_var = tk.BooleanVar(value=False)
        self.placeholder_var = tk.StringVar(value="Text")
        self.target_var = tk.StringVar(value="Custom")
        self.build()

    def buttons(self):
        return self.app.cfg.setdefault("custom_buttons", [])

    def build(self):
        header = tk.Frame(self, bg="#d8fbff")
        header.pack(fill="x")
        tk.Label(header, text="Custom Buttons", bg="#d8fbff", fg="#00343b", font=("Arial", 9, "bold")).pack(side="left", padx=6, pady=4)
        tk.Label(header, text="Make your own buttons", bg="#d8fbff", fg="#004552", font=("Arial", 8)).pack(side="left", padx=6)

        body = tk.Frame(self, bg="#ffffff")
        body.pack(fill="both", expand=True, padx=5, pady=5)
        body.columnconfigure(0, weight=1, minsize=150)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        left = tk.Frame(body, bg="#ffffff")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(left, bg="#ffffff", fg="#000000", relief="sunken", bd=1, exportselection=False, font=("Arial", 8))
        self.list_scroll = tk.Scrollbar(left, orient="vertical", command=self.listbox.yview, width=14)
        self.listbox.configure(yscrollcommand=self.list_scroll.set)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        self.list_scroll.grid(row=0, column=1, sticky="ns")
        self.listbox.bind("<<ListboxSelect>>", lambda e: self.load_selected())

        lbtn = tk.Frame(left, bg="#ffffff")
        lbtn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        AquaButton(lbtn, "New", command=self.new_button, height=24, width=60).pack(side="left", fill="x", expand=True, padx=(0, 3))
        AquaButton(lbtn, "Delete", command=self.delete_button, height=24, width=70).pack(side="left", fill="x", expand=True)

        right = tk.Frame(body, bg="#ffffff")
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(1, weight=1)

        tk.Label(right, text="Button Label", bg="#ffffff", fg="#00343b", font=("Arial", 8, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 4))
        tk.Entry(right, textvariable=self.label_var, bg="#ffffff", relief="sunken", bd=1, font=("Arial", 9)).grid(row=0, column=1, sticky="ew", pady=(0, 4))

        tk.Label(right, text="Command", bg="#ffffff", fg="#00343b", font=("Arial", 8, "bold")).grid(row=1, column=0, sticky="w", pady=(0, 4))
        tk.Entry(right, textvariable=self.command_var, bg="#ffffff", relief="sunken", bd=1, font=("Arial", 9)).grid(row=1, column=1, sticky="ew", pady=(0, 4))

        cb = tk.Checkbutton(right, text="Needs typed text first", variable=self.needs_text_var, bg="#ffffff", fg="#00343b")
        cb.grid(row=2, column=0, columnspan=2, sticky="w")
        ToolTip(cb, "Use this for commands like /friend or /shout where you need to type a name or message before sending.")

        tk.Label(right, text="Placeholder", bg="#ffffff", fg="#00343b", font=("Arial", 8, "bold")).grid(row=3, column=0, sticky="w", pady=(4, 4))
        tk.Entry(right, textvariable=self.placeholder_var, bg="#ffffff", relief="sunken", bd=1, font=("Arial", 9)).grid(row=3, column=1, sticky="ew", pady=(4, 4))

        tk.Label(right, text="Save to List", bg="#ffffff", fg="#00343b", font=("Arial", 8, "bold")).grid(row=4, column=0, sticky="w", pady=(4, 4))
        self.target_combo = ttk.Combobox(
            right,
            state="readonly",
            textvariable=self.target_var,
            values=[label for _, label in CUSTOM_TARGETS],
            width=14
        )
        self.target_combo.grid(row=4, column=1, sticky="w", pady=(4, 4))
        ToolTip(self.target_combo, "Choose where this custom button appears. Custom keeps it in the Custom editor; choosing Emotes/Dance/etc adds it to that list.")

        tk.Label(right, text="Examples: 'wave   /sit   /shout   hello everyone", bg="#ffffff", fg="#004552", font=("Arial", 8), anchor="w").grid(row=5, column=0, columnspan=2, sticky="ew", pady=(3, 7))

        btns = tk.Frame(right, bg="#ffffff")
        btns.grid(row=6, column=0, columnspan=2, sticky="ew")
        AquaButton(btns, "Save Button", command=self.save_button, height=26, width=110).pack(side="left", fill="x", expand=True, padx=(0, 3))
        AquaButton(btns, "Test Send", command=self.test_button, height=26, width=90).pack(side="left", fill="x", expand=True)

        self.refresh()

    def refresh(self):
        old = self.selected_index
        self.listbox.delete(0, "end")
        for item in self.buttons():
            self.listbox.insert("end", str(item.get("label", "Custom")))
        if self.listbox.size() > 0:
            idx = old if old is not None and 0 <= old < self.listbox.size() else 0
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(idx)
            self.selected_index = idx
            self.load_selected()

    def load_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        self.selected_index = int(sel[0])
        item = self.buttons()[self.selected_index]
        self.label_var.set(str(item.get("label", "")))
        self.command_var.set(str(item.get("command", "")))
        self.needs_text_var.set(bool(item.get("needs_text", False)))
        self.placeholder_var.set(str(item.get("placeholder", "Text")))
        self.target_var.set(custom_target_id_to_label(str(item.get("target_tab", "custom"))))

    def new_button(self):
        self.buttons().append({"label": "New Button", "command": "'wave", "target_tab": "custom"})
        self.selected_index = len(self.buttons()) - 1
        save_config(self.app.cfg)
        self.refresh()
        self.app.status.configure(text="New custom button added.")

    def delete_button(self):
        if self.selected_index is None:
            return
        if 0 <= self.selected_index < len(self.buttons()):
            del self.buttons()[self.selected_index]
        self.selected_index = 0
        save_config(self.app.cfg)
        self.refresh()
        self.app.status.configure(text="Custom button deleted.")

    def save_button(self):
        label = self.label_var.get().strip() or "Custom"
        command = self.command_var.get().strip()
        if not command:
            messagebox.showinfo(APP_NAME, "Type a command first.")
            return
        item = {
            "label": label,
            "command": command,
            "needs_text": bool(self.needs_text_var.get()),
            "placeholder": self.placeholder_var.get().strip() or "Text",
            "target_tab": custom_target_label_to_id(self.target_var.get())
        }
        if self.selected_index is None or not (0 <= self.selected_index < len(self.buttons())):
            self.buttons().append(item)
            self.selected_index = len(self.buttons()) - 1
        else:
            self.buttons()[self.selected_index] = item
        save_config(self.app.cfg)
        self.refresh()
        self.app.render_tabs()
        self.app.status.configure(text=f"Saved custom button: {label}")

    def test_button(self):
        command = self.command_var.get().strip()
        if not command:
            return
        item = {
            "label": self.label_var.get().strip() or "Custom",
            "command": command,
            "needs_text": bool(self.needs_text_var.get()),
            "placeholder": self.placeholder_var.get().strip() or "Text",
            "target_tab": custom_target_label_to_id(self.target_var.get())
        }
        self.app.command_clicked(item)


class ThereOverlayApp:
    def __init__(self):
        self.cfg = load_config()
        save_config(self.cfg)  # V2.0 cleanup removed old bundled sample dances
        self.target_hwnd = None
        self.target_title = ""
        self.window_map = {}
        self.active_tab_index = 0
        self.minibar = False
        self.dance_editor = None
        self.active_hotkey_key = None
        self.hotkey_queue = queue.Queue()
        self.status_queue = queue.Queue()
        self.send_lock = threading.Lock()
        self.dance_player = DancePlayer(self)
        self.hotkey_manager = GlobalHotkeyManager(self)

        self.root = tk.Tk()
        self.root._there_app = self
        self.asset_images = {}
        self.settings_window = None
        self.custom_editor = None
        self.tutorial_overlay = None
        self.tray_icon = None
        self.tray_thread = None
        self._closing = False
        self.root.title(APP_NAME)
        self.root.geometry("650x700+80+90")
        self.full_min_w = 610
        self.full_min_h = 640
        self.mini_min_w = 220
        self.mini_h = 34
        self.saved_full_geometry = "650x700+80+90"
        self.root.minsize(self.full_min_w, self.full_min_h)
        self.root.configure(bg="#020202")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", bool(self.cfg.get("always_on_top", True)))
        self.root.attributes("-alpha", float(self.cfg.get("opacity", 0.92)))

        try:
            self.root.attributes("-transparentcolor", "#020202")
        except tk.TclError:
            pass

        self.load_assets()
        self.build_ui()
        self.refresh_windows()
        self.try_auto_lock()
        self.hotkey_manager.start()
        self.root.after(80, self.poll_queues)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.setup_tray_icon()
        self.root.after(900, lambda: self.start_tutorial(force=False) if bool(self.cfg.get("show_tutorial_on_start", True)) else None)

    def load_assets(self):
        self.asset_images = {}
        try:
            logo = tk.PhotoImage(file=resource_path("TQA.png"))
            self.asset_images["tqa"] = logo
            self.asset_images["tqa_small"] = logo.subsample(24, 24)
            self.root.iconphoto(True, logo)
        except Exception:
            pass
        try:
            kofi = tk.PhotoImage(file=resource_path("kofi.png"))
            # 512px source -> about 24px.
            self.asset_images["kofi"] = kofi.subsample(21, 21)
        except Exception:
            pass

    def open_url(self, url):
        try:
            webbrowser.open(str(url))
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Could not open link:\n{exc}")

    def build_ui(self):
        self.shell = tk.Frame(self.root, bg="#a5dbe4", bd=1, relief="solid")
        self.shell.pack(fill="both", expand=True, padx=4, pady=4)

        self.titlebar = tk.Frame(self.shell, bg="#9be9f7", height=25)
        self.titlebar.pack(fill="x")
        self.titlebar.pack_propagate(False)

        if "tqa_small" in self.asset_images:
            logo_label = tk.Label(self.titlebar, image=self.asset_images["tqa_small"], bg="#9be9f7")
            logo_label.pack(side="left", padx=(3, 2), pady=2)
            logo_label.bind("<ButtonPress-1>", self.start_move)
            logo_label.bind("<B1-Motion>", self.do_move)

        self.title_label = tk.Label(
            self.titlebar,
            text=" ThereQuickActions",
            bg="#9be9f7",
            fg="#002a32",
            font=("Arial", 9, "bold"),
            anchor="w"
        )
        self.title_label.pack(side="left", fill="both", expand=True)

        self.btn_help = tk.Button(self.titlebar, text="?", command=lambda: self.start_tutorial(force=True), width=2, bg="#d8ffff", fg="#00434c", relief="ridge", bd=1, font=("Arial", 8, "bold"))
        self.btn_help.pack(side="left", padx=(1, 1), pady=2)

        self.btn_min = tk.Button(self.titlebar, text="—", command=self.toggle_minibar, width=2, bg="#d8ffff", fg="#00434c", relief="ridge", bd=1, font=("Arial", 8, "bold"))
        self.btn_min.pack(side="left", padx=(1, 1), pady=2)

        self.btn_close = tk.Button(self.titlebar, text="×", command=self.on_close, width=2, bg="#d8ffff", fg="#00434c", relief="ridge", bd=1, font=("Arial", 8, "bold"))
        self.btn_close.pack(side="left", padx=(1, 3), pady=2)

        for widget in [self.titlebar, self.title_label]:
            widget.bind("<ButtonPress-1>", self.start_move)
            widget.bind("<B1-Motion>", self.do_move)
            widget.bind("<Double-Button-1>", lambda e: self.toggle_minibar())

        self.body = tk.Frame(self.shell, bg="#c7f3fb")
        self.body.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        self.body.columnconfigure(0, weight=1)
        self.body.rowconfigure(1, weight=1)

        self.setup = tk.Frame(self.body, bg="#c7f3fb")
        self.setup.grid(row=0, column=0, sticky="ew", pady=(4, 3))

        self.admin_warning_label = tk.Label(
            self.setup,
            text="RESTART PROGRAM IN ADMIN MODE",
            bg="#a80000",
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            pady=4
        )
        if bool(self.cfg.get("show_admin_warning", True)) and not is_running_as_admin():
            self.admin_warning_label.pack(fill="x", pady=(0, 4))

        selector_row = tk.Frame(self.setup, bg="#c7f3fb")
        selector_row.pack(fill="x")

        self.style_ttk()
        self.window_combo = ttk.Combobox(selector_row, state="readonly", width=20)
        self.window_combo.pack(side="left", fill="x", expand=True, padx=(0, 3))

        AquaButton(selector_row, "↻", command=self.refresh_windows, height=24, width=34).pack(side="left", padx=(0, 3))

        lock_row = tk.Frame(self.setup, bg="#c7f3fb")
        lock_row.pack(fill="x", pady=(4, 0))
        self.lock_selected_big_button = AquaButton(lock_row, "LOCK SELECTED WINDOW", command=self.lock_selected, height=26, width=220)
        self.lock_selected_big_button.pack(fill="x")

        options_row = tk.Frame(self.setup, bg="#c7f3fb")
        options_row.pack(fill="x", pady=(4, 0))

        tk.Label(options_row, text="Chat", bg="#c7f3fb", fg="#00343b", font=("Arial", 8)).pack(side="left")
        self.chat_key_var = tk.StringVar(value=self.cfg.get("chat_key", "Enter"))
        self.chat_key_combo = ttk.Combobox(options_row, state="readonly", values=list(VK_CODES.keys()), width=7, textvariable=self.chat_key_var)
        self.chat_key_combo.pack(side="left", padx=(3, 6))
        self.chat_key_combo.bind("<<ComboboxSelected>>", self.setting_changed)

        tk.Label(options_row, text="Input", bg="#c7f3fb", fg="#00343b", font=("Arial", 8)).pack(side="left")
        self.input_mode_var = tk.StringVar(value=self.cfg.get("input_mode", "ScanCode"))
        self.input_mode_combo = ttk.Combobox(options_row, state="readonly", values=INPUT_MODES, width=12, textvariable=self.input_mode_var)
        self.input_mode_combo.pack(side="left", padx=(3, 0))
        self.input_mode_combo.bind("<<ComboboxSelected>>", self.setting_changed)

        self.status = tk.Label(self.setup, text="Pick There/game window, then Lock.", bg="#c7f3fb", fg="#004552", font=("Arial", 8), anchor="w")
        self.status.pack(fill="x", pady=(3, 0))

        mid = tk.Frame(self.body, bg="#c7f3fb")
        mid.grid(row=1, column=0, sticky="nsew", pady=(2, 3))
        mid.rowconfigure(0, weight=1)
        mid.columnconfigure(1, weight=1)

        self.tab_bar_outer = tk.Frame(mid, bg="#dffbff", bd=1, relief="solid", width=82)
        self.tab_bar_outer.grid(row=0, column=0, sticky="nsw", padx=(0, 5))
        self.tab_bar_outer.grid_propagate(False)

        # Fixed settings area: this does NOT scroll with the tab list.
        self.tab_settings_holder = tk.Frame(self.tab_bar_outer, bg="#dffbff")
        self.tab_settings_holder.pack(side="bottom", fill="x", padx=4, pady=(4, 6))
        self.settings_tab_button = AquaButton(self.tab_settings_holder, "⚙", command=self.open_settings, height=34, width=46, font=("Arial", 14, "bold"))
        self.settings_tab_button.pack(fill="x")
        ToolTip(self.settings_tab_button, "Settings: opacity, tooltips, always-on-top, visible tabs, and reset size.")

        self.tab_scroll_area = tk.Frame(self.tab_bar_outer, bg="#dffbff")
        self.tab_scroll_area.pack(side="top", fill="both", expand=True)

        self.tab_canvas = tk.Canvas(self.tab_scroll_area, bg="#dffbff", highlightthickness=0, width=58)
        self.tab_scroll = tk.Scrollbar(self.tab_scroll_area, orient="vertical", command=self.tab_canvas.yview, width=14)
        self.tab_bar = tk.Frame(self.tab_canvas, bg="#dffbff")
        self.tab_bar_id = self.tab_canvas.create_window((0, 0), window=self.tab_bar, anchor="nw")
        self.tab_canvas.configure(yscrollcommand=self.tab_scroll.set)
        self.tab_canvas.pack(side="left", fill="both", expand=True)
        self.tab_scroll.pack(side="right", fill="y")
        self.tab_bar.bind("<Configure>", lambda e: self.tab_canvas.configure(scrollregion=self.tab_canvas.bbox("all")))
        self.tab_canvas.bind("<Configure>", lambda e: self.tab_canvas.itemconfigure(self.tab_bar_id, width=e.width))
        self.tab_canvas.bind("<MouseWheel>", lambda e: self.tab_canvas.yview_scroll((-1 if e.delta > 0 else 1) * 3, "units"))
        self.tab_bar.bind("<MouseWheel>", lambda e: self.tab_canvas.yview_scroll((-1 if e.delta > 0 else 1) * 3, "units"))
        self.tab_scroll_area.bind("<MouseWheel>", lambda e: self.tab_canvas.yview_scroll((-1 if e.delta > 0 else 1) * 3, "units"))

        self.content_shell = tk.Frame(mid, bg="#ffffff", bd=1, relief="solid")
        self.content_shell.grid(row=0, column=1, sticky="nsew")

        self.tab_title = tk.Label(self.content_shell, text="Emotes", bg="#9be9f7", fg="#00343b", font=("Arial", 9, "bold"))
        self.tab_title.pack(fill="x")

        self.search_row = tk.Frame(self.content_shell, bg="#d8fbff")
        self.search_row.pack(fill="x")

        tk.Label(self.search_row, text="Search", bg="#d8fbff", fg="#004552", font=("Arial", 8)).pack(side="left", padx=(5, 3))
        self.search_var = tk.StringVar(value="")
        self.search_entry = tk.Entry(self.search_row, textvariable=self.search_var, bg="#ffffff", fg="#000000", relief="sunken", bd=1, font=("Arial", 8))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 4), pady=3)
        self.search_entry.bind("<KeyRelease>", lambda e: self.render_active_tab())

        self.command_panel = ScrollableCommandPanel(self.content_shell, self)
        self.command_panel.pack(fill="both", expand=True, padx=5, pady=(4, 5))

        self.bottom = tk.Frame(self.body, bg="#c7f3fb")
        self.bottom.grid(row=2, column=0, sticky="ew", pady=(1, 0))

        tk.Label(self.bottom, text="Edit/Send:", bg="#c7f3fb", fg="#00343b", font=("Arial", 8, "bold"), anchor="w").pack(fill="x")

        edit_row = tk.Frame(self.bottom, bg="#c7f3fb", height=32)
        edit_row.pack(fill="x")
        edit_row.pack_propagate(True)

        self.edit_var = tk.StringVar(value="")
        self.edit_box = tk.Entry(edit_row, textvariable=self.edit_var, bg="#ffffff", fg="#000000", relief="sunken", bd=1, font=("Arial", 9))
        self.edit_box.pack(side="left", fill="x", expand=True, padx=(0, 4), ipady=2)
        self.edit_box.bind("<Return>", lambda e: self.send_edit_box())

        AquaButton(edit_row, "Send", command=self.send_edit_box, height=27, width=70).pack(side="left")

        bottom_buttons = tk.Frame(self.body, bg="#c7f3fb")
        bottom_buttons.grid(row=3, column=0, sticky="ew", pady=(4, 0))

        AquaButton(bottom_buttons, "Save", command=self.save_config_now, height=25, width=70).pack(side="left", fill="x", expand=True, padx=(0, 3))
        AquaButton(bottom_buttons, "Reload", command=self.reload_config, height=25, width=80).pack(side="left", fill="x", expand=True, padx=(0, 3))

        footer = tk.Frame(self.body, bg="#c7f3fb")
        footer.grid(row=4, column=0, sticky="ew", pady=(2, 0))
        if "kofi" in self.asset_images:
            kofi_label = tk.Label(footer, image=self.asset_images["kofi"], bg="#c7f3fb", cursor="hand2")
            # Leave room for the bottom-right resize grip so the icon does not clip.
            kofi_label.pack(side="right", padx=(4, 22))
            kofi_label.bind("<Button-1>", lambda e: self.open_url("https://buymeacoffee.com/landminegirl"))
            ToolTip(kofi_label, "Support LandmineGirl on Ko-fi / Buy Me a Coffee.")
        credit = tk.Label(footer, text="V1.0  Auth: LandmineGirl", bg="#c7f3fb", fg="#004552", font=("Arial", 8, "bold"), cursor="hand2")
        credit.pack(side="right")
        credit.bind("<Button-1>", lambda e: self.open_url("https://github.com/Landminegirl"))
        ToolTip(credit, "Open LandmineGirl on GitHub.")

        self.resize_grip = tk.Label(self.shell, text="◢", bg="#c7f3fb", fg="#326b75", cursor="size_nw_se", font=("Arial", 10))
        self.resize_grip.place(relx=1.0, rely=1.0, x=-2, y=-2, anchor="se")
        self.resize_grip.bind("<ButtonPress-1>", self.start_resize)
        self.resize_grip.bind("<B1-Motion>", self.do_resize)

        self.render_tabs()
        self.render_active_tab()

    def style_ttk(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TCombobox", fieldbackground="#ffffff", background="#9be9f7", foreground="#00343b", padding=1)

    def start_move(self, event):
        self._move_dx = event.x_root - self.root.winfo_x()
        self._move_dy = event.y_root - self.root.winfo_y()

    def do_move(self, event):
        self.root.geometry(f"+{event.x_root - self._move_dx}+{event.y_root - self._move_dy}")

    def start_resize(self, event):
        self._resize_w = self.root.winfo_width()
        self._resize_h = self.root.winfo_height()
        self._resize_x = event.x_root
        self._resize_y = event.y_root

    def do_resize(self, event):
        min_w = self.mini_min_w if self.minibar else self.full_min_w
        min_h = self.mini_h if self.minibar else self.full_min_h
        new_w = max(min_w, self._resize_w + (event.x_root - self._resize_x))
        new_h = max(min_h, self._resize_h + (event.y_root - self._resize_y))
        self.root.geometry(f"{new_w}x{new_h}")

    def get_visible_tabs(self):
        reorder_tabs_in_config(self.cfg)
        hidden = set(self.cfg.get("hidden_tabs", []))

        # Backward compatibility with older two-toggle settings.
        if not bool(self.cfg.get("show_edge_extras", True)):
            hidden.add("edgeextras")
        if not bool(self.cfg.get("show_bedican_compass", True)):
            hidden.add("bedican")

        visible = []
        for tab in self.cfg.get("tabs", []):
            tab_id = tab.get("id")
            if tab_id in hidden:
                continue
            visible.append(tab)
        return visible

    def render_tabs(self):
        for child in self.tab_bar.winfo_children():
            child.destroy()

        self.visible_tabs = self.get_visible_tabs()
        self.active_tab_index = max(0, min(self.active_tab_index, max(0, len(self.visible_tabs) - 1)))

        for idx, tab in enumerate(self.visible_tabs):
            selected = idx == self.active_tab_index
            btn = tk.Canvas(self.tab_bar, width=42, height=45, bg="#dffbff", highlightthickness=0, cursor="hand2")
            btn.pack(side="top", pady=4, padx=4)

            draw_round_rect(btn, 2, 2, 40, 42, 8, "#9be9f7" if selected else "#e7fdff", "#397b8c", 1)
            label = str(tab.get("label", ""))
            btn.create_text(21, 14, text=str(tab.get("icon", "?")), font=("Arial", 13, "bold"), fill="#00343b")
            if label == "Auto Dance":
                btn.create_text(21, 29, text="Auto", font=("Arial", 6, "bold"), fill="#00343b")
                btn.create_text(21, 38, text="Dance", font=("Arial", 6, "bold"), fill="#00343b")
            elif label == "Edge Extras":
                btn.create_text(21, 29, text="Edge", font=("Arial", 6, "bold"), fill="#00343b")
                btn.create_text(21, 38, text="Extras", font=("Arial", 6, "bold"), fill="#00343b")
            elif label == "Bedican":
                btn.create_text(21, 34, text="Bedican", font=("Arial", 6, "bold"), fill="#00343b")
            else:
                btn.create_text(21, 34, text=label[:6], font=("Arial", 6, "bold"), fill="#00343b")
            btn.bind("<Button-1>", lambda e, i=idx: self.select_tab(i))

        try:
            self.tab_canvas.configure(scrollregion=self.tab_canvas.bbox("all"))
        except Exception:
            pass

    def select_tab(self, idx):
        self.active_tab_index = idx
        self.render_tabs()
        self.render_active_tab()

    def render_active_tab(self):
        tabs = getattr(self, "visible_tabs", None) or self.get_visible_tabs()
        self.visible_tabs = tabs
        if not tabs:
            return

        self.active_tab_index = max(0, min(self.active_tab_index, len(tabs) - 1))
        tab = tabs[self.active_tab_index]
        self.tab_title.configure(text=f"{tab.get('icon', '')} {tab.get('label', 'Tab')}")

        if tab.get("id") in ("autodance", "sets"):
            try:
                self.search_row.pack_forget()
            except Exception:
                pass
            self.command_panel.pack_forget()
            if self.custom_editor is not None:
                self.custom_editor.pack_forget()
            if self.dance_editor is None:
                self.dance_editor = DanceListEditor(self.content_shell, self)
            self.dance_editor.pack(fill="both", expand=True, padx=5, pady=(4, 5))
            self.dance_editor.refresh_lists()
            return

        if tab.get("id") == "custom":
            try:
                self.search_row.pack_forget()
            except Exception:
                pass
            self.command_panel.pack_forget()
            if self.dance_editor is not None:
                self.dance_editor.pack_forget()
            if self.custom_editor is None:
                self.custom_editor = CustomButtonEditor(self.content_shell, self)
            self.custom_editor.pack(fill="both", expand=True, padx=5, pady=(4, 5))
            self.custom_editor.refresh()
            return

        try:
            self.search_row.pack_forget()
            self.search_row.pack(fill="x", before=self.command_panel)
        except Exception:
            try:
                self.search_row.pack(fill="x")
            except Exception:
                pass
        self.search_entry.configure(state="normal")

        if self.dance_editor is not None:
            self.dance_editor.pack_forget()
        if self.custom_editor is not None:
            self.custom_editor.pack_forget()

        self.command_panel.pack(fill="both", expand=True, padx=5, pady=(4, 5))

        query = self.search_var.get().strip().lower()
        commands = list(tab.get("commands", []))

        tab_id = tab.get("id")
        if tab_id not in ("custom", "autodance", "sets"):
            for custom_item in self.cfg.get("custom_buttons", []):
                if not isinstance(custom_item, dict):
                    continue
                if custom_item.get("target_tab", "custom") == tab_id:
                    commands.append(custom_item)

        if query:
            commands = [
                item for item in commands
                if query in " ".join([
                    str(item.get("label", "")),
                    str(item.get("command", "")),
                    str(item.get("description", "")),
                ]).lower()
            ]

        self.command_panel.set_commands(commands)

    def refresh_windows(self):
        selected = self.window_combo.get() if hasattr(self, "window_combo") else ""
        self.window_map.clear()

        labels = []
        for hwnd, title in list_windows(exclude_titles={APP_NAME, "ThereQuickActions"}):
            label = f"{title}  [{hwnd}]"
            self.window_map[label] = hwnd
            labels.append(label)

        self.window_combo["values"] = labels

        if selected in labels:
            self.window_combo.set(selected)
            return

        last = str(self.cfg.get("auto_lock_last_title", ""))
        for label in labels:
            if last and last.lower() in label.lower():
                self.window_combo.set(label)
                return

        if labels:
            self.window_combo.current(0)

    def try_auto_lock(self):
        last = str(self.cfg.get("auto_lock_last_title", ""))
        if not last:
            return

        for label, hwnd in self.window_map.items():
            if last.lower() in label.lower():
                self.target_hwnd = hwnd
                self.target_title = get_window_title(hwnd) or label
                self.status.configure(text=f"Auto-locked: {self.target_title}")
                return

    def lock_selected(self):
        label = self.window_combo.get()
        hwnd = self.window_map.get(label)

        if not hwnd:
            messagebox.showinfo(APP_NAME, "Pick a window from the list first.")
            return

        self.target_hwnd = hwnd
        self.target_title = get_window_title(hwnd) or label
        self.cfg["auto_lock_last_title"] = self.target_title
        save_config(self.cfg)
        self.status.configure(text=f"Locked: {self.target_title}")

    def setting_changed(self, *_):
        self.cfg["chat_key"] = self.chat_key_var.get()
        self.cfg["input_mode"] = self.input_mode_var.get()
        save_config(self.cfg)

    def save_config_now(self):
        self.setting_changed()
        self.apply_runtime_settings(save=True)
        messagebox.showinfo(APP_NAME, "Saved settings.")

    def reload_config(self):
        self.cfg = load_config()
        self.chat_key_var.set(self.cfg.get("chat_key", "Enter"))
        self.input_mode_var.set(self.cfg.get("input_mode", "ScanCode"))
        self.render_tabs()
        self.render_active_tab()
        self.restart_hotkeys()

    def toggle_minibar(self):
        if not self.minibar:
            self.saved_full_geometry = self.root.geometry()
            self.root.minsize(self.mini_min_w, self.mini_h)
            self.body.pack_forget()
            self.resize_grip.place_forget()
            self.minibar = True
            self.btn_min.configure(text="□")
            self.root.geometry(f"{max(self.mini_min_w, min(self.root.winfo_width(), 420))}x{self.mini_h}")
        else:
            self.root.minsize(self.full_min_w, self.full_min_h)
            self.body.pack(fill="both", expand=True, padx=5, pady=(0, 5))
            self.resize_grip.place(relx=1.0, rely=1.0, x=-2, y=-2, anchor="se")
            self.minibar = False
            self.btn_min.configure(text="—")
            self.root.geometry(self.saved_full_geometry or "520x680")

    def command_clicked(self, item):
        if "url" in item:
            self.open_url(item.get("url"))
            return

        if "hotkey" in item:
            self.send_hotkey(item.get("hotkey", []))
            return

        command = str(item.get("command", ""))
        if bool(item.get("needs_text", False)):
            if not command.endswith(" "):
                command += " "
            self.edit_var.set(command)
            self.edit_box.focus_set()
            self.edit_box.icursor("end")
            self.status.configure(text=f"Type {item.get('placeholder', 'text')}, then Send.")
            return

        command_to_send = maybe_hide_dance_text(command, bool(self.cfg.get("hide_button_emote_text", False)))
        self.edit_var.set(command_to_send)
        self.send_text_to_game(command_to_send)

    def send_edit_box(self):
        text = self.edit_var.get()
        if text.strip():
            text_to_send = maybe_hide_dance_text(text, bool(self.cfg.get("hide_button_emote_text", False)))
            self.send_text_to_game(text_to_send)

    def ensure_target(self):
        if not self.target_hwnd or not user32.IsWindow(self.target_hwnd):
            if threading.current_thread() is threading.main_thread():
                messagebox.showinfo(APP_NAME, "No valid game window locked. Pick it from the list and click Lock.")
            else:
                self.status_queue.put("No valid game window locked. Pick it from the list and click Lock.")
            return False
        return True

    def send_text_to_game(self, text, from_thread=False):
        if not bool(self.cfg.get("enabled", True)):
            if from_thread:
                self.status_queue.put("Actions are disabled. Enable from the tray icon.")
            else:
                self.status.configure(text="Actions are disabled. Enable from the tray icon.")
            return

        if not self.ensure_target():
            return

        with self.send_lock:
            try:
                mode = self.input_mode_var.get() or "ScanCode"
                focus_window(self.target_hwnd)
                time.sleep(int(self.cfg.get("focus_delay_ms", 150)) / 1000.0)

                chat_key = self.chat_key_var.get()
                vk = VK_CODES.get(chat_key, VK_CODES["Enter"])
                text_to_send = text

                if vk is not None:
                    press_vk(vk, "ScanCode" if mode == "ClipboardPaste" else mode)
                    time.sleep(int(self.cfg.get("submit_delay_ms", 90)) / 1000.0)

                    if chat_key == "Slash" and bool(self.cfg.get("slash_open_inserts_slash", True)) and text_to_send.startswith("/"):
                        text_to_send = text_to_send[1:]

                if mode == "Unicode":
                    send_unicode_text(text_to_send, int(self.cfg.get("type_delay_ms", 10)))
                elif mode == "ClipboardPaste":
                    paste_clipboard_text(text_to_send, "ScanCode")
                elif mode == "VirtualKey":
                    send_key_text(text_to_send, "VirtualKey", int(self.cfg.get("type_delay_ms", 10)))
                else:
                    send_key_text(text_to_send, "ScanCode", int(self.cfg.get("type_delay_ms", 10)))

                time.sleep(int(self.cfg.get("submit_delay_ms", 90)) / 1000.0)
                press_vk(VK_RETURN, "ScanCode" if mode == "ClipboardPaste" else mode)

                msg = f"Sent: {text[:45]}"
                if from_thread:
                    self.status_queue.put(msg)
                else:
                    self.status.configure(text=msg)

            except Exception as exc:
                if from_thread:
                    self.status_queue.put(f"Send error: {exc}")
                else:
                    messagebox.showerror(APP_NAME, str(exc))

    def send_hotkey(self, hotkey):
        if not self.ensure_target():
            return

        try:
            mode = self.input_mode_var.get() or "ScanCode"
            if mode in ("Unicode", "ClipboardPaste"):
                mode = "ScanCode"

            keys = []
            for key in hotkey:
                vk = HOTKEY_VK.get(str(key).lower())
                if vk:
                    keys.append(vk)

            if not keys:
                return

            focus_window(self.target_hwnd)
            time.sleep(int(self.cfg.get("focus_delay_ms", 150)) / 1000.0)

            for vk in keys:
                key_down(vk, mode)
                time.sleep(0.02)

            time.sleep(0.05)

            for vk in reversed(keys):
                key_up(vk, mode)
                time.sleep(0.02)

            self.status.configure(text="Sent hotkey.")
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def play_dance(self, name, script, loop=False):
        if not bool(self.cfg.get("enabled", True)):
            self.status.configure(text="Actions are disabled; Auto Dance not started.")
            return
        self.dance_player.play(name or "Untitled", script or "", loop=loop)

    def stop_dance(self):
        self.dance_player.stop()
        self.active_hotkey_key = None
        self.status.configure(text="Stopping dance list...")

    def play_hotkey_dance(self, key_name):
        if not bool(self.cfg.get("enabled", True)):
            self.status_queue.put("Actions are disabled; F-key ignored.")
            return

        dance_name = self.cfg.get("dance_hotkey_bindings", {}).get(key_name, "")
        if not dance_name:
            return

        loop_enabled = bool(self.cfg.get("dance_loop_default", False))

        # If a looping dance was started by this same F-key, tapping the same key stops it.
        if (
            loop_enabled
            and self.active_hotkey_key == key_name
            and self.dance_player.active
            and self.dance_player.current_loop
            and self.dance_player.current_name == dance_name
        ):
            self.stop_dance()
            self.status.configure(text=f"Stopped loop: {dance_name}")
            return

        for item in self.cfg.get("dance_lists", []):
            if item.get("name") == dance_name:
                self.active_hotkey_key = key_name
                self.play_dance(dance_name, item.get("script", ""), loop=loop_enabled)
                return

        self.status.configure(text=f"No dance set found for {key_name}.")

    def restart_hotkeys(self):
        try:
            self.hotkey_manager.restart()
        except Exception as exc:
            self.status.configure(text=f"Hotkey restart failed: {exc}")

    def poll_queues(self):
        while True:
            try:
                key_name = self.hotkey_queue.get_nowait()
            except queue.Empty:
                break
            if key_name == "__STOP_DANCE__":
                self.stop_dance()
            else:
                self.play_hotkey_dance(key_name)

        while True:
            try:
                msg = self.status_queue.get_nowait()
            except queue.Empty:
                break
            self.status.configure(text=msg)

        self.root.after(80, self.poll_queues)


    def show_popup_above_main(self, win):
        try:
            win.transient(self.root)
        except Exception:
            pass
        try:
            win.attributes("-topmost", bool(self.cfg.get("always_on_top", True)))
        except Exception:
            pass
        try:
            win.lift(self.root)
        except Exception:
            try:
                win.lift()
            except Exception:
                pass

    def open_settings(self):
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.lift()
            self.settings_window.focus_force()
            return

        win = tk.Toplevel(self.root)
        self.settings_window = win
        win._there_app = self
        win.title("ThereQuickActions Settings")
        win.configure(bg="#c7f3fb")
        win.attributes("-topmost", bool(self.cfg.get("always_on_top", True)))
        try:
            win.attributes("-alpha", float(self.cfg.get("opacity", 0.92)))
        except Exception:
            pass
        win.geometry(f"430x520+{self.root.winfo_rootx()+40}+{self.root.winfo_rooty()+40}")
        self.show_popup_above_main(win)
        win.minsize(390, 420)

        shell = tk.Frame(win, bg="#a5dbe4", bd=1, relief="solid")
        shell.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Label(shell, text="Settings", bg="#9be9f7", fg="#00343b", font=("Arial", 10, "bold")).pack(fill="x")

        body = tk.Frame(shell, bg="#c7f3fb")
        body.pack(fill="both", expand=True, padx=8, pady=8)

        tk.Label(body, text="Opacity", bg="#c7f3fb", fg="#00343b", font=("Arial", 8, "bold")).grid(row=0, column=0, sticky="w")
        opacity_var = tk.DoubleVar(value=float(self.cfg.get("opacity", 0.92)))
        opacity_value = tk.Label(body, text=f"{opacity_var.get():.2f}", bg="#c7f3fb", fg="#00343b", width=5)
        opacity_value.grid(row=0, column=2, sticky="e")

        def on_opacity(value):
            val = max(0.25, min(1.0, float(value)))
            self.cfg["opacity"] = val
            opacity_value.configure(text=f"{val:.2f}")
            self.apply_runtime_settings(save=False)

        scale = tk.Scale(body, from_=0.25, to=1.0, resolution=0.01, orient="horizontal", variable=opacity_var, command=on_opacity, bg="#c7f3fb", fg="#00343b", highlightthickness=0)
        scale.grid(row=0, column=1, sticky="ew", padx=6)
        body.columnconfigure(1, weight=1)

        tooltips_var = tk.BooleanVar(value=bool(self.cfg.get("show_tooltips", True)))
        top_var = tk.BooleanVar(value=bool(self.cfg.get("always_on_top", True)))
        normal_hide_var = tk.BooleanVar(value=bool(self.cfg.get("hide_button_emote_text", False)))
        admin_warning_var = tk.BooleanVar(value=bool(self.cfg.get("show_admin_warning", True)))

        tab_vars = {}
        hidden = set(self.cfg.get("hidden_tabs", []))
        # Legacy two toggles also feed into the generic list.
        if not bool(self.cfg.get("show_edge_extras", True)):
            hidden.add("edgeextras")
        if not bool(self.cfg.get("show_bedican_compass", True)):
            hidden.add("bedican")

        def changed():
            self.cfg["show_tooltips"] = bool(tooltips_var.get())
            self.cfg["always_on_top"] = bool(top_var.get())
            self.cfg["topmost_mode"] = "always" if self.cfg["always_on_top"] else "off"
            self.cfg["hide_button_emote_text"] = bool(normal_hide_var.get())
            self.cfg["show_admin_warning"] = bool(admin_warning_var.get())

            new_hidden = []
            for tab_id, var in tab_vars.items():
                if not bool(var.get()):
                    new_hidden.append(tab_id)

            self.cfg["hidden_tabs"] = new_hidden
            # Keep old config keys in sync for people upgrading from earlier builds.
            self.cfg["show_edge_extras"] = "edgeextras" not in new_hidden
            self.cfg["show_bedican_compass"] = "bedican" not in new_hidden

            self.apply_runtime_settings(save=False)
            self.render_tabs()
            self.render_active_tab()
            self.update_admin_warning_banner()

        cb1 = tk.Checkbutton(body, text="Show tooltips", variable=tooltips_var, bg="#c7f3fb", fg="#00343b", command=changed)
        cb1.grid(row=1, column=0, columnspan=3, sticky="w", pady=(8, 0))
        ToolTip(cb1, "Shows helpful hover descriptions for settings and Auto Dance options.")

        cb2 = tk.Checkbutton(body, text="Always on top", variable=top_var, bg="#c7f3fb", fg="#00343b", command=changed)
        cb2.grid(row=2, column=0, columnspan=3, sticky="w", pady=(2, 0))
        ToolTip(cb2, "Keeps the overlay and helper popups above There/the game. Turn off if you want normal windows.")

        cb3 = tk.Checkbutton(body, text="Hide emote text on normal tabs", variable=normal_hide_var, bg="#c7f3fb", fg="#00343b", command=changed)
        cb3.grid(row=3, column=0, columnspan=3, sticky="w", pady=(2, 0))
        ToolTip(cb3, "Applies the same apostrophe-hiding to normal action buttons and the Edit/Send box. Example: 'wave becomes 'wave'.")

        cb4 = tk.Checkbutton(body, text="Show admin-mode warning", variable=admin_warning_var, bg="#c7f3fb", fg="#00343b", command=changed)
        cb4.grid(row=4, column=0, columnspan=3, sticky="w", pady=(2, 0))
        ToolTip(cb4, "Shows the big red warning if ThereQuickActions was not started as administrator.")

        list_label = tk.Label(body, text="Visible lists / tabs", bg="#c7f3fb", fg="#00343b", font=("Arial", 8, "bold"), anchor="w")
        list_label.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(10, 2))

        tab_box = tk.Frame(body, bg="#ffffff", bd=1, relief="solid")
        tab_box.grid(row=6, column=0, columnspan=3, sticky="nsew")
        body.rowconfigure(6, weight=1)

        tab_canvas = tk.Canvas(tab_box, bg="#ffffff", highlightthickness=0, height=190)
        tab_scroll = tk.Scrollbar(tab_box, orient="vertical", command=tab_canvas.yview, width=14)
        tab_inner = tk.Frame(tab_canvas, bg="#ffffff")
        tab_inner_id = tab_canvas.create_window((0, 0), window=tab_inner, anchor="nw")
        tab_canvas.configure(yscrollcommand=tab_scroll.set)
        tab_canvas.pack(side="left", fill="both", expand=True)
        tab_scroll.pack(side="right", fill="y")
        tab_inner.bind("<Configure>", lambda e: tab_canvas.configure(scrollregion=tab_canvas.bbox("all")))
        tab_canvas.bind("<Configure>", lambda e: tab_canvas.itemconfigure(tab_inner_id, width=e.width))
        tab_canvas.bind("<MouseWheel>", lambda e: tab_canvas.yview_scroll((-1 if e.delta > 0 else 1) * 3, "units"))

        reorder_tabs_in_config(self.cfg)
        for tab in self.cfg.get("tabs", []):
            if not isinstance(tab, dict):
                continue
            tab_id = tab.get("id", "")
            label = tab.get("label", tab_id)
            var = tk.BooleanVar(value=(tab_id not in hidden))
            tab_vars[tab_id] = var
            cb = tk.Checkbutton(tab_inner, text=label, variable=var, bg="#ffffff", fg="#00343b", command=changed, anchor="w")
            cb.pack(fill="x", padx=6, pady=2)
            ToolTip(cb, f"Show or hide the {label} tab/list.")

        button_row = tk.Frame(body, bg="#c7f3fb")
        button_row.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(12, 0))

        AquaButton(button_row, "Apply + Save", command=lambda: self.save_settings_window(win), height=26, width=110).pack(side="left", fill="x", expand=True, padx=(0, 4))
        AquaButton(button_row, "Reset Size", command=self.reset_window_size, height=26, width=90).pack(side="left", fill="x", expand=True, padx=(0, 4))
        AquaButton(button_row, "Close", command=win.destroy, height=26, width=70).pack(side="left", fill="x", expand=True)

    def apply_runtime_settings(self, save=True):
        try:
            self.root.attributes("-alpha", float(self.cfg.get("opacity", 0.92)))
        except Exception:
            pass
        try:
            self.root.attributes("-topmost", bool(self.cfg.get("always_on_top", True)))
        except Exception:
            pass
        if self.settings_window is not None and self.settings_window.winfo_exists():
            try:
                self.settings_window.attributes("-topmost", bool(self.cfg.get("always_on_top", True)))
                self.settings_window.attributes("-alpha", float(self.cfg.get("opacity", 0.92)))
            except Exception:
                pass
        if self.dance_editor is not None and hasattr(self.dance_editor, "builder_popup"):
            try:
                self.dance_editor.apply_builder_window_options()
            except Exception:
                pass
        if save:
            save_config(self.cfg)

    def save_settings_window(self, win=None):
        self.apply_runtime_settings(save=True)
        self.status.configure(text="Settings saved.")
        if win is not None and win.winfo_exists():
            win.lift()

    def reset_window_size(self):
        self.root.minsize(self.full_min_w, self.full_min_h)
        self.root.geometry("650x700")
        self.saved_full_geometry = "650x700"
        self.status.configure(text="Window size reset.")


    def update_admin_warning_banner(self):
        if not hasattr(self, "admin_warning_label"):
            return
        try:
            should_show = bool(self.cfg.get("show_admin_warning", True)) and not is_running_as_admin()
            if should_show and not self.admin_warning_label.winfo_ismapped():
                self.admin_warning_label.pack(fill="x", pady=(0, 4), before=self.window_combo.master)
            elif not should_show and self.admin_warning_label.winfo_ismapped():
                self.admin_warning_label.pack_forget()
        except Exception:
            pass

    def tutorial_tab_index_by_id(self, tab_id):
        try:
            for i, tab in enumerate(self.get_visible_tabs()):
                if tab.get("id") == tab_id:
                    return i
        except Exception:
            pass
        return None

    def tutorial_set_tab(self, tab_id):
        idx = self.tutorial_tab_index_by_id(tab_id)
        if idx is None:
            return
        try:
            self.select_tab(idx)
            self.root.update_idletasks()
        except Exception:
            pass

    def tutorial_restore_tab(self, previous_index):
        try:
            if previous_index is not None:
                tabs = self.get_visible_tabs()
                if 0 <= previous_index < len(tabs):
                    self.select_tab(previous_index)
                    self.root.update_idletasks()
        except Exception:
            pass

    def tutorial_target_rect(self, kind):
        self.root.update_idletasks()
        rw = max(1, self.root.winfo_width())
        rh = max(1, self.root.winfo_height())

        def rect_for(widget, pad=5):
            try:
                x = widget.winfo_rootx() - self.root.winfo_rootx() - pad
                y = widget.winfo_rooty() - self.root.winfo_rooty() - pad
                w = widget.winfo_width() + pad * 2
                h = widget.winfo_height() + pad * 2
                return (max(0, int(x)), max(0, int(y)), max(20, int(w)), max(20, int(h)))
            except Exception:
                return (12, 12, rw - 24, 80)

        if kind == "admin":
            if hasattr(self, "admin_warning_label") and self.admin_warning_label.winfo_ismapped():
                return rect_for(self.admin_warning_label, 6)
            return (10, 8, rw - 20, 55)
        if kind == "select":
            return rect_for(self.window_combo, 8) if hasattr(self, "window_combo") else (10, 35, rw - 20, 32)
        if kind == "lock":
            return rect_for(self.lock_selected_big_button, 8) if hasattr(self, "lock_selected_big_button") else (10, 72, rw - 20, 34)
        if kind == "tabs":
            return rect_for(self.tab_bar_outer, 5) if hasattr(self, "tab_bar_outer") else (6, 140, 88, rh - 220)
        if kind == "autodance":
            # Highlight both the Auto Dance tab and the Auto Dance panel area.
            try:
                tab_rect = None
                target_idx = self.tutorial_tab_index_by_id("autodance")
                if target_idx is not None and hasattr(self, "tab_bar"):
                    children = [c for c in self.tab_bar.winfo_children() if c.winfo_class() == "Canvas"]
                    if 0 <= target_idx < len(children):
                        tab_rect = rect_for(children[target_idx], 6)

                panel_rect = rect_for(self.content_shell, 4) if hasattr(self, "content_shell") else (100, 140, rw - 120, rh - 250)
                if tab_rect:
                    x1 = min(tab_rect[0], panel_rect[0])
                    y1 = min(tab_rect[1], panel_rect[1])
                    x2 = max(tab_rect[0] + tab_rect[2], panel_rect[0] + panel_rect[2])
                    y2 = max(tab_rect[1] + tab_rect[3], panel_rect[1] + panel_rect[3])
                    return (x1, y1, x2 - x1, y2 - y1)
                return panel_rect
            except Exception:
                if hasattr(self, "content_shell"):
                    return rect_for(self.content_shell, 4)
                return (100, 140, rw - 120, rh - 250)
        if kind == "edit":
            return rect_for(self.bottom, 5) if hasattr(self, "bottom") else (6, max(0, rh - 100), rw - 12, 90)
        if kind == "settings":
            return rect_for(self.settings_tab_button, 7) if hasattr(self, "settings_tab_button") else (12, max(0, rh - 80), 70, 55)
        if kind == "help":
            return rect_for(self.btn_help, 7) if hasattr(self, "btn_help") else (max(0, rw - 86), 4, 82, 32)
        return (12, 12, rw - 24, rh - 24)

    def start_tutorial(self, force=False):
        if self.tutorial_overlay is not None:
            try:
                self.tutorial_overlay.destroy()
            except Exception:
                pass
            self.tutorial_overlay = None
        if not force and bool(self.cfg.get("tutorial_seen", False)):
            return
        self.tutorial_overlay = TutorialOverlay(self)

    def mark_tutorial_seen(self):
        self.cfg["tutorial_seen"] = True
        save_config(self.cfg)



    def setup_tray_icon(self):
        if not TRAY_AVAILABLE:
            try:
                self.status.configure(text="Tray icon unavailable: install pystray + pillow.")
            except Exception:
                pass
            return

        try:
            icon_path = resource_path("TQA.ico")
            if not os.path.exists(icon_path):
                icon_path = resource_path("TQA.png")
            image = Image.open(icon_path)
        except Exception:
            try:
                image = Image.new("RGBA", (64, 64), (25, 190, 220, 255))
            except Exception:
                return

        def checked_enabled(item):
            return bool(self.cfg.get("enabled", True))

        def checked_top(item):
            return bool(self.cfg.get("always_on_top", True))

        menu = pystray.Menu(
            pystray.MenuItem("Show / Restore", lambda icon, item: self.tray_call(self.show_from_tray)),
            pystray.MenuItem("Enabled", lambda icon, item: self.tray_call(self.toggle_enabled), checked=checked_enabled),
            pystray.MenuItem("Always on top", lambda icon, item: self.tray_call(self.toggle_always_on_top), checked=checked_top),
            pystray.MenuItem("Replay Tutorial", lambda icon, item: self.tray_call(lambda: self.start_tutorial(force=True))),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Close ThereQuickActions", lambda icon, item: self.tray_call(self.on_close)),
        )

        self.tray_icon = pystray.Icon("ThereQuickActions", image, "ThereQuickActions", menu)

        def run_icon():
            try:
                self.tray_icon.run()
            except Exception:
                pass

        self.tray_thread = threading.Thread(target=run_icon, daemon=True)
        self.tray_thread.start()

    def tray_call(self, func):
        try:
            self.root.after(0, func)
        except Exception:
            pass

    def tray_update_menu(self):
        try:
            if self.tray_icon is not None:
                self.tray_icon.update_menu()
        except Exception:
            pass

    def show_from_tray(self):
        try:
            self.root.deiconify()
        except Exception:
            pass
        try:
            self.root.lift()
            self.root.focus_force()
        except Exception:
            pass

    def toggle_enabled(self):
        new_value = not bool(self.cfg.get("enabled", True))
        self.cfg["enabled"] = new_value
        save_config(self.cfg)

        if new_value:
            self.status.configure(text="Actions enabled.")
            self.restart_hotkeys()
        else:
            self.status.configure(text="Actions disabled.")
            try:
                self.dance_player.stop()
            except Exception:
                pass
            try:
                self.hotkey_manager.stop()
            except Exception:
                pass

        self.tray_update_menu()

    def toggle_always_on_top(self):
        self.cfg["always_on_top"] = not bool(self.cfg.get("always_on_top", True))
        self.cfg["topmost_mode"] = "always" if bool(self.cfg.get("always_on_top", True)) else "off"
        self.apply_runtime_settings(save=True)
        self.status.configure(text="Always on top: " + ("on" if self.cfg.get("always_on_top", True) else "off"))
        self.tray_update_menu()

    def stop_tray_icon(self):
        try:
            if self.tray_icon is not None:
                self.tray_icon.stop()
        except Exception:
            pass
        self.tray_icon = None


    def show_help(self):
        self.start_tutorial(force=True)


    def on_close(self):
        if self._closing:
            return
        self._closing = True

        try:
            self.stop_tray_icon()
        except Exception:
            pass

        try:
            if self.dance_editor is not None and hasattr(self.dance_editor, "builder_popup"):
                try:
                    self.dance_editor.save_builder_geometry()
                except Exception:
                    pass
                self.dance_editor.builder_popup.destroy()
        except Exception:
            pass
        try:
            self.dance_player.stop()
        except Exception:
            pass
        try:
            self.hotkey_manager.stop()
        except Exception:
            pass
        self.root.destroy()

    def run(self):
        self.root.mainloop()



class TutorialOverlay:
    HOLE_COLOR = "#ff00ff"

    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.index = 0
        self.original_tab_index = None
        self.autodance_step_index = 4
        self._autodance_tab_switched = False
        self.steps = [
            {
                "kind": "admin",
                "title": "Run as administrator",
                "body": "Always run ThereQuickActions as administrator for the most reliable sends and hotkeys. If it is not admin, the red warning appears at the top.",
            },
            {
                "kind": "select",
                "title": "Select the There window",
                "body": "Pick your There game window from this dropdown. If you do not see it, click the refresh button next to the list.",
            },
            {
                "kind": "lock",
                "title": "Lock selected window",
                "body": "After selecting There, always click LOCK SELECTED WINDOW. That keeps every button aimed at the right There window.",
            },
            {
                "kind": "tabs",
                "title": "Action tabs",
                "body": "Use these tabs for Emotes, Avatar actions, Dance commands, Chat text, Slash commands, Keys, Custom buttons, Edge Extras, Bedican, and Auto Dance.",
            },
            {
                "kind": "autodance",
                "title": "Auto Dance",
                "body": "Auto Dance plays saved dance scripts. Create Dance lets you build dances with bubbles. You can add delays and bind saved dances to F-keys.",
            },
            {
                "kind": "edit",
                "title": "Edit / Send",
                "body": "This box shows what will be sent. You can edit it, type your own command/text, then press Send.",
            },
            {
                "kind": "settings",
                "title": "Settings",
                "body": "The gear opens opacity, always-on-top, visible tab toggles, admin warning, and emote text hiding options.",
            },
            {
                "kind": "help",
                "title": "Replay this tutorial",
                "body": "Click the ? button any time to run this tutorial again.",
            },
        ]

        self.overlay = tk.Toplevel(self.root)
        self.overlay.overrideredirect(True)
        self.overlay.configure(bg=self.HOLE_COLOR)
        self.overlay.attributes("-topmost", True)
        try:
            self.overlay.attributes("-transparentcolor", self.HOLE_COLOR)
        except Exception:
            pass
        try:
            self.overlay.attributes("-alpha", 0.88)
        except Exception:
            pass
        self.overlay.transient(self.root)

        self.canvas = tk.Canvas(self.overlay, bg=self.HOLE_COLOR, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        self.bubble = tk.Toplevel(self.root)
        self.bubble.overrideredirect(True)
        self.bubble.configure(bg="#a5dbe4")
        self.bubble.attributes("-topmost", True)
        self.bubble.transient(self.root)

        shell = tk.Frame(self.bubble, bg="#a5dbe4", bd=1, relief="solid")
        shell.pack(fill="both", expand=True)
        self.title_label = tk.Label(shell, text="", bg="#8ee8f7", fg="#00343b", font=("Arial", 10, "bold"), anchor="w", padx=8, pady=4)
        self.title_label.pack(fill="x")
        self.body_label = tk.Label(shell, text="", bg="#eaffff", fg="#00343b", font=("Arial", 9), wraplength=285, justify="left", padx=10, pady=8)
        self.body_label.pack(fill="both", expand=True)

        btns = tk.Frame(shell, bg="#dffbff")
        btns.pack(fill="x", padx=6, pady=(0, 6))
        self.back_btn = AquaButton(btns, "Back", command=self.back, height=26, width=75)
        self.back_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.skip_btn = AquaButton(btns, "Skip Tutorial", command=self.skip, height=26, width=115)
        self.skip_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.next_btn = AquaButton(btns, "Next", command=self.next, height=26, width=75)
        self.next_btn.pack(side="left", fill="x", expand=True)

        self._config_job = None
        self.root.bind("<Configure>", self.on_root_configure, add="+")
        self.overlay.bind("<Escape>", lambda e: self.skip())
        self.bubble.bind("<Escape>", lambda e: self.skip())

        self.refresh_geometry()
        self.show_step()

    def destroy(self):
        try:
            self.overlay.destroy()
        except Exception:
            pass
        try:
            self.bubble.destroy()
        except Exception:
            pass
        self.app.tutorial_overlay = None

    def on_root_configure(self, event=None):
        # Debounce while dragging/resizing so the tutorial does not stutter.
        if self._config_job is not None:
            try:
                self.root.after_cancel(self._config_job)
            except Exception:
                pass
        self._config_job = self.root.after(35, self._redraw_after_config)

    def _redraw_after_config(self):
        self._config_job = None
        try:
            self.refresh_geometry()
            self.show_step()
        except Exception:
            pass

    def refresh_geometry(self):
        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        w = max(100, self.root.winfo_width())
        h = max(100, self.root.winfo_height())
        self.overlay.geometry(f"{w}x{h}+{x}+{y}")

    def best_bubble_position(self, x, y, w, h, bw, bh, ow, oh):
        """Place bubble next to the highlighted target, outside the highlighted area whenever possible."""
        margin = 8
        gap = 14

        # Available room on each side of the highlighted rectangle.
        room_right = ow - (x + w) - margin
        room_left = x - margin
        room_below = oh - (y + h) - margin
        room_above = y - margin

        target_cx = x + w / 2
        target_cy = y + h / 2

        candidates = []

        if room_right >= bw + gap:
            candidates.append((x + w + gap, y + h / 2 - bh / 2, "right"))
        if room_left >= bw + gap:
            candidates.append((x - bw - gap, y + h / 2 - bh / 2, "left"))
        if room_below >= bh + gap:
            candidates.append((x + w / 2 - bw / 2, y + h + gap, "below"))
        if room_above >= bh + gap:
            candidates.append((x + w / 2 - bw / 2, y - bh - gap, "above"))

        # If the window is too small for a perfect outside placement, choose the side with most room.
        if not candidates:
            side_rooms = [
                ("right", room_right),
                ("left", room_left),
                ("below", room_below),
                ("above", room_above),
            ]
            best_side = max(side_rooms, key=lambda t: t[1])[0]
            if best_side == "right":
                candidates.append((x + w + gap, y + h / 2 - bh / 2, "right-forced"))
            elif best_side == "left":
                candidates.append((x - bw - gap, y + h / 2 - bh / 2, "left-forced"))
            elif best_side == "below":
                candidates.append((x + w / 2 - bw / 2, y + h + gap, "below-forced"))
            else:
                candidates.append((x + w / 2 - bw / 2, y - bh - gap, "above-forced"))

        best = None
        for bx, by, side in candidates:
            cbx = max(margin, min(int(bx), max(margin, ow - bw - margin)))
            cby = max(margin, min(int(by), max(margin, oh - bh - margin)))

            # Prefer positions whose CENTER is closest to the target center but never over the target if avoidable.
            bubble_cx = cbx + bw / 2
            bubble_cy = cby + bh / 2
            dist = ((bubble_cx - target_cx) ** 2 + (bubble_cy - target_cy) ** 2) ** 0.5

            overlaps = not (cbx + bw <= x or cbx >= x + w or cby + bh <= y or cby >= y + h)
            overlap_penalty = 100000 if overlaps and "forced" not in side else 0
            score = overlap_penalty + dist

            if best is None or score < best[0]:
                best = (score, cbx, cby)

        return int(best[1]), int(best[2])

    def show_step(self):
        self.refresh_geometry()
        self.root.update_idletasks()

        # Step 5/8 is Auto Dance: switch to Auto Dance so the tutorial highlights the right thing.
        if self.index == self.autodance_step_index and not self._autodance_tab_switched:
            self.original_tab_index = getattr(self.app, "active_tab_index", None)
            self.app.tutorial_set_tab("autodance")
            self._autodance_tab_switched = True
        elif self._autodance_tab_switched and self.index != self.autodance_step_index:
            self.app.tutorial_restore_tab(self.original_tab_index)
            self._autodance_tab_switched = False

        step = self.steps[self.index]
        x, y, w, h = self.app.tutorial_target_rect(step["kind"])

        ow = max(100, self.root.winfo_width())
        oh = max(100, self.root.winfo_height())

        c = self.canvas
        c.delete("all")

        # Darken everything around the highlighted target. The target area stays transparent.
        c.create_rectangle(0, 0, ow, y, fill="#000000", outline="#000000")
        c.create_rectangle(0, y + h, ow, oh, fill="#000000", outline="#000000")
        c.create_rectangle(0, y, x, y + h, fill="#000000", outline="#000000")
        c.create_rectangle(x + w, y, ow, y + h, fill="#000000", outline="#000000")

        c.create_rectangle(x, y, x + w, y + h, outline="#ffef78", width=3)
        c.create_rectangle(x + 3, y + 3, x + w - 3, y + h - 3, outline="#63f7ff", width=2)

        self.title_label.configure(text=f"{self.index + 1}/{len(self.steps)}  {step['title']}")
        self.body_label.configure(text=step["body"])
        self.next_btn.text = "Done" if self.index == len(self.steps) - 1 else "Next"
        self.next_btn.redraw(False)

        self.bubble.update_idletasks()
        bw = min(360, max(300, self.bubble.winfo_reqwidth()))
        bh = min(220, max(145, self.bubble.winfo_reqheight()))

        bx, by = self.best_bubble_position(x, y, w, h, bw, bh, ow, oh)
        rx = self.root.winfo_rootx() + bx
        ry = self.root.winfo_rooty() + by
        self.bubble.geometry(f"{bw}x{bh}+{rx}+{ry}")
        try:
            self.bubble.update_idletasks()
        except Exception:
            pass

        self.overlay.lift()
        self.bubble.lift()

    def next(self):
        if self.index >= len(self.steps) - 1:
            self.finish()
            return
        self.index += 1
        self.show_step()

    def back(self):
        if self.index <= 0:
            return
        self.index -= 1
        self.show_step()

    def skip(self):
        self.finish()

    def finish(self):
        if self._autodance_tab_switched:
            self.app.tutorial_restore_tab(self.original_tab_index)
            self._autodance_tab_switched = False
        self.app.mark_tutorial_seen()
        self.destroy()



if __name__ == "__main__":
    relaunch_as_admin_if_needed()
    ThereOverlayApp().run()
