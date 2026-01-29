import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

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
            for messaging in entry.get('messaging', []):
                sender_id = messaging['sender']['id']
                if messaging.get('message'):
                    message_text = messaging['message'].get('text')
                    if message_text:
                        try:
                            # အမည်ကို call_gemini_3_flash ဟု တိကျစွာ ပြောင်းလဲထားသည်
                            ai_answer = call_gemini_3_flash(message_text)
                            send_fb_message(sender_id, ai_answer)
                        except Exception as e:
                            print(f"Server Error: {e}")
                            send_fb_message(sender_id, "စနစ်ကို ခေတ္တစစ်ဆေးနေပါတယ်ခင်ဗျာ။")
    return "ok", 200

def call_gemini_3_flash(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GOOGLE_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    KNOWLEDGE_DATABASE = """
    GrowBot Agency ဝန်ဆောင်မှုများ-
    ၁။ AI Chatbots (FB/Telegram)
    ၂။ Marketing Strategy
    ၃။ Business Automation
    ၄။ Special Content Agent 2 (Auto FB Posting)
    """

    system_instruction = f"You are the Senior AI Manager of GrowBot. Use this DB to answer: {KNOWLEDGE_DATABASE}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"System: {system_instruction}\nCustomer: {prompt}"}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        result = response.json()
        
        if 'candidates' in result:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"API Error: {result}")
            return "လူကြီးမင်း မေးခွန်းကို အမြန်ဆုံး နားလည်အောင် ကြိုးစားနေပါတယ်ခင်ဗျာ။"
    except Exception as e:
        print(f"API Connection Error: {e}")
        return "ခေတ္တစောင့်ပေးပါ၊ စနစ်ကို ပြန်လည်စစ်ဆေးနေပါတယ်။"

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
