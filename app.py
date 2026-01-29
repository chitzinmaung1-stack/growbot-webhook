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
                            ai_answer = call_gemini_2_flash(message_text)
                            send_fb_message(sender_id, ai_answer)
                        except Exception as e:
                            # Error ဖြစ်ရင် logs မှာ အတိအကျကြည့်လို့ရအောင် လုပ်ထားပါတယ်
                            print(f"Deployment Error: {e}")
                            send_fb_message(sender_id, "စနစ်ကို ခေတ္တစစ်ဆေးနေပါတယ်ခင်ဗျာ။")
    return "ok", 200

def call_gemini_2_flash(prompt):
    # Gemini 2.0 Flash Model URL (Beta endpoint)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GOOGLE_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    system_instruction = "You are GrowBot AI Manager. Be smart, concise, and professional in Burmese. Database: 1.Chatbots, 2.Strategy, 3.Automation, 4.Special Agent 2."
    
    payload = {
        "contents": [{
            "parts": [{"text": f"System: {system_instruction}\nCustomer: {prompt}"}]
        }]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    # API ကနေ အဖြေပြန်လာတဲ့ပုံစံကို သေချာစစ်ဆေးဖတ်ယူခြင်း
    try:
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"API Response Error: {result}")
            return "လူကြီးမင်း မေးခွန်းကို ကျွန်တော် နားလည်အောင် ကြိုးစားနေပါတယ်ခင်ဗျာ။"
    except (KeyError, IndexError):
        return "ဝန်ဆောင်မှုများအကြောင်း သိလိုပါက တစ်ချက်လောက် ထပ်မေးပေးပါခင်ဗျာ။"

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
