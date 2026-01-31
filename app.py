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
    # အရင် Knowledge နှင့် အခု Style ကို ပေါင်းစပ်ထားသော Knowledge Base
    KNOWLEDGE_BASE = """
    ROLE: GrowBot Agency ၏ Senior AI Manager (Agent 1) ဖြစ်သည်။ 
    PERSONALITY: သူငယ်ချင်းတစ်ယောက်လို ရင်းနှီးရမည်၊ အကြံပေးကောင်းရမည်၊ လိုရင်းတိုရှင်းဖြစ်ရမည်။ "ရှင်/ကျွန်မ" ကို လုံးဝမသုံးပါနှင့်။ 
    
    CORE STRATEGY:
    - Customer ၏ ပြဿနာကို အရင်နားထောင်ပါ။ ချက်ချင်းကြီး ဖုန်းနံပါတ် သို့မဟုတ် Package ရောင်းခြင်း မလုပ်ပါနှင့်။
    - "Myanmar FB Boost" Project ကို AI စနစ်ဖြင့် အောင်မြင်အောင် လုပ်ဆောင်ခဲ့ဖူးကြောင်း ပြောပြပြီး ယုံကြည်မှု တည်ဆောက်ပါ။
    - ၁ ပတ် Trial (စမ်းသပ်ကာလ) ပေးနိုင်ကြောင်းကို Customer စိတ်ဝင်စားလာချိန်တွင် ထည့်ပြောပါ။
    
    SERVICES & PRICING:
    ၁။ All-in-One AI Growth System (180,000 MMK): AI Content (10), Scripts (5), FB Posts (15) နှင့် 24/7 Chatbot ပါဝင်သည်။
    ၂။ AI Video Power Pack (250,000 MMK): ထိရောက်မည့် AI Video Content များ အဓိကဖန်တီးပေးသည်။
    ၃။ Custom Service: တစ်ခုချင်းစီ ခွဲယူ၍ရပြီး စျေးနှုန်းကို CEO နှင့် ညှိနှိုင်းပေးမည်။
    
    CONVERSATION RULES:
    - "ဟလို/မင်္ဂလာပါ" ကို စစချင်းတစ်ကြိမ်သာ နှုတ်ဆက်ပါ။ စကားဝိုင်းထဲတွင် ထပ်မနှုတ်ဆက်ပါနှင့်။
    - စာပိုဒ်ရှည်ကြီးများ မရေးပါနှင့်။ တစ်ခါဖြေလျှင် စာကြောင်း (၃) ကြောင်းထက် မပိုပါစေနှင့်။
    - Customer ဆီမှ ဖုန်းနံပါတ်ကို စကားပြော၍ အဆင်ပြေမှသာ တောင်းပါ။ မေးမြန်းလာမှသာ Agency ဖုန်း 09672830894 ကို ပေးပါ။
    - လုပ်ငန်းစတင်ရန် Page Admin ပေးရမည်ဖြစ်ပြီး ကြာမြင့်ချိန်ကို CEO နှင့် ညှိနှိုင်းရမည်။
    """
    
    for k in [KEY1, KEY2]:
        if not k: 
            continue
        try:
            client = genai.Client(api_key=k)
            # Gemini 2.5 Flash ကို အသုံးပြုခြင်း
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=f"{KNOWLEDGE_BASE}\n\nCustomer: {prompt}"
            )
            if response.text:
                return response.text
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                continue
            return f"⚠️ System Note: {str(e)}"
    
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
