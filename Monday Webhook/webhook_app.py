from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")
HEADERS = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("Webhook received:", data)

    try:
        item_id = data['event']['pulseId']
        board_id = data['event']['boardId']
        trigger_col = data['event']['columnId']

        print(f"Column {trigger_col} changed on item {item_id} in board {board_id}")

        # Basic response: create a new item on same board
        mutation = f'''
        mutation {{
            create_item(board_id: {board_id}, item_name: "Auto-created on status change") {{
                id
            }}
        }}
        '''
        res = requests.post('https://api.monday.com/v2', headers=HEADERS, json={'query': mutation})
        print("Create item response:", res.text)

    except Exception as e:
        print("Error handling webhook:", e)

    return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET'])
def home():
    return "Webhook listener is live", 200
