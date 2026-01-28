import os
import google.generativeai as genai # ဒါကို သေချာ ပြန်စစ်ပါ
from flask import Flask, request
import requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Gemini Setup - အောက်ပါစာသားကို အတိအကျ ကူးပါ
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
# Gemini 1.5 Flash ကို သုံးထားပါတယ်
model = genai.GenerativeModel('gemini-1.5-flash') 

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == os.getenv("VERIFY_TOKEN"):
        return request.args.get("hub.challenge")
    return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get('object') == 'page':
        for entry in data.get('entry', []):
            # KeyError တက်ခဲ့တဲ့ messaging_event ကို ဒီမှာ ရှင်းထားပါတယ်
            for messaging in entry.get('messaging', []):
                if messaging.get('message'):
                    sender_id = messaging['sender']['id']
                    message_text = messaging['message'].get('text')
                    
                    if message_text:
                        try:
                            # Gemini ဖြင့် စာပြန်ခြင်း
                            response = model.generate_content(
                                f"မင်းက GrowBot Agency ရဲ့ အရောင်းဝန်ထမ်း ဖြစ်တယ်။ လူကြီးမင်းလို့ သုံးနှုန်းပြီး ယဉ်ကျေးစွာ မြန်မာလို ပြန်ဖြေပါ။ {message_text}"
                            )
                            ai_answer = response.text
                            send_message(sender_id, ai_answer)
                        except Exception as e:
                            print(f"Gemini Error: {e}")
    return "ok", 200

def send_message(recipient_id, message_text):
    params = {"access_token": os.getenv("PAGE_ACCESS_TOKEN")}
    data = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post("https://graph.facebook.com/v21.0/me/messages", params=params, json=data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
