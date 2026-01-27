from flask import Flask, request

app = Flask(__name__)

# Facebook မှာ ရိုက်ထည့်မယ့် Verify Token နဲ့ ဒီကစာသား အတိအကျ တူရပါမယ်
VERIFY_TOKEN = "GrowBot_Secret_123" 

@app.route('/webhook', methods=['GET'])
def verify():
    # Facebook က URL ကို စမ်းသပ်စစ်ဆေးတဲ့အပိုင်း
    token_sent = request.args.get("hub.verify_token")
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification token mismatch", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    # စာဝင်လာရင် လက်ခံတဲ့အပိုင်း (အခုတော့ 200 OK ပဲ ပြန်ထားပါမယ်)
    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(port=5000)
