import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Render မှ နာမည်များကို အတိအကျယူခြင်း
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
                        # စမ်းသပ်ချက်များကို တိုက်ရိုက်ပြရန်
                        final_reply = try_api(msg)
                        send_fb(sender_id, final_reply)
    return "ok", 200

def try_api(prompt):
    # Gemini 1.5 Flash Stable Version ကို သုံးသည်
    keys = [KEY1, KEY2]
    debug_info = []

    for i, k in enumerate(keys, 1):
        if not k:
            debug_info.append(f"Key {i}: Empty in Render")
            continue
        
        # URL ကို အရှင်းဆုံး Version ဖြင့် ပြောင်းလဲထားသည်
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
        
        try:
            r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
            res = r.json()
            
            if 'candidates' in res:
                return res['candidates'][0]['content']['parts'][0]['text']
            else:
                # ဘာကြောင့် မရတာလဲဆိုတဲ့ အဖြေကို တိုက်ရိုက်ယူမည်
                err_msg = res.get('error', {}).get('message', 'No Response')
                debug_info.append(f"Key {i} Error: {err_msg}")
        except Exception as e:
            debug_info.append(f"Key {i} Exception: {str(e)}")

    return "❌ System Error Info:\n" + "\n".join(debug_info)

def send_fb(uid, txt):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_TOKEN}"
    requests.post(url, json={"recipient": {"id": uid}, "message": {"text": txt}})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
