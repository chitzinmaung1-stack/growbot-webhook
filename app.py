import os
import requests
from flask import Flask, request
from dotenv import load_dotenv
import google.generativeai as genai

# .env file ထဲက အချက်အလက်တွေကို load လုပ်ပါ
load_dotenv()

app = Flask(__name__)

# --- Configuration (လုံုံခြုံရေးအတွက် Environment Variables မှတစ်ဆင့်ခေါ်ယူခြင်း) ---
# .env file ထဲမှာ သိမ်းဆည်းထားရမည့် အချက်အလက်များ
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "GrowBot_Secret_123")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini AI Setup - သင်သုံးချင်တဲ့ 2.0 Flash Version ကို ထည့်ပေးထားပါတယ်
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

@app.route('/webhook', methods=['GET'])
def verify():
    # Verification token ကို စစ်ဆေးခြင်း
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get('object') == 'page':
        for entry in data.get('entry', []):
            for messaging_event in entry.get('messaging', []):
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message'].get('text')
                    
                    if message_text:
                        try:
                            # Gemini AI ဆီက အဖြေတောင်းခြင်း
                            # System Prompt ကို ပိုကောင်းအောင် ပြင်ထားပါတယ်
                            response = model.generate_content(
                                f"မင်းက GrowBot Agency ရဲ့ AI Manager ပါ။ ယဉ်ကျေးစွာ စာပြန်ပေးပါ။ Customer မေးခွန်း: {message_text}"
                            )
                            ai_answer = response.text
                            
                            # Facebook Messenger ဆီ စာပြန်ပို့ခြင်း
                            send_message(sender_id, ai_answer)
                        except Exception as e:
                            print(f"Error in Gemini: {e}")
    return "ok", 200

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Error sending message: {response.text}")

if __name__ == '__main__':
    app.run(port=5000, debug=True)
