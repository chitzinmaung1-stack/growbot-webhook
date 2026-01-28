from groq import Groq

# Groq Setup
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# AI Response ရယူရန်
completion = client.chat.completions.create(
    model="llama3-8b-8192", # Free သုံးဖို့ အမြန်ဆုံး model ပါ
    messages=[
        {"role": "system", "content": "မင်းက GrowBot Agency ရဲ့ AI Manager ပါ။"},
        {"role": "user", "content": message_text}
    ]
)
ai_answer = completion.choices[0].message.content
