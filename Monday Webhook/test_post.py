import requests

MONDAY_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMDgzOTgxNCwiYWFpIjoxMSwidWlkIjo2Mjg4Mjg0MywiaWFkIjoiMjAyNC0xMC0zMVQxODoyNDo1NS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjAwMTk5MjMsInJnbiI6InVzZTEifQ.OwrhlolZ6uLUI2LQQ8pjA1DRPCc61kx_n3a3j6lM09E"
BOARD_ID = "9334635005"

query = """
query ($board_id: ID!) {
  boards(ids: [$board_id]) {
    webhooks {
      id
      url
      event
    }
  }
}
"""

variables = {
    "board_id": BOARD_ID
}

res = requests.post(
    "https://api.monday.com/v2",
    headers={
        "Authorization": MONDAY_API_KEY,
        "Content-Type": "application/json"
    },
    json={"query": query, "variables": variables}
)

print(res.text)
