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
                if messaging.get('message'):
                    sender_id = messaging['sender']['id']
                    message_text = messaging['message'].get('text')
                    if message_text:
                        ai_answer = call_gemini_direct(message_text)
                        send_fb_message(sender_id, ai_answer)
    return "ok", 200

def call_gemini_direct(prompt):
    # CEO ၏ Gemini 3 Flash Preview ကို အသုံးပြုခြင်း
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GOOGLE_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    # ဤနေရာတွင် AI ကို ညွှန်ကြားချက် ပြောင်းလဲထားပါသည်
    system_instruction = """
    You are the AI Manager of GrowBot Agency. 
    Your goal is to have a natural, helpful, and professional conversation in Burmese.
    
    IMPORTANT RULES:
    1. Do NOT repeat the whole database in one reply. 
    2. Only answer based on what the customer asks using the knowledge provided.
    3. Keep answers short, engaging, and friendly (use Burmese polite particles like 'ခင်ဗျာ').
    4. If they just say 'Hello', just greet them warmly and ask how you can help.
    
    KNOWLEDGE BASE:
    - Services: AI Chatbots (FB/Telegram), Sales & Marketing Strategy, Business Automation.
    - Special Agent 2: Can auto-generate and post marketing content to FB page from just one sentence.
    - Portfolio: Myanmar FB Boost (Telegram Airdrop Bot with payment system).
    - If interested: Ask for Phone number/Telegram ID for CEO to contact back.
    """

    payload = {
        "contents": [{
            "parts": [{"text": f"Instruction: {system_instruction}\n\nCustomer: {prompt}\n\nAI Manager's Response:"}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except:
        return "မင်္ဂလာပါ၊ GrowBot Agency မှ ကူညီရန် အသင့်ရှိနေပါတယ်ခင်ဗျာ။"

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
