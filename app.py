import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Render မှ Environment Variables များကို ယူသည်
# API Key နှစ်ခုလုံးကို Mail အသစ်မှ Key များဖြင့် အစားထိုးထားရန် လိုသည်
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
                        reply = try_all_models_and_keys(msg)
                        send_fb(sender_id, reply)
    return "ok", 200

def try_all_models_and_keys(prompt):
    # စမ်းသပ်မည့် Model ID များ စာရင်း
    model_variants = [
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
        "gemini-1.5-flash-002",
        "gemini-1.5-flash-001"
    ]
    
    debug_log = []

    for model in model_variants:
        for i, k in enumerate(KEYS, 1):
            if not k: continue
            
            # v1beta URL ကို အသုံးပြုထားသည်
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={k}"
            
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
                res = r.json()
                
                if 'candidates' in res:
                    # အောင်မြင်လျှင် ဘယ် Model နှင့် Key ကို သုံးသွားသည်ကိုပါ ပြမည်
                    return f"✅ Success! (Model: {model})\n\n{res['candidates'][0]['content']['parts'][0]['text']}"
                else:
                    err = res.get('error', {}).get('message', 'Unknown Error')
                    debug_log.append(f"❌ {model} (Key {i}): {err}")
            except Exception as e:
                debug_log.append(f"❌ {model} (Key {i}) Connection Error")

    return "🚫 1.5 Flash Models အားလုံး မရပါ:\n\n" + "\n".join(debug_log[:5]) # စာတိုစေရန် ၅ ခုသာပြသည်

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
