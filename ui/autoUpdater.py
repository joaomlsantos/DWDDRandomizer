import json
import threading
import webbrowser
from tkinter import messagebox

import urllib.request

GITHUB_REPO = "joaomlsantos/DWDDRandomizer"

def parseVersion(version_str: str) -> tuple:
    version_str = version_str.lstrip("v")
    return tuple(int(x) for x in version_str.split("."))

def getDisplayVersion(version_str: str) -> str:
    return version_str.lstrip("v")


def checkVersionUpdate(root, current_version, preferences_path):
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        latest_version = data["tag_name"].lstrip("v")
        release_url = data["html_url"]

        if parseVersion(latest_version) > parseVersion(current_version):
            skipped = _load_skipped_version(preferences_path)
            if skipped == latest_version:
                return

            message = f"A new version ({latest_version}) is available.\n\n"
            message += f"You are currently on version {getDisplayVersion(current_version)}.\n\n"
            message += "Would you like to download it now?"

            root.after(0, lambda: showUpdateDialog(root, message, release_url, latest_version, preferences_path))

    except Exception as e:
        print(f"Update check failed: {e}")

def showUpdateDialog(root, message, release_url, latest_version, preferences_path):
    result = messagebox.askyesno(
        "Update Available",
        message,
        icon='info',
        parent=root
    )
    if result:
        webbrowser.open(release_url)
    else:
        _save_skipped_version(preferences_path, latest_version)


def _load_skipped_version(preferences_path):
    try:
        with open(preferences_path, 'r') as f:
            preferences = json.load(f)
            return preferences.get("skipped_update_version")
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _save_skipped_version(preferences_path, version):
    try:
        with open(preferences_path, 'r') as f:
            preferences = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        preferences = {}

    preferences["skipped_update_version"] = version

    try:
        with open(preferences_path, 'w') as f:
            json.dump(preferences, f, indent=2)
    except Exception:
        pass


def mainThreadCheck(root, current_version, preferences_path):
    thread = threading.Thread(
        target=checkVersionUpdate,
        args=(root, current_version, preferences_path),
        daemon=True
    )
    thread.start()