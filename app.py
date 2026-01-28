import os
from groq import Groq
from flask import Flask, request
import requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Groq Setup
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "GrowBot_Secret_123")

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get('object') == 'page':
        for entry in data.get('entry', []):
            for messaging_event in entry.get('messaging', []):
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message'].get('text')
                    
                    if message_text:
                        try:
                            # Groq AI ဆီက အဖြေတောင်းခြင်း
                            completion = client.chat.completions.create(
                                model="llama3-8b-8192", 
                                messages=[
                                    {"role": "system", "content": "မင်းက GrowBot Agency ရဲ့ AI Manager ပါ။ ယဉ်ကျေးပျူငှာစွာ စာပြန်ပေးပါ။"},
                                    {"role": "user", "content": message_text}
                                ]
                            )
                            ai_answer = completion.choices[0].message.content
                            send_message(sender_id, ai_answer)
                        except Exception as e:
                            print(f"Error: {e}")
    return "ok", 200

def send_message(recipient_id, message_text):
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post("https://graph.facebook.com/v12.0/me/messages", params=params, headers=headers, json=data)

if __name__ == "__main__":
    app.run(port=5000)
