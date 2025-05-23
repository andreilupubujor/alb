import requests
import csv
from datetime import datetime

API_TOKEN = "add_here"  # Replace with a new secure token
BASE_URL = "https://api.pagerduty.com"

HEADERS = {
    "Authorization": f"Token token={API_TOKEN}",
    "Accept": "application/vnd.pagerduty+json;version=2",
    "Content-Type": "application/json"
}

def get_users():
    users = []
    limit = 100
    offset = 0
    more = True

    while more:
        response = requests.get(
            f"{BASE_URL}/users",
            headers=HEADERS,
            params={"limit": limit, "offset": offset}
        )
        data = response.json()
        users.extend(data["users"])
        more = data.get("more", False)
        offset += limit

    print(f"🔹 Fetched {len(users)} users")
    return users

def get_teams():
    teams = []
    limit = 100
    offset = 0
    more = True

    while more:
        response = requests.get(
            f"{BASE_URL}/teams",
            headers=HEADERS,
            params={"limit": limit, "offset": offset}
        )
        data = response.json()
        teams.extend(data["teams"])
        more = data.get("more", False)
        offset += limit

    print(f"🔹 Fetched {len(teams)} teams")
    return {team["id"]: team["name"] for team in teams}

def get_schedules():
    schedules = []
    limit = 100
    offset = 0
    more = True

    while more:
        response = requests.get(
            f"{BASE_URL}/schedules",
            headers=HEADERS,
            params={"limit": limit, "offset": offset}
        )
        data = response.json()
        schedules.extend(data["schedules"])
        more = data.get("more", False)
        offset += limit

    print(f"🔹 Fetched {len(schedules)} schedules")
    return schedules

def get_escalation_policies():
    policies = []
    url = f"{BASE_URL}/escalation_policies"
    more = True
    offset = 0
    limit = 100

    while more:
        response = requests.get(
            url,
            headers=HEADERS,
            params={"limit": limit, "offset": offset}
        )
        data = response.json()
        policies.extend(data["escalation_policies"])
        more = data.get("more", False)
        offset += limit

    print(f"🔹 Fetched {len(policies)} escalation policies")
    return policies

def build_user_schedule_policy_map():
    users = get_users()
    teams = get_teams()
    schedules = get_schedules()
    policies = get_escalation_policies()

    schedule_map = {}
    for sched in schedules:
        for user in sched.get("users", []):
            schedule_map.setdefault(user["id"], []).append({
                "schedule_name": sched["name"],
                "schedule_id": sched["id"]
            })

    policy_schedule_map = {}
    for policy in policies:
        for rule in policy["escalation_rules"]:
            for target in rule.get("targets", []):
                if target["type"] == "schedule_reference":
                    policy_schedule_map.setdefault(target["id"], []).append(policy["name"])

    result = []
    for user in users:
        user_id = user["id"]
        team_names = [teams[team["id"]] for team in user.get("teams", []) if team["id"] in teams]
        schedules = schedule_map.get(user_id, [])
        schedule_names = [s["schedule_name"] for s in schedules]
        related_policies = [p for s in schedules for p in policy_schedule_map.get(s["schedule_id"], [])]

        result.append({
            "Name": user["name"],
            "Email": user["email"],
            "Teams": ", ".join(team_names),
            "Schedules": ", ".join(schedule_names),
            "Escalation Policies": ", ".join(set(related_policies))
        })

    print(f"✅ Built summary for {len(result)} users")
    return result

def write_to_csv(data):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"pagerduty_user_summary_{timestamp}.csv"

    if data:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ CSV saved as {filename}")
    else:
        print("⚠️ No data to write to CSV.")

if __name__ == "__main__":
    data = build_user_schedule_policy_map()
    write_to_csv(data)
