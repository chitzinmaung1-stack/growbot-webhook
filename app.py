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

# စကားပြောမှတ်ဉာဏ် (Memory) အတွက် ရိုးရှင်းသော Dictionary တစ်ခု သုံးထားပါသည်
# မှတ်ချက် - Server Restart ဖြစ်လျှင် Memory ပျောက်ပါမည်။ အမြဲတမ်းမှတ်လိုပါက Database လိုအပ်ပါသည်။
chat_history = {}

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
                            # User တဦးချင်းစီ၏ History ကို ယူခြင်း
                            history = chat_history.get(sender_id, [])
                            
                            # AI ထံမှ အဖြေတောင်းခြင်း
                            ai_answer = call_senior_ai_manager(message_text, history)
                            
                            # History ကို Update လုပ်ခြင်း (နောက်ဆုံး ၅ ကြိမ်အထိ မှတ်မည်)
                            history.append({"role": "user", "parts": [{"text": message_text}]})
                            history.append({"role": "model", "parts": [{"text": ai_answer}]})
                            chat_history[sender_id] = history[-10:] 
                            
                            send_fb_message(sender_id, ai_answer)
                        except Exception as e:
                            print(f"Deployment Error: {e}")
                            send_fb_message(sender_id, "လူကြီးမင်း၏ မေးခွန်းအတွက် အကောင်းဆုံး ဗျူဟာကို စဉ်းစားနေပါသည်၊ ခေတ္တစောင့်ပေးပါခင်ဗျာ။")
    return "ok", 200

def call_senior_ai_manager(prompt, history):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GOOGLE_API_KEY}"
    
    # လုပ်ငန်းဗျူဟာနှင့် Knowledge Database
    KNOWLEDGE_DB = """
    ROLE: Senior AI Strategy Consultant of GrowBot Agency.
    MISSION: လုပ်ငန်းရှင်များကို AI နည်းပညာဖြင့် အောင်မြင်အောင် လမ်းပြရန်နှင့် ယုံကြည်မှုတည်ဆောက်ရန်။
    TONE: တည်ကြည်သော၊ ပရော်ဖက်ရှင်နယ်ဆန်သော၊ အကျိုးအကြောင်းခိုင်လုံသော။
    
    SERVICES & PRICING:
    1. All-in-One AI Growth System (180,000 MMK/month): 10 Special Contents, 5 Scripts, 15 Posts, 24/7 Chatbot.
    2. AI Content & Video Power Pack (250,000 MMK/month): 10 Special Contents, 5 Scripts, 10 AI Video Posts.
    
    STRATEGY:
    - Customer ၏ Pain Point ကို အရင်မေးမြန်းပြီး Diagnostic လုပ်ပါ။
    - Myanmar FB Boost project အောင်မြင်မှု သာဓကကို ထည့်သွင်းပြောဆိုပါ။
    - ၁ ပတ် Trial ပေးနိုင်ကြောင်းနှင့် လစဉ်ကြေးစနစ်ဖြစ်၍ အန္တရာယ်ကင်းကြောင်း အသိပေးပါ။
    - ရောင်းရုံသက်သက်မဟုတ်ဘဲ အကြံပေးတစ်ယောက်ကဲ့သို့ ပြုမူပါ။
    """

    payload = {
        "contents": history + [{"role": "user", "parts": [{"text": f"Context: {KNOWLEDGE_DB}\n\nCustomer Message: {prompt}"}]}]
    }
    
    response = requests.post(url, json=payload, timeout=15)
    result = response.json()
    
    try:
        return result['candidates'][0]['content']['parts'][0]['text']
    except:
        return "လူကြီးမင်း၏ လုပ်ငန်းအတွက် အဆီလျော်ဆုံး အဖြေကို ရှာဖွေနေပါသည်၊ ခေတ္တစောင့်ပေးပါခင်ဗျာ။"

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
