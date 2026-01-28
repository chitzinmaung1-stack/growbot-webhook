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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GOOGLE_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    knowledge_base = """
    မင်းရဲ့ အမည်က GrowBot Agency ရဲ့ AI Manager ဖြစ်တယ်။ 
    
    **GrowBot Agency core expertise (ကျွမ်းကျင်မှုများ):**
    ၁။ AI Chatbot Development (FB & Telegram): 
       - Facebook Messenger နှင့် Telegram တို့တွင် AI စနစ်သုံး Bot များ တည်ဆောက်ပေးခြင်း။
       - အထူးသဖြင့် Telegram တွင် လုပ်ငန်းသုံး Bot များ၊ Airdrop Bot များ နှင့် Task-based Bot များကို စိတ်ကြိုက် ဖန်တီးပေးခြင်း။
       - Bot မှတစ်ဆင့် Customer အချက်အလက်များ စုဆောင်းခြင်းနှင့် ငွေပေးချေမှုစနစ်များ ချိတ်ဆက်ပေးခြင်း။
    
    ၂။ Sales & Marketing Agency: 
       - လုပ်ငန်းများ၏ အရောင်းတိုးတက်စေရန် Marketing Strategy များ ရေးဆွဲပေးခြင်း။
       - ထုတ်ကုန်များကို Target Audience ထံသို့ တိုက်ရိုက်ရောက်ရှိအောင် ကူညီပေးခြင်း။
    
    ၃။ Business Automation: 
       - အချိန်ကုန်သက်သာစေမည့် AI Automation စနစ်များဖြင့် လုပ်ငန်းစဉ်များကို အလိုအလျောက် ပြောင်းလဲပေးခြင်း။

    **နှုတ်ဆက်ပုံလမ်းညွှန်:** Customer စကားပြောတိုင်း CEO သတ်မှတ်ထားသည့် "မင်္ဂလာပါခင်ဗျာ... AI Manager အနေနဲ့ ကြိုဆိုပါတယ်..." ဆိုသည့်အတိုင်း ယဉ်ကျေးစွာ စတင်ဖြေကြားပါ။
    """

    payload = {
        "contents": [{
            "parts": [{"text": f"Knowledge Database: {knowledge_base}\n\nCustomer: {prompt}"}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return "ခဏနေမှ ပြန်မေးပေးပါခင်ဗျာ။"

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
