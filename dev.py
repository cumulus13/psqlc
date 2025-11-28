import os
import sys
import time
import hashlib
import shutil
from gntp.notifier import GrowlNotifier

PARENT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "psqlc.py"))
TARGET_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "psqlc", "psqlc.py"))
ICON_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "psqlc.png"))

APPNAME = "psqlc"
EVENT_NAME = "changed"


# -----------------------------------
# Utility: hash helper
# -----------------------------------
def hash_file(path):
    try:
        h = hashlib.sha1()
        with open(path, "rb") as f:
            h.update(f.read())
        return h.hexdigest()
    except:
        return None


# -----------------------------------
# Growl notifier (GNTP)
# -----------------------------------
growl = GrowlNotifier(
    applicationName=APPNAME,
    notifications=[EVENT_NAME],
    defaultNotifications=[EVENT_NAME],
    applicationIcon=open(ICON_FILE, "rb").read() if os.path.isfile(ICON_FILE) else None,
)
growl.register()


def notify(title, message):
    try:
        growl.notify(
            noteType=EVENT_NAME,
            title=title,
            description=message,
            icon=open(ICON_FILE, "rb").read() if os.path.isfile(ICON_FILE) else None,
            sticky=False,
            priority=1,
        )
    except Exception as e:
        print(f"[WARN] Growl error: {e}")


# -----------------------------------
# Main logic
# -----------------------------------
def main():
    # if len(sys.argv) < 2 or sys.argv[1] != "start":
    #     print("Usage: python def start")
    #     sys.exit(1)

    print("Monitoring started...")
    print(f"Parent   : {PARENT_FILE}")
    print(f"Target   : {TARGET_FILE}")
    print("CTRL+C to stop.\n")

    # current_hash = hash_file(PARENT_FILE)
    # print(f"current_hash: {current_hash}")

    while True:
        time.sleep(1)

        parent_hash = hash_file(PARENT_FILE)
        target_hash = hash_file(TARGET_FILE)
        # print(f"target_hash: {target_hash}")

        if parent_hash != target_hash:
            try:
                shutil.copy2(PARENT_FILE, TARGET_FILE)
                print(f"[UPDATE] {PARENT_FILE} -> {TARGET_FILE}")

                notify(
                    "psqlc updated",
                    "Parent psqlc.py changed and synced to psqlc/psqlc.py"
                )

            except Exception as e:
                print(f"[ERROR] copy failed: {e}")

            # current_hash = target_hash


if __name__ == "__main__":
    main()
