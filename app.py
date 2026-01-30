import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Key များကို Render မှ တိုက်ရိုက်ယူခြင်း
KEY1 = os.getenv("GOOGLE_API_KEY_1")
KEY2 = os.getenv("GOOGLE_API_KEY_2")
PAGE_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
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
                    msg = messaging['message'].get('text')
                    if msg:
                        final_reply = try_all_keys(msg)
                        send_fb(sender_id, final_reply)
    return "ok", 200

def try_all_keys(prompt):
    keys = [KEY1, KEY2]
    # နာမည်ကို gemini-1.5-flash-latest ဟု ပိုမိုတိကျစွာ ပြောင်းလဲထားသည်
    model_id = "gemini-1.5-flash-latest" 
    
    for k in keys:
        if not k: continue
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={k}"
        try:
            r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=25)
            res = r.json()
            if 'candidates' in res:
                return res['candidates'][0]['content']['parts'][0]['text']
        except:
            continue
            
    return "လူကြီးမင်း၏ မေးခွန်းအတွက် အကောင်းဆုံးဝန်ဆောင်မှုများကို ပြန်လည်စစ်ဆေးနေပါသည်၊ ခဏလေးစောင့်ပေးပါခင်ဗျာ။"

def send_fb(uid, txt):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_TOKEN}"
    requests.post(url, json={"recipient": {"id": uid}, "message": {"text": txt}})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
