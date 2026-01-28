import os
from groq import Groq
from flask import Flask, request
import requests
from dotenv import load_dotenv

# .env file ထဲက အချက်အလက်တွေကို load လုပ်ပါ
load_dotenv()

app = Flask(__name__)

# Groq Setup
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Facebook Configuration
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "GrowBot_Secret_123")

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
            for messaging_event in entry.get('messaging', []):
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message'].get('text')
                    
                    if message_text:
                        try:
                            # AI Model ကို စနစ်တကျ ခိုင်းစေခြင်း
                            completion = client.chat.completions.create(
                                model="llama-3.1-8b-instant", 
                                messages=[
                                    {
                                        "role": "system", 
                                        "content": """မင်းက GrowBot Agency ရဲ့ လူမှုဆက်ဆံရေးကောင်းမွန်တဲ့ AI Manager ဖြစ်ပါတယ်။ 
                                        အောက်ပါ စည်းကမ်းချက်များကို တိကျစွာလိုက်နာပါ -
                                        ၁။ မြန်မာစာကို Unicode စနစ်ဖြင့်သာ မှန်ကန်စွာ ရေးသားပါ။
                                        ၂။ စာသားများကို ယဉ်ကျေးပျူငှာပြီး ဖတ်ရလွယ်ကူအောင် စီစဉ်ပါ။ (ဥပမာ - "ဟုတ်ကဲ့ခင်ဗျာ" သို့မဟုတ် "မင်္ဂလာပါ" စသည်ဖြင့် သုံးပါ)
                                        ၃။ GrowBot Agency သည် Facebook Page များအတွက် AI Chatbot ဝန်ဆောင်မှု ပေးကြောင်း ထည့်သွင်းပြောကြားပါ။
                                        ၄။ စာလုံးပေါင်း သတ်ပုံများကို အထူးဂရုစိုက်ပါ။ ဗျည်းအက္ခရာများနှင့် အသတ်များကို စနစ်တကျ သုံးပါ။"""
                                    },
                                    {"role": "user", "content": message_text}
                                ]
                            )
                            ai_answer = completion.choices[0].message.content
                            send_message(sender_id, ai_answer)
                        except Exception as e:
                            print(f"Error: {e}")
    return "ok", 200

def send_message(recipient_id, message_text):
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post("https://graph.facebook.com/v12.0/me/messages", params=params, headers=headers, json=data)

if __name__ == "__main__":
    app.run(port=5000)
