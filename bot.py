import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler,ApplicationBuilder)

# Load your quiz questions
with open("output.json", "r") as f:
    questions = json.load(f)

# Simple user score tracking (in-memory or file)
user_scores = {}

QUESTION, ANSWER = range(2)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_scores[user_id] = {"score": 0, "current_q": 0}
    await send_question(update, context)
    return QUESTION

async def send_question(update, context):
    user_id = str(update.effective_user.id)
    q_index = user_scores[user_id]["current_q"]
    if q_index >= len(questions):
        await update.message.reply_text(f"🎉 Quiz finished! Your score: {user_scores[user_id]['score']} / {len(questions)}")
        return ConversationHandler.END

    q = questions[q_index]
    context.user_data["correct_answer"] = q["answer"]
    keyboard = [[option] for option in q["options"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text(f"Q{q['id']}: {q['question']}", reply_markup=reply_markup)

async def receive_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    answer = update.message.text
    correct = context.user_data.get("correct_answer")
    if answer == correct:
        user_scores[user_id]["score"] += 1
        await update.message.reply_text("✅ Correct!")
    else:
        await update.message.reply_text(f"❌ Wrong! Correct answer: {correct}")

    user_scores[user_id]["current_q"] += 1
    return await send_question(update, context)

# Stop command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Quiz cancelled.")
    return ConversationHandler.END

# Main
def main():
    app = ApplicationBuilder().token("8167373653:AAGYS2IjLOubzyciagnoV2dKu8w11s-h3Ow").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()

