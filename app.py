import os
from flask import Flask, request
import requests
from google import genai

app = Flask(__name__)

# Render Environment Variables
KEY1 = os.getenv("GOOGLE_API_KEY_1")
KEY2 = os.getenv("GOOGLE_API_KEY_2")
PAGE_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

def call_gemini(prompt):
    # Key နှစ်ခုလုံးကို အလှည့်ကျ စမ်းသပ်ခြင်း
    for k in [KEY1, KEY2]:
        if not k: continue
        try:
            client = genai.Client(api_key=k)
            # Gemini 2.5 Flash ကို တိုက်ရိုက်ခေါ်ယူခြင်း
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )
            if response.text:
                return response.text
        except Exception as e:
            # Quota ပြည့်လျှင် နောက် Key ကို ကူးမည်
            if "429" in str(e) or "quota" in str(e).lower():
                continue
            return f"⚠️ API Error: {str(e)}"
    
    return "ဝန်ဆောင်မှုများ ခေတ္တပြည့်နှက်နေပါသည်၊ ခဏလေးစောင့်ပေးပါခင်ဗျာ။"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get('object') == 'page':
        for entry in data.get('entry', []):
            for messaging in entry.get('messaging', []):
                sender_id = messaging['sender']['id']
                if messaging.get('message'):
                    msg = messaging['message'].get('text')
                    if msg:
                        reply = call_gemini(msg)
                        send_fb(sender_id, reply)
    return "ok", 200

def send_fb(uid, txt):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_TOKEN}"
    requests.post(url, json={"recipient": {"id": uid}, "message": {"text": txt}})

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Failed", 403

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
