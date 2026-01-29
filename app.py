import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# စကားပြောမှတ်ဉာဏ်ကို user_id အလိုက် စနစ်တကျ သိမ်းဆည်းမည်
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
                sender_id = str(messaging['sender']['id']) # ID ကို String အဖြစ် အသေအချာပြောင်းပါ
                if messaging.get('message'):
                    message_text = messaging['message'].get('text')
                    if message_text:
                        try:
                            # User တဦးချင်းစီ၏ history ကို ခေါ်ယူခြင်း
                            if sender_id not in chat_history:
                                chat_history[sender_id] = []
                            
                            current_history = chat_history[sender_id]
                            ai_answer = call_senior_ai_manager(message_text, current_history)
                            
                            # History update (နောက်ဆုံး အသွားအပြန် ၂ ကြိမ်သာမှတ်မည် - Error နည်းရန်)
                            current_history.append({"role": "user", "parts": [{"text": message_text}]})
                            current_history.append({"role": "model", "parts": [{"text": ai_answer}]})
                            chat_history[sender_id] = current_history[-4:] 
                            
                            send_fb_message(sender_id, ai_answer)
                        except Exception as e:
                            print(f"Server Error Log: {e}")
                            # Error ဖြစ်လျှင်ပင် customer စောင့်မနေရအောင် အခြေခံအဖြေတခုပေးခြင်း
                            fallback_msg = "မင်္ဂလာပါခင်ဗျာ၊ လူကြီးမင်း၏ မေးမြန်းမှုကို Senior Manager ထံသို့ လွှဲပြောင်းပေးနေပါသည်၊ ခေတ္တစောင့်ပေးပါခင်ဗျာ။"
                            send_fb_message(sender_id, fallback_msg)
    return "ok", 200

def call_gemini_direct(prompt):
    # Model ID ကို gemini-1.5-flash လို့ပဲ သုံးပြီး URL ကို အမှန်ကန်ဆုံး ပြင်ထားပါတယ်
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    knowledge_base = """
    မင်းက GrowBot Agency ရဲ့ AI Manager ဖြစ်တယ်။ 
    
    **နှုတ်ဆက်ပုံလမ်းညွှန်:** Customer က "မင်္ဂလာပါ" လို့ စတင်နှုတ်ဆက်ရင် ဖြစ်စေ၊ စကားစပြောရင်ဖြစ်စေ အောက်ပါအတိုင်း အမြဲနှုတ်ဆက်ပါ။
    "မင်္ဂလာပါခင်ဗျာ။ GrowBot Agency ရဲ့ AI Manager အနေနဲ့ ကြိုဆိုပါတယ်ခင်ဗျာ။ ကျွန်တော်တို့ GrowBot Agency က AI နည်းပညာတွေကို အသုံးပြုပြီး စီးပွားရေးလုပ်ငန်းတွေ တိုးတက်အောင် ကူညီပေးနေပါတယ်ခင်ဗျာ။ ဘယ်လိုများ ကူညီပေးရမလဲဆိုတာ ပြောပြပေးနိုင်ပါတယ်ခင်ဗျ။"
    """

    payload = {
        "contents": [{
            "parts": [{"text": f"{knowledge_base}\n\nCustomer: {prompt}"}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        if 'candidates' in result and result['candidates']:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # တကယ်လို့ 404 ထပ်တက်ရင် ဘာကြောင့်လဲဆိုတာ အတိအကျ မြင်ရအောင် Logs ထုတ်ခြင်း
            print(f"DEBUG - Full Response: {result}")
            return "ခဏနေမှ ပြန်မေးပေးပါခင်ဗျာ။"
    except Exception as e:
        return "ခဏနေမှ ပြန်မေးပေးပါခင်ဗျာ။"
        
def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
