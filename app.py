import os
import google.generativeai as genai
from flask import Flask, request
import requests

app = Flask(__name__)

# Render မှ တိကျသော နာမည်များဖြင့် ဆွဲယူခြင်း
KEYS = [os.getenv("GOOGLE_API_KEY_1"), os.getenv("GOOGLE_API_KEY_2")]
PAGE_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

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
                        # 2.0 Flash SDK ဖြင့် တိုက်ရိုက်ခေါ်ယူခြင်း
                        reply = call_gemini_2_0(msg)
                        send_fb(sender_id, reply)
    return "ok", 200

def call_gemini_2_0(prompt):
    # GrowBot Agency မူလ Knowledge Base
    KNOWLEDGE = "မင်းက GrowBot Agency ရဲ့ Senior AI Manager ဖြစ်တယ်။ ဝန်ဆောင်မှုများကို ယဉ်ကျေးစွာ ရှင်းပြပါ။"
    
    for k in KEYS:
        if not k: continue
        try:
            genai.configure(api_key=k)
            # URL မလိုဘဲ SDK ဖြင့် တိုက်ရိုက်ချိတ်ဆက်ခြင်း
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(f"{KNOWLEDGE}\nCustomer: {prompt}")
            return response.text
        except Exception as e:
            # Quota ပြည့်ပါက နောက် Key သို့ ကူးပြောင်းမည်
            if "429" in str(e) or "quota" in str(e).lower():
                continue
            return f"⚠️ System Note: {str(e)}"

    return "ဝန်ဆောင်မှုများ ခေတ္တပြည့်နှက်နေပါသည်၊ ၅ မိနစ်ခန့်အကြာမှ ပြန်မေးပေးပါခင်ဗျာ။"

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
