from flask import Flask, request

app = Flask(__name__)

# Facebook Dashboard မှာ ရိုက်ထည့်တဲ့ Token နဲ့ ဒီကစာသား အတိအကျ တူရပါမယ်
VERIFY_TOKEN = "GrowBot_Secret_123" 

@app.route('/webhook', methods=['GET'])
def verify():
    # Facebook က URL ကို စမ်းသပ်စစ်ဆေးတဲ့အပိုင်း
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification token mismatch", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    # စာဝင်လာရင် လက်ခံတဲ့အပိုင်း
    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(port=5000)
