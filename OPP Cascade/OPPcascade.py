import requests
import json

# === 🔧 CONFIG ===
API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMDgzOTgxNCwiYWFpIjoxMSwidWlkIjo2Mjg4Mjg0MywiaWFkIjoiMjAyNC0xMC0zMVQxODoyNDo1NS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjAwMTk5MjMsInJnbiI6InVzZTEifQ.OwrhlolZ6uLUI2LQQ8pjA1DRPCc61kx_n3a3j6lM09E"
API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

# Your Company OPP board
COMPANY_BOARD_ID = 9334635005  # Replace with your actual board ID

# Template board to duplicate
TEMPLATE_BOARD_ID = 9334633767  # Replace with your clean team OPP template board ID

# Optional: Workspace to place new boards in
WORKSPACE_ID = 11082085  # Replace with your workspace ID or set to None

# Column ID for the Teams multi-select dropdown (you can find this via Monday UI or API)
TEAM_COLUMN_ID = "dropdown_mkrrnger"  # This is usually the internal ID for your dropdown column


# === 🔌 API HELPERS ===
def run_query(query, variables=None):
    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=HEADERS)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print("❌ Monday API Error Response:")
        print(response.text)  # << This will show the cause
        raise
    return response.json()



# === 📥 FETCH COMPANY OPP ITEMS ===
def get_company_board_items(board_id):
    query = """
    query ($board_ids: [ID!]) {
      boards(ids: $board_ids) {
        id
        name
        items_page(limit: 100) {
          items {
            id
            name
            column_values {
              id
              text
              value
            }
          }
        }
      }
    }
    """
    data = run_query(query, {"board_ids": [str(board_id)]})
    return data["data"]["boards"][0]["items_page"]["items"]


# === 📤 EXTRACT UNIQUE TEAM TAGS ===
def extract_unique_teams(items, team_column_id):
    unique_teams = set()
    for item in items:
        for col in item["column_values"]:
            if col["id"] == team_column_id and col["text"]:
                teams = [t.strip() for t in col["text"].split(",")]
                unique_teams.update(teams)
    return unique_teams


# === 📋 DUPLICATE TEMPLATE BOARD ===
def duplicate_team_board(team_name, template_board_id, workspace_id=None):
    query = """
    mutation ($board_id: ID!, $board_name: String!, $workspace_id: ID) {
      duplicate_board(
        board_id: $board_id,
        duplicate_type: duplicate_board_with_structure,
        board_name: $board_name,
        workspace_id: $workspace_id
      ) {
        board {
          id
          name
        }
      }
    }
    """

    board_title = f"{team_name} OPP – Q3 2025"
    variables = {
        "board_id": str(template_board_id),
        "board_name": board_title
    }
    if workspace_id:
        variables["workspace_id"] = str(workspace_id)

    result = run_query(query, variables)
    return result["data"]["duplicate_board"]["board"]


def create_team_items(company_items, team_boards):
    for item in company_items:
        item_name = item["name"]
        column_values = item["column_values"]

        # Find all tagged teams
        for col in column_values:
            if col["id"] == TEAM_COLUMN_ID and col["text"]:
                teams = [t.strip() for t in col["text"].split(",")]

                for team in teams:
                    if team not in team_boards:
                        print(f"⚠️ Skipping team {team} (no board found)")
                        continue

                    board_id = team_boards[team]

                    # === 1. Get the group_id for "Cobalt OPP"
                    group_query = """
                    query ($board_id: [ID!]) {
                      boards(ids: $board_id) {
                        groups {
                          id
                          title
                        }
                      }
                    }
                    """
                    group_data = run_query(group_query, {"board_id": [str(board_id)]})
                    groups = group_data["data"]["boards"][0]["groups"]
                    cobalt_group = next((g["id"] for g in groups if g["title"] == "Cobalt OPP"), None)

                    if not cobalt_group:
                        print(f"❌ Group 'Cobalt OPP' not found on {team}'s board")
                        continue

                    # === 2. Create the item in that group's board
                    print(f"📝 Creating '{item_name}' on {team}'s board...")
                    create_query = """
                    mutation ($board_id: ID!, $group_id: String!, $item_name: String!) {
                      create_item(
                        board_id: $board_id,
                        group_id: $group_id,
                        item_name: $item_name
                      ) {
                        id
                      }
                    }
                    """
                    create_vars = {
                        "board_id": str(board_id),
                        "group_id": cobalt_group,
                        "item_name": item_name
                    }
                    run_result = run_query(create_query, create_vars)
                    team_item_id = run_result["data"]["create_item"]["id"]

                    # === 3. Create subitem under company item with link as name
                    company_item_id = str(item["id"])
                    team_item_url = f"https://cobaltsp.monday.com/boards/{board_id}/pulses/{team_item_id}"
                    subitem_name = f"({team_item_url})"

                    subitem_query = """
                    mutation ($parent_item_id: ID!, $item_name: String!) {
                      create_subitem(parent_item_id: $parent_item_id, item_name: $item_name) {
                        id
                      }
                    }
                    """
                    subitem_vars = {
                        "parent_item_id": str(company_item_id),
                        "item_name": subitem_name
                    }
                    subitem_result = run_query(subitem_query, subitem_vars)
                    subitem_id = subitem_result["data"]["create_subitem"]["id"]

                    # === 4. Lookup subitem board ID
                    board_lookup_query = """
                    query ($item_id: [ID!]) {
                      items(ids: $item_id) {
                        board {
                          id
                        }
                      }
                    }
                    """
                    board_lookup_vars = {"item_id": [int(subitem_id)]}
                    board_lookup_result = run_query(board_lookup_query, board_lookup_vars)
                    subitem_board_id = board_lookup_result["data"]["items"][0]["board"]["id"]

                    # === 5. Update subitem text column to say 'Finance Updates'
                    update_column_query = """
                    mutation ($board_id: ID!, $item_id: ID!, $column_id: String!, $value: JSON!) {
                      change_column_value(board_id: $board_id, item_id: $item_id, column_id: $column_id, value: $value) {
                        id
                      }
                    }
                    """
                    update_column_vars = {
                        "board_id": str(subitem_board_id),
                        "item_id": int(subitem_id),
                        "column_id": "text_mkrrfmx5",  # ← your actual Team column ID
                        "value": json.dumps(f"{team} Updates")
                    }
                    run_query(update_column_query, update_column_vars)

                    print(
                        f"🔗 Subitem created under '{item_name}' linking to {team} board item and labeled '{team} Updates'")




# === 🚀 MAIN DRIVER ===
def main():
    print("📥 Fetching Company OPP items...")
    items = get_company_board_items(COMPANY_BOARD_ID)
    teams = extract_unique_teams(items, TEAM_COLUMN_ID)

    print(f"🧩 Unique teams found: {teams}")

    created_boards = {}
    for team in teams:
        print(f"📋 Creating board for team: {team}")
        new_board = duplicate_team_board(team, TEMPLATE_BOARD_ID, None)
        created_boards[team] = new_board["id"]
        print(f"✅ Created board: '{new_board['name']}' (ID: {new_board['id']})")

    print("\n🎉 All team boards created successfully.")
    create_team_items(items,created_boards)
    #return created_boards


if __name__ == "__main__":
    main()



