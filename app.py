import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# User အလိုက် စကားပြောမှတ်ဉာဏ် သိမ်းဆည်းရန်
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
                        
                        # AI အဖြေတောင်းခြင်း (History ပါဝင်သည်)
                        ai_answer = call_senior_ai_manager(message_text, chat_storage[sender_id])
                        
                        # History သိမ်းဆည်းခြင်း
                        chat_storage[sender_id].append({"role": "user", "parts": [{"text": message_text}]})
                        chat_storage[sender_id].append({"role": "model", "parts": [{"text": ai_answer}]})
                        chat_storage[sender_id] = chat_storage[sender_id][-6:] # နောက်ဆုံး ၃ ကြိမ်အသွားအပြန်မှတ်မည်
                        
                        send_fb_message(sender_id, ai_answer)
    return "ok", 200

def call_senior_ai_manager(prompt, history):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GOOGLE_API_KEY}"
    
    KNOWLEDGE_BASE = """
    မင်းက GrowBot Agency ရဲ့ Senior AI Manager ဖြစ်တယ်။ 
    - Customer က မင်္ဂလာပါလို့ စနှုတ်ဆက်မှသာ အပြည့်အစုံ နှုတ်ဆက်ပါ။ စကားဝိုင်းထဲ ရောက်နေရင် ထပ်မနှုတ်ဆက်ပါနဲ့။
    - Customer ပြောတာတွေကို သေချာမှတ်သားပြီး အဖြေပေးပါ။ (Memory ပါဝင်သည်)
    - Services: All-in-One (180,000 MMK), AI Video (250,000 MMK).
    - Myanmar FB Boost project မှာ AI နဲ့ အောင်မြင်ခဲ့ဖူးကြောင်း ထည့်ပြောပါ။
    """

    payload = {
        "contents": history + [{"role": "user", "parts": [{"text": f"Context: {KNOWLEDGE_BASE}\n\nCustomer: {prompt}"}]}]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=25)
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except:
        return "ခေတ္တစောင့်ပေးပါခင်ဗျာ၊ အကောင်းဆုံးဗျူဟာကို စဉ်းစားနေလို့ပါခင်ဗျာ။"

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
