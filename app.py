import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Environment Variables များကို စစ်ဆေးခြင်း
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
                if messaging.get('message'):
                    sender_id = messaging['sender']['id']
                    message_text = messaging['message'].get('text')
                    
                    if message_text:
                        # Gemini ဆီသို့ တိုက်ရိုက် API ခေါ်ယူခြင်း
                        ai_answer = call_gemini_direct(message_text)
                        send_fb_message(sender_id, ai_answer)
    return "ok", 200

def call_gemini_direct(prompt):
    # Model ID ကို -latest ထည့်ပြီး အပြည့်အစုံ ပြောင်းထားပါတယ်
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GOOGLE_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"မင်းက GrowBot Agency ရဲ့ အရောင်းဝန်ထမ်း ဖြစ်တယ်။ လူကြီးမင်းလို့ သုံးနှုန်းပြီး ယဉ်ကျေးစွာ မြန်မာလို ပြန်ဖြေပါ။ {prompt}"}]
        }]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        if 'candidates' in result and result['candidates']:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # Error တက်ရင် API Key ကြောင့်လား၊ Model ကြောင့်လားဆိုတာ ဒီမှာ အဖြေပေါ်ပါလိမ့်မယ်
            print(f"Gemini API Response Error: {result}")
            return "ခဏနေမှ ပြန်မေးပေးပါခင်ဗျာ။"
    except Exception as e:
        print(f"Connection Error: {e}")
        return "ခဏနေမှ ပြန်မေးပေးပါခင်ဗျာ။"

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
