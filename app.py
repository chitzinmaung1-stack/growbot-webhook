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
    # CEO စမ်းသပ်အောင်မြင်ခဲ့သော gemini-2.0-flash-exp ကို အသုံးပြုထားပါသည်
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GOOGLE_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    knowledge_base = """
    မင်းရဲ့ အမည်က GrowBot Agency ရဲ့ AI Manager ဖြစ်တယ်။ 
    မင်းရဲ့ တာဝန်က GrowBot Agency ရဲ့ ဝန်ဆောင်မှုတွေကို စိတ်ဝင်စားတဲ့ Customer တွေကို ယဉ်ကျေးစွာ ဖြေကြားပေးဖို့ ဖြစ်တယ်။
    
    **နှုတ်ဆက်ပုံလမ်းညွှန်:** Customer က "မင်္ဂလာပါ" လို့ စတင်နှုတ်ဆက်ရင် ဖြစ်စေ၊ စကားစပြောရင်ဖြစ်စေ အောက်ပါအတိုင်း အမြဲနှုတ်ဆက်ပါ။
    "မင်္ဂလာပါခင်ဗျာ။ GrowBot Agency ရဲ့ AI Manager အနေနဲ့ ကြိုဆိုပါတယ်ခင်ဗျာ။ ကျွန်တော်တို့ GrowBot Agency က AI နည်းပညာတွေကို အသုံးပြုပြီး စီးပွားရေးလုပ်ငန်းတွေ တိုးတက်အောင် ကူညီပေးနေပါတယ်ခင်ဗျာ။ ဘယ်လိုများ ကူညီပေးရမလဲဆိုတာ ပြောပြပေးနိုင်ပါတယ်ခင်ဗျ။"

    **GrowBot Agency Knowledge Database:**
    ၁။ ကျွန်တော်တို့က လုပ်ငန်းတွေအတွက် AI Chatbot (Facebook, Telegram) တွေ တည်ဆောက်ပေးပါတယ်။
    ၂။ Sales & Marketing Agency အနေနဲ့ လုပ်ငန်းတွေရဲ့ အရောင်းတိုးတက်အောင် ကူညီပေးပါတယ်။
    ၃။ လုပ်ငန်းရှင်တွေ အချိန်ကုန်သက်သာစေဖို့ လုပ်ငန်းစဉ်တွေကို AI နဲ့ Automation လုပ်ပေးပါတယ်။
    
    အမြဲတမ်း 'ခင်ဗျာ' သုံးပြီး ယဉ်ကျေးစွာ ဖြေကြားပေးပါ။
    """

    payload = {
        "contents": [{
            "parts": [{"text": f"{knowledge_base}\n\nCustomer Question: {prompt}"}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        if 'candidates' in result and result['candidates']:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # 404 ပြန်တက်ရင် Logs မှာ အတိအကျ မြင်ရအောင် ထုတ်ထားပါတယ်
            print(f"DEBUG - Full Response: {result}")
            return "ခဏနေမှ ပြန်မေးပေးပါခင်ဗျာ။"
    except Exception as e:
        print(f"Request Error: {e}")
        return "ခဏနေမှ ပြန်မေးပေးပါခင်ဗျာ။"

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
