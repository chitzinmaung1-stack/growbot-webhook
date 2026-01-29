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
                sender_id = messaging['sender']['id']
                if messaging.get('message'):
                    message_text = messaging['message'].get('text')
                    if message_text:
                        try:
                            ai_answer = call_gemini_2_flash(message_text)
                            send_fb_message(sender_id, ai_answer)
                        except Exception as e:
                            # Error ဖြစ်ရင် logs မှာ အတိအကျကြည့်လို့ရအောင် လုပ်ထားပါတယ်
                            print(f"Deployment Error: {e}")
                            send_fb_message(sender_id, "စနစ်ကို ခေတ္တစစ်ဆေးနေပါတယ်ခင်ဗျာ။")
    return "ok", 200

def call_gemini_3_flash(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GOOGLE_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    # --- ဤနေရာတွင် မိမိလုပ်ငန်းအကြောင်းအရာများကို အသေးစိတ် ဖြည့်စွက်နိုင်ပါသည် ---
    KNOWLEDGE_DATABASE = """
    GrowBot Agency ဝန်ဆောင်မှုများ အသေးစိတ်-
    ၁။ AI Chatbot Development: Facebook Messenger နှင့် Telegram (Airdrop/Task bots) များတွင် ၂၄ နာရီ အလိုအလျောက် အရောင်းပိတ်ပေးမည့် စနစ်များ။
    ၂။ Sales & Marketing Strategy: လုပ်ငန်းများ၏ အမြတ်အစွန်း တိုးတက်လာစေရန် နည်းဗျူဟာများ ရေးဆွဲပေးခြင်း။
    ၃။ Business Automation: လူအင်အား သုံးစရာမလိုဘဲ လုပ်ငန်းစဉ်များကို AI ဖြင့် အလိုအလျောက် လည်ပတ်စေခြင်း။
    ၄။ Special Content Agent 2: စာတစ်ကြောင်း ပို့ရုံဖြင့် ပရော်ဖက်ရှင်နယ် Marketing Post နှင့် ပုံများကို Page ပေါ် တိုက်ရိုက်တင်ပေးသည့် စနစ်။
    အောင်မြင်မှုမှတ်တမ်း: Myanmar FB Boost (Telegram Airdrop Bot) ကို အောင်မြင်စွာ တည်ဆောက်ခဲ့သည်။
    """

    system_instruction = f"""
    You are the Senior AI Manager of GrowBot Agency. 
    Use the following Knowledge Database to answer customer questions precisely and professionally in Burmese.
    Combine your internal reasoning with this data.
    
    DATABASE:
    {KNOWLEDGE_DATABASE}
    """
    
    payload = {
        "contents": [{
            "parts": [{"text": f"Instruction: {system_instruction}\n\nCustomer Message: {prompt}"}]
        }]
    }
    
    # ... (ကျန်တဲ့ request ပိုင်းက အတူတူပါပဲ) ...

    
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    # API ကနေ အဖြေပြန်လာတဲ့ပုံစံကို သေချာစစ်ဆေးဖတ်ယူခြင်း
    try:
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"API Response Error: {result}")
            return "လူကြီးမင်း မေးခွန်းကို ကျွန်တော် နားလည်အောင် ကြိုးစားနေပါတယ်ခင်ဗျာ။"
    except (KeyError, IndexError):
        return "ဝန်ဆောင်မှုများအကြောင်း သိလိုပါက တစ်ချက်လောက် ထပ်မေးပေးပါခင်ဗျာ။"

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
