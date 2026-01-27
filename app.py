from flask import Flask, request

app = Flask(__name__)

# ဒါက Facebook နဲ့ ချိတ်ရင် သုံးရမယ့် လျှို့ဝှက်ချက်ပါ။ သင် ကြိုက်တာ ပြောင်းလို့ရပါတယ်။
VERIFY_TOKEN = "GrowBot_Secret_123" 

@app.route('/webhook', methods=['GET'])
def verify():
    # Facebook က သင့် URL ကို စစ်ဆေးတဲ့ အပိုင်း
    token_sent = request.args.get("hub.verify_token")
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification token mismatch", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    # စာဝင်လာရင် လက်ခံတဲ့ အပိုင်း
    data = request.get_json()
    print("Received Data:", data) 
    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(port=5000)
