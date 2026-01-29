import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# စကားပြောမှတ်ဉာဏ်ကို user_id အလိုက် စနစ်တကျ သိမ်းဆည်းမည်
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
                sender_id = str(messaging['sender']['id']) # ID ကို String အဖြစ် အသေအချာပြောင်းပါ
                if messaging.get('message'):
                    message_text = messaging['message'].get('text')
                    if message_text:
                        try:
                            # User တဦးချင်းစီ၏ history ကို ခေါ်ယူခြင်း
                            if sender_id not in chat_history:
                                chat_history[sender_id] = []
                            
                            current_history = chat_history[sender_id]
                            ai_answer = call_senior_ai_manager(message_text, current_history)
                            
                            # History update (နောက်ဆုံး အသွားအပြန် ၂ ကြိမ်သာမှတ်မည် - Error နည်းရန်)
                            current_history.append({"role": "user", "parts": [{"text": message_text}]})
                            current_history.append({"role": "model", "parts": [{"text": ai_answer}]})
                            chat_history[sender_id] = current_history[-4:] 
                            
                            send_fb_message(sender_id, ai_answer)
                        except Exception as e:
                            print(f"Server Error Log: {e}")
                            # Error ဖြစ်လျှင်ပင် customer စောင့်မနေရအောင် အခြေခံအဖြေတခုပေးခြင်း
                            fallback_msg = "မင်္ဂလာပါခင်ဗျာ၊ လူကြီးမင်း၏ မေးမြန်းမှုကို Senior Manager ထံသို့ လွှဲပြောင်းပေးနေပါသည်၊ ခေတ္တစောင့်ပေးပါခင်ဗျာ။"
                            send_fb_message(sender_id, fallback_msg)
    return "ok", 200

def call_senior_ai_manager(prompt, history):
    # Gemini 3 Flash URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GOOGLE_API_KEY}"
    
    KNOWLEDGE_DB = """
    ROLE: Senior AI Strategy Consultant of GrowBot Agency.
    TONE: Professional & Strategic.
    SERVICES: 
    1. All-in-One (180,000 MMK) - Content & Chatbot focus.
    2. Video Power Pack (250,000 MMK) - AI Video focus.
    SPECIAL: 1 Week Trial, Myanmar FB Boost Success Case.
    """

    # Payload format ကို ပိုမိုခိုင်မာအောင် ပြင်ဆင်ခြင်း
    payload = {
        "contents": history + [{"role": "user", "parts": [{"text": f"Context: {KNOWLEDGE_DB}\n\nCustomer: {prompt}"}]}]
    }
    
    response = requests.post(url, json=payload, timeout=20)
    result = response.json()
    
    if 'candidates' in result and len(result['candidates']) > 0:
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        print(f"Detailed API Response: {result}")
        return "လူကြီးမင်း၏ လုပ်ငန်းအတွက် အဆီလျော်ဆုံး ဗျူဟာကို စဉ်းစားပေးနေပါသည်၊ ခဏလေး စောင့်ပေးပါခင်ဗျာ။"

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
