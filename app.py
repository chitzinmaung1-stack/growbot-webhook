import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Environment Variables (Render တွင် ဖြည့်သွင်းရန်)
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
                
                # ၁။ Get Started Button သို့မဟုတ် ခလုတ်များကို နှိပ်ခြင်းကို စစ်ဆေးခြင်း
                if messaging.get("postback"):
                    payload = messaging["postback"].get("payload")
                    if payload == "GET_STARTED_PAYLOAD":
                        welcome_text = "မင်္ဂလာပါ CEO ခင်ဗျာ။ GrowBot Agency ရဲ့ AI Manager အဖြစ် ကြိုဆိုပါတယ်။ လူကြီးမင်းကို ဘယ်လိုကူညီပေးရမလဲခင်ဗျာ?"
                        send_fb_message(sender_id, welcome_text)
                
                # ၂။ ပုံမှန် စာသားပေးပို့မှုကို စစ်ဆေးခြင်း
                elif messaging.get('message'):
                    message_text = messaging['message'].get('text')
                    if message_text:
                        ai_answer = call_gemini_direct(message_text)
                        send_fb_message(sender_id, ai_answer)
                        
    return "ok", 200

def call_gemini_direct(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GOOGLE_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    system_instruction = """
    You are the AI Manager of GrowBot Agency. Answer in Burmese.
    Keep it natural, professional, and short. Use polite particles like 'ခင်ဗျာ'.
    Only share specific business details from the database if relevant to the question.
    KNOWLEDGE: AI Chatbots (FB/Telegram), Marketing Strategy, Automation, Special Content Agent 2.
    """

    payload = {
        "contents": [{
            "parts": [{"text": f"Instruction: {system_instruction}\n\nCustomer: {prompt}\n\nAI Manager's Reply:"}]
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
