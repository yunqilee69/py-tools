from telegram import Update
from telegram.ext import Application, MessageHandler, filters

TOKEN = "8532027931:AAE6T5HcDdKCeLR7lqIIkcA2Fll-dbCNFlY"   # 换成你的

async def echo(update: Update, _):
    await update.message.reply_text(update.message.text)

print('启动中')
app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.run_polling()          # 轮询模式，无需反向代理
print('启动完成')