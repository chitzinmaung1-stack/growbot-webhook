import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

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
                        
                        # Timeout ကို ၃၀ စက္ကန့်အထိ တိုးမြှင့်ထားသည်
                        ai_answer = call_senior_ai_manager(message_text, chat_storage[sender_id])
                        
                        chat_storage[sender_id].append({"role": "user", "parts": [{"text": message_text}]})
                        chat_storage[sender_id].append({"role": "model", "parts": [{"text": ai_answer}]})
                        chat_storage[sender_id] = chat_storage[sender_id][-4:] # History ကို ပိုလျှော့ပြီး load လျှော့ချသည်
                        
                        send_fb_message(sender_id, ai_answer)
    return "ok", 200

def call_senior_ai_manager(prompt, history):
    # Gemini 2.5 Flash (Stable URL)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GOOGLE_API_KEY}"
    
    KNOWLEDGE_BASE = """
    မင်းက GrowBot Agency ရဲ့ Senior Manager ဖြစ်တယ်။
    - မေးခွန်းတွေအများကြီးမေးလာရင် တိုတိုနဲ့ ရှင်းရှင်း တစ်ခုချင်းစီ ခွဲဖြေပေးပါ။
    - Services: All-in-One (180,000 MMK), AI Video (250,000 MMK). 
    - ၁ ပတ် Trial ပေးနိုင်ကြောင်း သေချာထည့်ပြောပါ။
    - Pricing မေးလာရင် ချက်ချင်း Package ဈေးနှုန်းတွေကို ချပြပါ။
    - Myanmar FB Boost အောင်မြင်မှုကို ယုံကြည်မှုအတွက် သုံးပါ။
    """

    payload = {
        "contents": history + [{"role": "user", "parts": [{"text": f"Context: {KNOWLEDGE_BASE}\n\nCustomer Message: {prompt}"}]}]
    }
    
    try:
        # Timeout ကို ၂၅ စက္ကန့်အထိ ပေးထားသည်
        response = requests.post(url, json=payload, timeout=25)
        result = response.json()
        if 'candidates' in result:
            return result['candidates'][0]['content']['parts'][0]['text']
        return "လူကြီးမင်း၏ မေးခွန်းများအတွက် အသေးစိတ် ဈေးနှုန်းနှင့် ဝန်ဆောင်မှုများကို ပြန်လည်တွက်ချက်နေပါသည်၊ ခဏလေး စောင့်ပေးပါခင်ဗျာ။"
    except Exception as e:
        print(f"Server Error: {e}")
        return "စနစ်ကို ခေတ္တ စစ်ဆေးနေပါသည်၊ ၁ မိနစ်ခန့်အကြာမှ ပြန်လည် ပေးပို့ပေးပါခင်ဗျာ။"

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
