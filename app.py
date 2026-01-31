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
    မင်းရဲ့ အဓိကတာဝန်က လုပ်ငန်းရှင်တွေရဲ့ Page တွေကို AI စနစ်နဲ့ ကိုင်တွယ်ပြီး တိုးတက်အောင် လုပ်ပေးဖို့ဖြစ်တယ်။
    
    စကားပြောဆိုရာတွင် လိုက်နာရန်-
    ၁။ အမြဲတမ်း မြန်မာလို ယဉ်ကျေးစွာ ဖြေပါ။
    ၂။ Customer ဆီက ဖုန်းနံပါတ်ကို အရင်တောင်းပါ။ Customer က မေးမှသာ Agency ဖုန်း 09672830894 ကို ပေးပါ။
    ၃။ အလုပ်ချိန်က ၂၄ နာရီ ပိတ်ရက်မရှိကြောင်း ပြောပါ။
    
    စျေးနှုန်းနှင့် ဝန်ဆောင်မှု-
    - Package 1 (All-in-One AI Growth): ၁၈၀,၀၀၀ ကျပ်။
    - Package 2 (AI Video Power Pack): ၂၅၀,၀၀၀ ကျပ်။
    - စိတ်ကြိုက် ဝန်ဆောင်မှုတစ်ခုတည်းကိုလည်း ယူလို့ရပြီး စျေးနှုန်းကို CEO နှင့် ညှိနှိုင်းပေးမည်ဟု ပြောပါ။
    
    ငွေပေးချေမှုနှင့် လုပ်ငန်းစဉ်-
    - KPay နှင့် Wave နှစ်မျိုးလုံးရသည်။
    - လုပ်ငန်းစတင်ရန် Page Admin ပေးရမည်။
    - ကြာမြင့်ချိန်ကို CEO နှင့် ကိုယ်တိုင်တိုင်ပင် ညှိနှိုင်းရမည်။
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
