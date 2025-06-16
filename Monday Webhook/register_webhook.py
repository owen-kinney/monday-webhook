import requests

MONDAY_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMDgzOTgxNCwiYWFpIjoxMSwidWlkIjo2Mjg4Mjg0MywiaWFkIjoiMjAyNC0xMC0zMVQxODoyNDo1NS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjAwMTk5MjMsInJnbiI6InVzZTEifQ.OwrhlolZ6uLUI2LQQ8pjA1DRPCc61kx_n3a3j6lM09E"
BOARD_ID = "9379787189"  # keep in quotes!
WEBHOOK_URL = "https://webhook.site/f194683c-5468-44f7-be8b-69b620fcbddf"

query = """
mutation ($board_id: ID!, $url: String!) {
  create_webhook(board_id: $board_id, url: $url, event: create_update) {
    id
  }
}
"""

variables = {
    "board_id": BOARD_ID,
    "url": WEBHOOK_URL
}

response = requests.post(
    "https://api.monday.com/v2",
    headers={
        "Authorization": MONDAY_API_KEY,
        "Content-Type": "application/json"
    },
    json={
        "query": query,
        "variables": variables
    }
)

print("Status:", response.status_code)
print("Response:", response.text)

