import requests
import csv
from datetime import datetime

API_TOKEN = "add_here"  # Replace this with a secure, regenerated token
BASE_URL = "https://api.pagerduty.com"

HEADERS = {
    "Authorization": f"Token token={API_TOKEN}",
    "Accept": "application/vnd.pagerduty+json;version=2",
    "Content-Type": "application/json"
}

def get_paginated(endpoint):
    items = []
    limit = 100
    offset = 0
    more = True

    while more:
        response = requests.get(
            f"{BASE_URL}/{endpoint}",
            headers=HEADERS,
            params={"limit": limit, "offset": offset}
        )
        data = response.json()
        items.extend(data[endpoint])
        more = data.get("more", False)
        offset += limit

    print(f"🔹 Fetched {len(items)} items from {endpoint}")
    return items

def get_teams():
    teams = get_paginated("teams")
    return {team["id"]: team["name"] for team in teams}

def get_schedules():
    return get_paginated("schedules")

def get_escalation_policies():
    return get_paginated("escalation_policies")

def get_team_schedule_policy_mapping():
    teams = get_teams()
    schedules = get_schedules()
    policies = get_escalation_policies()

    # Map: schedule_id → team names
    schedule_to_teams = {}
    for sched in schedules:
        team_ids = sched.get("teams", [])
        team_names = [teams.get(team["id"], "Unknown Team") for team in team_ids]
        schedule_to_teams[sched["id"]] = team_names

    # Build final rows
    rows = []
    for policy in policies:
        for rule in policy.get("escalation_rules", []):
            for target in rule.get("targets", []):
                if target["type"] == "schedule_reference":
                    schedule_id = target["id"]
                    schedule = next((s for s in schedules if s["id"] == schedule_id), None)
                    if schedule:
                        schedule_name = schedule["name"]
                        team_names = schedule_to_teams.get(schedule_id, ["(No team)"])
                        for team in team_names:
                            rows.append({
                                "Team": team,
                                "Schedule Name": schedule_name,
                                "Schedule ID": schedule_id,
                                "Escalation Policy": policy["name"],
                                "Escalation Policy ID": policy["id"]
                            })

    print(f"✅ Built {len(rows)} team → schedule → policy mappings")
    return rows

def write_to_csv(data, filename_prefix="team_schedule_policy"):
    timestamp = datetime.now()
    formatted_time = timestamp.strftime("%Y-%m-%d %H:%M")
    filename = f"{filename_prefix}_{timestamp.strftime('%Y-%m-%d_%H-%M')}.csv"

    if data:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            file.write(f"# Generated on {formatted_time}\n")
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ CSV saved as {filename}")
    else:
        print("⚠️ No data to write.")

if __name__ == "__main__":
    data = get_team_schedule_policy_mapping()
    write_to_csv(data)
