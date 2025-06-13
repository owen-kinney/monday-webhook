import requests

API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMDgzOTgxNCwiYWFpIjoxMSwidWlkIjo2Mjg4Mjg0MywiaWFkIjoiMjAyNC0xMC0zMVQxODoyNDo1NS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjAwMTk5MjMsInJnbiI6InVzZTEifQ.OwrhlolZ6uLUI2LQQ8pjA1DRPCc61kx_n3a3j6lM09E"
API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

COMPANY_BOARD_ID = 9334635005  # Replace with your actual company OPP board ID
TEAM_BOARD_MAP = {
    "Finance": 9335990051,
    "Integration": 9335989749,
    "People": 9335990876,
    "Tech": 9335990353
    # Add other teams here
}

TEAM_COLUMN_ID = "dropdown_mkrrnger"  # Replace with your actual Teams dropdown column ID


def run_query(query, variables=None):
    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=HEADERS)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print("❌ Error:")
        print(response.text)
        raise
    return response.json()


def get_company_items(board_id):
    query = """
    query ($board_id: [ID!]) {
      boards(ids: $board_id) {
        items_page(limit: 100) {
          items {
            id
            name
            column_values {
              id
              text
            }
            subitems {
              id
              name
            }
          }
        }
      }
    }
    """
    data = run_query(query, {"board_id": [str(board_id)]})
    return data["data"]["boards"][0]["items_page"]["items"]


def get_team_board_item_by_name(board_id, item_name):
    query = """
    query ($board_id: [ID!]) {
      boards(ids: $board_id) {
        items_page(limit: 100) {
          items {
            id
            name
          }
        }
      }
    }
    """
    data = run_query(query, {"board_id": [str(board_id)]})
    for item in data["data"]["boards"][0]["items_page"]["items"]:
        if item["name"] == item_name:
            return item["id"]
    return None


def get_subitem_statuses(parent_id):
    query = """
    query ($parent_id: [ID!]) {
      items(ids: $parent_id) {
        subitems {
          name
          column_values {
            id
            text
          }
        }
      }
    }
    """
    data = run_query(query, {"parent_id": [str(parent_id)]})
    subitems = data["data"]["items"][0]["subitems"]
    status_summary = []

    for s in subitems:
        name = s["name"]
        status = next((col["text"] for col in s["column_values"] if col["id"] == "status"), "Unknown")
        status_summary.append(f"- {name}: {status}")
    return status_summary


def post_update_to_company_subitem(subitem_id, update_body):
    mutation = """
    mutation ($item_id: ID!, $body: String!) {
      create_update(item_id: $item_id, body: $body) {
        id
      }
    }
    """
    variables = {
        "item_id": str(subitem_id),
        "body": update_body
    }
    run_query(mutation, variables)


def main():
    print("📥 Fetching company board items...")
    company_items = get_company_items(COMPANY_BOARD_ID)

    for item in company_items:
        item_name = item["name"]
        item_id = item["id"]
        subitems = item.get("subitems", [])
        tagged_teams = []

        for col in item["column_values"]:
            if col["id"] == TEAM_COLUMN_ID and col["text"]:
                tagged_teams = [t.strip() for t in col["text"].split(",")]

        for team in tagged_teams:
            if team not in TEAM_BOARD_MAP:
                print(f"⚠️ Team '{team}' not found in TEAM_BOARD_MAP")
                continue

            # Find matching item in team board
            team_board_id = TEAM_BOARD_MAP[team]
            team_item_id = get_team_board_item_by_name(team_board_id, item_name)
            if not team_item_id:
                print(f"❌ Could not find item '{item_name}' in {team} board")
                continue

            # Pull subitem statuses from team board item
            status_lines = get_subitem_statuses(team_item_id)
            if not status_lines:
                print(f"ℹ️ No subitems found for team item '{item_name}' in {team}")
                continue

            summary_text = f"**{team} team related items:**\n" + "\n".join(status_lines)

            # Find the "Team Updates" subitem under this company item
            target_subitem = next((s for s in subitems if s["name"] == f"{team} Updates"), None)
            if not target_subitem:
                print(f"⚠️ No subitem named '{team} Updates' under company item '{item_name}'")
                continue

            print(f"✏️ Posting update to '{team} Updates' subitem under '{item_name}'...")
            post_update_to_company_subitem(target_subitem["id"], summary_text)

    print("✅ Weekly update complete.")


if __name__ == "__main__":
    main()
