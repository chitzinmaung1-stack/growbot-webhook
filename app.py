import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Render မှ Environment Variables များကို တိုက်ရိုက်ယူသည်
KEYS = [os.getenv("GOOGLE_API_KEY_1"), os.getenv("GOOGLE_API_KEY_2")]
PAGE_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

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
                        # 2.0 Variants အားလုံးကို လိုက်စမ်းမည့် Function
                        reply = try_2_0_variants(msg)
                        send_fb(sender_id, reply)
    return "ok", 200

def try_2_0_variants(prompt):
    # စမ်းသပ်မည့် 2.0 Model ID များ စာရင်း
    variants = [
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash",
        "gemini-2.0-flash-thinking-exp",
        "gemini-2.0-flash-lite-preview-02-05"
    ]
    
    logs = []

    for model in variants:
        for i, k in enumerate(KEYS, 1):
            if not k: continue
            
            # v1beta URL ကို အသုံးပြုထားသည်
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={k}"
            
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
                res = r.json()
                
                if 'candidates' in res:
                    # အောင်မြင်လျှင် အသုံးပြုသွားသော Model အမည်ကိုပါ ပြမည်
                    return f"🚀 2.0 Success! (Model: {model})\n\n{res['candidates'][0]['content']['parts'][0]['text']}"
                else:
                    err = res.get('error', {}).get('message', 'Unknown Error')
                    logs.append(f"❌ {model} (Key {i}): {err}")
            except:
                logs.append(f"❌ {model} (Key {i}) Connection Fail")

    return "🚫 2.0 Models အားလုံး မရသေးပါ:\n\n" + "\n".join(logs[:4])

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
