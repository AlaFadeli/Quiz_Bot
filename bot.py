from datetime import datetime
import sys
now = datetime.now().hour
if not (8 <=now < 24 ):
    print("Outside allowed time. Exiting")
    sys.exit(0)




import json
import random
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

CHOOSE_TYPE, ASK_QUESTION, CHECK_ANSWER = range(3)

# Load all questions from JSON file
with open("all_questions.json", "r") as f:
    questions_data = json.load(f)

# Group questions by class
questions_by_class = {
    "ev": [q for q in questions_data if q["class"].lower() == "ev"],
    "cv": [q for q in questions_data if q["class"].lower() == "cv"]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to FS Quiz Bot!\nType 'EV' or 'CV' to start.")
    return CHOOSE_TYPE

async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q_type = update.message.text.strip().lower()

    if q_type not in ["ev", "cv"]:
        await update.message.reply_text("Please choose either 'EV' or 'CV'.")
        return CHOOSE_TYPE

    selected_list = questions_by_class.get(q_type, [])
    if not selected_list:
        await update.message.reply_text("No questions available for this type.")
        return CHOOSE_TYPE

    question = random.choice(selected_list)
    context.user_data["current_question"] = question

    option_lines = []
    option_letters = ["A", "B", "C", "D", "E", "F"]
    for i, ans in enumerate(question["options"]):
        option_lines.append(f"{option_letters[i]}) {ans}")

    context.user_data["current_answer"] = question["correct_option"]

    q_text = f"📘 *Question:*\n{question['text']}\n\n" + "\n".join(option_lines)
    await update.message.reply_text(q_text, parse_mode="Markdown")

    return CHECK_ANSWER

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text.strip().upper()
    current_question = context.user_data.get("current_question", {})
    correct_answer = current_question.get("correct_option", "")
    explanation = current_question.get("explanation", "No explanation provided.")

    if user_answer == correct_answer:
        reply = "✅ *Correct!*"
    else:
        reply = f"❌ *Wrong!* The correct answer was: {correct_answer}"

    reply += f"\n\n📘 *Explanation:*\n{explanation}"

    await update.message.reply_text(reply, parse_mode="Markdown")
    await update.message.reply_text("Type 'EV' or 'CV' to get another question.")
    return CHOOSE_TYPE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Quiz cancelled. Type /start to try again.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token("8167373653:AAGYS2IjLOubzyciagnoV2dKu8w11s-h3Ow").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_type)],
            CHECK_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
