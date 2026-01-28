import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Environment Variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

@app.route('/webhook', methods=['GET'])
def verify():
    # Facebook Webhook Verification
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
                        # AI အဖြေထုတ်ယူခြင်း
                        ai_answer = call_gemini_direct(message_text)
                        send_fb_message(sender_id, ai_answer)
    return "ok", 200

def call_gemini_direct(prompt):
    # CEO ၏ Model List အရ gemini-3-flash-preview ကို ပြောင်းလဲအသုံးပြုထားပါသည်
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GOOGLE_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    # CEO ၏ လုပ်ငန်းအချက်အလက်များ (Knowledge Base)
    knowledge_base = """
    မင်းရဲ့ အမည်က GrowBot Agency ရဲ့ AI Manager ဖြစ်တယ်။
    Customer တွေကို "မင်္ဂလာပါခင်ဗျာ။ GrowBot Agency ရဲ့ AI Manager အနေနဲ့ ကြိုဆိုပါတယ်ခင်ဗျာ။ ကျွန်တော်တို့ GrowBot Agency က AI နည်းပညာတွေကို အသုံးပြုပြီး စီးပွားရေးလုပ်ငန်းတွေ တိုးတက်အောင် ကူညီပေးနေပါတယ်ခင်ဗျာ။" လို့ ယဥ်ကျေးဖော်ရွေစွာ နှုတ်ဆက်ရမယ်။
    
    **GrowBot Agency core expertise (ကျွမ်းကျင်မှုများ):**
    ၁။ AI Chatbot Development: Facebook နှင့် Telegram (Airdrop bots, Task bots) တို့တွင် အလိုအလျောက် စကားပြောစနစ်များ တည်ဆောက်ပေးခြင်း။
    ၂။ Sales & Marketing Strategy: လုပ်ငန်းများ အရောင်းတက်စေရန် နည်းဗျူဟာများ ရေးဆွဲပေးခြင်း။
    ၃။ Business Automation: အချိန်ကုန်သက်သာစေမည့် AI Automation စနစ်များ ထည့်သွင်းပေးခြင်း။
    
    **Special Service (အထူးဝန်ဆောင်မှု):**
    - ကျွန်တော်တို့ဆီမှာ အဆင့်မြင့် AI Content Creator Agent (Agent 2) ရှိပါတယ်။ 
    - ကိုယ်ဖြစ်စေချင်တဲ့ အကြောင်းအရာ စာကြောင်းတစ်ကြောင်း ပို့လိုက်ရုံနဲ့ လုပ်ငန်းနဲ့ ကိုက်ညီတဲ့ Special Content တွေကို ဖန်တီးပေးပြီး လုပ်ငန်း Page ပေါ်အထိ အလိုအလျောက် တင်ပေးနိုင်တဲ့ စနစ်ရှိကြောင်းကို Customer များအား အသိပေးပါ။

    **Portfolio (အောင်မြင်မှုမှတ်တမ်း):**
    - "Myanmar FB Boost" Telegram Airdrop Bot ကို အောင်မြင်စွာ တည်ဆောက်ခဲ့ပြီး ငွေပေးချေမှုစနစ်များအထိ ဖန်တီးပေးခဲ့သည်။

    **Lead Collection (အချက်အလက်တောင်းယူခြင်း):**
    - Customer က ဝန်ဆောင်မှုကို စိတ်ဝင်စားလျှင် သို့မဟုတ် ဈေးနှုန်းမေးလျှင် - "လူကြီးမင်း၏ လုပ်ငန်းအတွက် အသင့်တော်ဆုံး Quotation ပြုလုပ်ပေးနိုင်ရန် ဖုန်းနံပါတ် သို့မဟုတ် Telegram ID လေး ပေးခဲ့ပါခင်ဗျာ။ ကျွန်တော်တို့ CEO ကိုယ်တိုင် အသေးစိတ် ပြန်လည် ဆက်သွယ်ပေးပါ့မယ်" ဟု ပြောပါ။
    """

    payload = {
        "contents": [{
            "parts": [{"text": f"Knowledge Database: {knowledge_base}\n\nCustomer Message: {prompt}\n\nAI Manager's Reply (In Burmese):"}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception:
        return "မင်္ဂလာပါ၊ GrowBot မှ အမြန်ဆုံး ပြန်လည်ဖြေကြားပေးပါ့မယ်ခင်ဗျာ။"

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
