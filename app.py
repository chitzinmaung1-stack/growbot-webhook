import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# စကားပြောမှတ်ဉာဏ်ကို ပိုမိုသန့်ရှင်းအောင် ထိန်းသိမ်းမည်
chat_history = {}

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
                            # Memory ကို ယူပြီး ရှင်းလင်းစွာ ပေးပို့မည်
                            history = chat_history.get(sender_id, [])
                            ai_answer = call_senior_ai_manager(message_text, history)
                            
                            # History ကို update လုပ်ပါ (နောက်ဆုံး အပြန်အလှန် ၃ ကြိမ်သာ မှတ်မည် - Error ကင်းရန်)
                            history.append({"role": "user", "parts": [{"text": message_text}]})
                            history.append({"role": "model", "parts": [{"text": ai_answer}]})
                            chat_history[sender_id] = history[-6:] 
                            
                            send_fb_message(sender_id, ai_answer)
                        except Exception as e:
                            print(f"Detail Error: {e}")
                            send_fb_message(sender_id, "လူကြီးမင်း၏ မေးခွန်းကို အသေချာဆုံး အဖြေပေးနိုင်ရန် စနစ်ကို ပြန်လည်ညှိနှိုင်းနေပါသည်၊ ခေတ္တစောင့်ပေးပါခင်ဗျာ။")
    return "ok", 200

def call_senior_ai_manager(prompt, history):
    # Gemini 3 Flash Preview URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GOOGLE_API_KEY}"
    
    KNOWLEDGE_DB = """
    ROLE: Senior AI Strategy Consultant of GrowBot Agency.
    TONE: Professional & Strategic.
    SERVICES: 
    1. All-in-One (180,000 MMK) - Chatbot focus.
    2. Video Power Pack (250,000 MMK) - AI Video focus.
    SPECIAL: 1 Week Trial, Myanmar FB Boost Success Case.
    """

    # Payload ကို ပိုမို တည်ငြိမ်သော Format သို့ ပြောင်းလဲခြင်း
    payload = {
        "contents": history + [{"role": "user", "parts": [{"text": f"Context: {KNOWLEDGE_DB}\n\nCustomer Message: {prompt}"}]}]
    }
    
    response = requests.post(url, json=payload, timeout=20)
    result = response.json()
    
    if 'candidates' in result:
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        # API ဘက်က error ပြလာရင် logs မှာ အတိအကျပြရန်
        print(f"API Detailed Error: {result}")
        raise Exception("API Response Error")

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
