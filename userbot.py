from telethon import TelegramClient, events
import asyncio, random
from datetime import datetime, timedelta
import openai

# ------ إعدادات Telegram ------
api_id = YOUR_API_ID          # ضع هنا api_id من my.telegram.org
api_hash = 'YOUR_API_HASH'    # ضع هنا api_hash من my.telegram.org
phone = '+YOUR_PHONE_NUMBER'  # ضع رقمك مع مفتاح الدولة

client = TelegramClient('userbot_session', api_id, api_hash)

# ------ إعدادات OpenAI ------
openai.api_key = 'YOUR_OPENAI_API_KEY'  # ضع مفتاح OpenAI الخاص بك

# قائمة رسائل جاهزة لتجنب التكرار
reply_templates = [
    "يعطيك العافية، والله مشغولة شوي ما بطول لرد عليك، رح رد عليك أول ما افضى، شكرا لصبرك",
    "أهلاً! حالياً مشغولة شوي، سأعود للرد عليك فوراً ❤️",
    "مرحباً، غير متواجدة حالياً، لكن رح أرجعلك خلال قليل 🌸"
]

# تخزين الرسائل المؤجلة
pending_replies = {}

# ------ استقبال رسالة جديدة ------
@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    sender = await event.get_sender()
    sender_id = sender.id
    message = event.message.message

    # الرد الذكي مع AI لتغيير صياغة الرسائل
    ai_response = random.choice(reply_templates)
    try:
        completion = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"حول هذه الرسالة لرد طبيعي قصير باللهجة العربية بأسلوب مرح ولطيف: '{ai_response}'",
            max_tokens=50
        )
        ai_response = completion.choices[0].text.strip()
    except:
        pass  # fallback للرد التقليدي

    await client.send_message(sender_id, ai_response)

    # تذكير بعد 10 دقائق
    remind_time = datetime.now() + timedelta(minutes=10)
    pending_replies[sender_id] = (remind_time, message)

# التحقق من التذكيرات
async def reminder_checker():
    while True:
        now = datetime.now()
        for user_id, (time, msg) in list(pending_replies.items()):
            if now >= time:
                await client.send_message(user_id, "⏰ تذكير: لم يتم الرد بعد على رسالتك! ❤️")
                del pending_replies[user_id]
        await asyncio.sleep(60)

# تشغيل البوت
async def main():
    asyncio.create_task(reminder_checker())
    await client.start(phone)
    print("✅ Userbot جاهز ويعمل 24/7")
    await client.run_until_disconnected()

asyncio.run(main())
