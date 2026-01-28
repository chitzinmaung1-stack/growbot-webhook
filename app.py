import os
import google.generativeai as genai
from flask import Flask, request
import requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Gemini Setup (Llama အစား Gemini ကို ပြောင်းလဲအသုံးပြုထားပါတယ်)
# Render Environment ထဲမှာ GOOGLE_API_KEY ဆိုပြီး သေချာထည့်ပေးပါ
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Facebook Configuration
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "GrowBot_Secret_123")

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
            for messaging_event in entry.get('messaging', []):
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message'].get('text')
                    
                    if message_text:
                        try:
                            # Agent 1 ၏ System Prompt ကို အားကောင်းအောင် ပြင်ဆင်ထားပါတယ်
                            prompt = f"""မင်းက GrowBot Agency ရဲ့ အရောင်းနှင့် ဆက်ဆံရေး Manager (Agent 1) ဖြစ်တယ်။ 
                            လူကြီးမင်းလို့ သုံးနှုန်းပြီး ယဉ်ကျေးပျူငှာစွာ မြန်မာလို ပြန်ဖြေပေးပါ။ 
                            GrowBot Agency က AI Chatbot နဲ့ Automation ဝန်ဆောင်မှု ပေးကြောင်းကိုသာ ဖြေပါ။
                            Customer မေးခွန်း - {message_text}"""
                            
                            response = model.generate_content(
                                prompt,
                                generation_config=genai.types.GenerationConfig(temperature=0.3)
                            )
                            ai_answer = response.text
                            send_message(sender_id, ai_answer)
                        except Exception as e:
                            print(f"Error: {e}")
    return "ok", 200

def send_message(recipient_id, message_text):
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post("https://graph.facebook.com/v21.0/me/messages", params=params, headers=headers, json=data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
