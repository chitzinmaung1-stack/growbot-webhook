import os
import requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

# --- Configuration ---
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Gemini AI Setup - Model နာမည်ကို gemini-1.5-flash-8b သို့ ပြောင်းထားသည်
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-8b')

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
                    message_text = messaging_event['messaging_event']['message'].get('text')
                    
                    if message_text:
                        try:
                            # Gemini ဆီက အဖြေတောင်းခြင်း
                            prompt = f"မင်းက GrowBot Agency ရဲ့ AI Manager ပါ။ ယဉ်ကျေးစွာ စာပြန်ပေးပါ။ မေးခွန်းမှာ: {message_text}"
                            response = model.generate_content(prompt)
                            ai_answer = response.text
                            
                            # Facebook ဆီ စာပြန်ပို့ခြင်း
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
