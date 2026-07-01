import json
from datetime import datetime, timezone
import os


LOG_FILE = "audit_log.json"


def write_audit_log(entry):
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as file:
            logs = json.load(file)
    else:
        logs = []

    logs.append(entry)

    with open(LOG_FILE, "w") as file:
        json.dump(logs, file, indent=4)


def get_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as file:
            return json.load(file)

    return []
def update_status(content_id, new_status, appeal_reason):

    if os.path.exists(LOG_FILE):

        with open(LOG_FILE, "r") as file:
            logs = json.load(file)

    else:
        return False


    for entry in logs:

        if entry["content_id"] == content_id:

            entry["status"] = new_status

            entry["appeal"] = {
                "reason": appeal_reason,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


            with open(LOG_FILE, "w") as file:
                json.dump(logs, file, indent=4)


            return True


    return False