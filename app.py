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
                        # Memory မပါဘဲ တိုက်ရိုက်ခေါ်ယူပြီး Loop ကို ဖြတ်တောက်သည်
                        ai_answer = call_gemini_clean(message_text)
                        send_fb_message(sender_id, ai_answer)
    return "ok", 200

def call_gemini_clean(prompt):
    # CEO ပြောသည့်အတိုင်း 2.5 flash ကို သုံးထားသည်
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GOOGLE_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    knowledge_base = "မင်းက GrowBot Agency ရဲ့ Senior Manager ဖြစ်တယ်။ အမြဲတမ်း ယဉ်ကျေးစွာ ဖြေကြားပေးပါ။"

    payload = {
        "contents": [{"parts": [{"text": f"{knowledge_base}\n\nCustomer: {prompt}"}]}]
    }
    
    try:
        # Timeout ကို အများဆုံး ၅၀ စက္ကန့်အထိ ပေးထားသည်
        response = requests.post(url, headers=headers, json=payload, timeout=50)
        result = response.json()
        if 'candidates' in result:
            return result['candidates'][0]['content']['parts'][0]['text']
        return "ဝန်ဆောင်မှုများကို ပြန်လည်စစ်ဆေးနေပါသည်၊ ခေတ္တစောင့်ပေးပါခင်ဗျာ။"
    except:
        return "စနစ်အား အဆင့်မြှင့်တင်နေပါသည်၊ ခဏနေမှ ပြန်မေးပေးပါခင်ဗျာ။"

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
