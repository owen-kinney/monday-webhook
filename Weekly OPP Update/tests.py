import requests

API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzMDgzOTgxNCwiYWFpIjoxMSwidWlkIjo2Mjg4Mjg0MywiaWFkIjoiMjAyNC0xMC0zMVQxODoyNDo1NS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjAwMTk5MjMsInJnbiI6InVzZTEifQ.OwrhlolZ6uLUI2LQQ8pjA1DRPCc61kx_n3a3j6lM09E'
BOARD_ID = 9283543082  # Your board ID

headers = {
    "Authorization": API_KEY
}

query = f"""
{{
  boards(ids: [{BOARD_ID}]) {{
    items_page(limit: 1) {{
      items {{
        name
        column_values {{
          id
          text
        }}
      }}
    }}
  }}
}}
"""

response = requests.post(
    url="https://api.monday.com/v2",
    json={"query": query},
    headers=headers
)

import json
print(json.dumps(response.json(), indent=2))
