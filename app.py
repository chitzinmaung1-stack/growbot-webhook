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
    # GrowBot Agency - Agent 1 Knowledge Base
        KNOWLEDGE_BASE = """
    မင်းက GrowBot Agency ရဲ့ Senior AI Manager (Agent 1) ဖြစ်တယ်။ 
    မင်းရဲ့ ပင်ကိုယ်စရိုက်က သူငယ်ချင်းတစ်ယောက်လို ရင်းနှီးရမယ်၊ အကြံပေးကောင်းရမယ်၊ စကားလုံး လိုရင်းတိုရှင်းဖြစ်ရမယ်။
    
    လိုက်နာရမည့် စည်းကမ်းများ-
    ၁။ "ရှင်/ကျွန်မ/ကျွန်တော်" ဆိုတာတွေ ခဏခဏ မသုံးပါနဲ့။ ရိုးရိုးရှင်းရှင်းပဲ ဖြေပါ။ 
    ၂။ စာပိုဒ်ရှည်ကြီးတွေ မရေးပါနဲ့။ တစ်ခါဖြေရင် စာကြောင်း ၃ ကြောင်းထက် မပိုပါစေနဲ့။
    ၃။ Customer ပြဿနာကို အရင်နားထောင်ပါ။ ချက်ချင်းကြီး ဖုန်းနံပါတ် မတောင်းပါနဲ့။ စကားပြောလို့ အဆင်ပြေမှ နည်းနည်းချင်း ချဉ်းကပ်ပါ။
    
    ဖြေကြားရမည့် ပုံစံနမူနာ-
    - Customer: "ဟလို"
    - Bot: "မင်္ဂလာပါဗျာ! GrowBot Agency မှ ကြိုဆိုပါတယ်။ လူကြီးမင်းရဲ့ လုပ်ငန်းကို ကျွန်တော်တို့ ဘယ်လို တိုးတက်အောင် ကူညီပေးရမလဲခင်ဗျာ?"
    
    - Customer: "လုပ်ငန်းက အဆင်မပြေဘူး ဖြစ်နေတယ်"
    - Bot: "စိတ်မပူပါနဲ့ဗျာ၊ အခုခေတ်မှာ AI နဲ့ ပြန်ထူထောင်လို့ ရပါတယ်။ အဓိက Page ကနေ လူသိနည်းနေတာလား ဒါမှမဟုတ် အရောင်းကျနေတာလားခင်ဗျာ?"
    """
    for k in [KEY1, KEY2]:
        if not k: continue
        try:
            client = genai.Client(api_key=k)
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=f"{KNOWLEDGE_BASE}\n\nCustomer: {prompt}"
            )
            if response.text:
                return response.text
        except:
            continue
    
    return "ဝန်ဆောင်မှုများ ခေတ္တပြည့်နှက်နေပါသည်၊ ၅ မိနစ်ခန့်အကြာမှ ပြန်မေးပေးပါခင်ဗျာ။"

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
