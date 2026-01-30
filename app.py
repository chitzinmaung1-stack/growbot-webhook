import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Render မှ Environment Variables များယူခြင်း
API_KEYS = [
    os.getenv("GOOGLE_API_KEY_1"),
    os.getenv("GOOGLE_API_KEY_2")
]
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# စကားပြောမှတ်ဉာဏ်သိမ်းဆည်းရန်
chat_storage = {}

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
                sender_id = str(messaging['sender']['id'])
                if messaging.get('message'):
                    message_text = messaging['message'].get('text')
                    if message_text:
                        if sender_id not in chat_storage:
                            chat_storage[sender_id] = []
                        
                        # AI အဖြေတောင်းခြင်း (Key Rotation ပါဝင်သည်)
                        ai_answer = call_ai_with_rotation(message_text, chat_storage[sender_id])
                        
                        # History သိမ်းဆည်းခြင်း (ဝန်မပိစေရန် နောက်ဆုံး ၄ ကြောင်းသာမှတ်မည်)
                        chat_storage[sender_id].append({"role": "user", "parts": [{"text": message_text}]})
                        chat_storage[sender_id].append({"role": "model", "parts": [{"text": ai_answer}]})
                        chat_storage[sender_id] = chat_storage[sender_id][-4:]
                        
                        send_fb_message(sender_id, ai_answer)
    return "ok", 200

def call_ai_with_rotation(prompt, history):
    KNOWLEDGE_BASE = """
    မင်းက GrowBot Agency ရဲ့ Senior AI Manager ဖြစ်တယ်။
    - Services: All-in-One AI Growth (180,000 MMK), AI Video Power Pack (250,000 MMK).
    - အမြဲတမ်း ၁ ပတ် Trial ပေးနိုင်ကြောင်း ထည့်ပြောပါ။
    - Pricing မေးလျှင် Package နှစ်ခုလုံးကို အသေးစိတ်ရှင်းပြပါ။
    - မြန်မာလို ယဉ်ကျေးစွာ ဖြေကြားပေးပါ။
    """

    # API Key တစ်ခုချင်းစီကို အလှည့်ကျ စမ်းသပ်ခေါ်ယူခြင်း
    for key in API_KEYS:
        if not key: continue
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
        payload = {
            "contents": history + [{"role": "user", "parts": [{"text": f"Context: {KNOWLEDGE_BASE}\n\nCustomer: {prompt}"}]}]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=25)
            result = response.json()
            
            # Quota ပြည့်နေလျှင် (429 Error) နောက် Key တစ်ခုသို့ ကူးပြောင်းမည်
            if 'error' in result and result['error']['code'] == 429:
                continue
                
            if 'candidates' in result:
                return result['candidates'][0]['content']['parts'][0]['text']
        except:
            continue
            
    return "လူကြီးမင်း၏ မေးခွန်းအတွက် အကောင်းဆုံးဝန်ဆောင်မှုများကို ပြန်လည်စစ်ဆေးနေပါသည်၊ ခဏလေးစောင့်ပေးပါခင်ဗျာ။"

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
