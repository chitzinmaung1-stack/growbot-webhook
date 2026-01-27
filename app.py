import requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

# --- Configuration ---
PAGE_ACCESS_TOKEN = "EAAbEi8p64aoBQigERfHgf4ctsepNnwI6Q44wwNqSQaGMijKuq6anur7KgbIkxOdFyZAEZC1bM7P4P8GSdnyZCuj04ZAL64klilY5HSe28ZBPcZA0lLMoPWWYPeBomNOsweLSAKwZBdWXxWpjyX5HK8Jv1yvxVl4LEIF6PtetQBju6HXJ3tAyLNcUiHznyK508FAv3nGtQZDZD"
VERIFY_TOKEN = "GrowBot_Secret_123"
GEMINI_API_KEY = "AIzaSyCe5I9_lyDiUQID2kPAx9awJceBnRMDNQs"

# Gemini AI Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

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
                            # 1. Gemini ဆီက အဖြေတောင်းခြင်း
                            prompt = f"မင်းက GrowBot Agency ရဲ့ AI Manager ပါ။ ယဉ်ကျေးစွာ စာပြန်ပေးပါ။ မေးခွန်းမှာ: {message_text}"
                            response = model.generate_content(prompt)
                            ai_answer = response.text
                            
                            # 2. Facebook ဆီ စာပြန်ပို့ခြင်း
                            send_message(sender_id, ai_answer)
                        except Exception as e:
                            print(f"Error: {e}")
    return "ok", 200

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(port=5000)
