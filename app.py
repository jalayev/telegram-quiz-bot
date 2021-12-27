import logging

from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
# from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, Dispatcher
import telegram
from telebot.credentials import bot_token, bot_user_name, URL
from telebot.quiz_game.quiz_main import quiz_start

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# global bot
# global TOKEN
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

# start the flask app
app = Flask(__name__)

# Quiz content
game_started = False
quiz = quiz_start()


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    global game_started
    global quiz
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    # for debugging purposes only
    print("got text message :", text)
    print(f"\n{game_started}\n")
    # the first time you chat with the bot AKA the welcoming message
    if text == "/start" and not game_started:
        # print the welcoming message
        bot_welcome = """
        📖 You have now started the quiz.
        ⏩ You have 3 lives remaining.
        ⏩ Enter 'quit' to quit the game.
        """
        # send the welcoming message
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)
        quiz = quiz_start()
        quiz.next_question(bot, chat_id, msg_id)
        game_started = True
    elif text.lower() == 'quit' and game_started:
        msg = "The game is now over. Click /start to start the quiz\n"
        msg += f"Your final score is {quiz.score}/{quiz.question_number}"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        game_started = False
    elif (text.lower() == "true" or text.lower() == "t") and game_started:
        text = "true"
        quiz.check_answer(bot, chat_id, msg_id, text)
        if quiz.game_is_over:
            msg = "You don't have any more lives, the game is over.\n" \
                  f"Your final score is {quiz.score}/{quiz.question_number}"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            game_started = False
        else:
            msg = f"Remaining lives: {quiz.lives}\n" \
                  f"Current score is {quiz.score}/{quiz.question_number}"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            quiz.next_question(bot, chat_id, msg_id)
    elif (text.lower() == "false" or text.lower() == "f") and game_started:
        text = "false"
        quiz.check_answer(bot, chat_id, msg_id, text)
        if quiz.game_is_over:
            msg = "You don't have any more lives, the game is over.\n" \
                  f"Your final score is {quiz.score}/{quiz.question_number}"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            game_started = False
        else:
            msg = f"Remaining lives: {quiz.lives}\n" \
                  f"Current score is {quiz.score}/{quiz.question_number}"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            quiz.next_question(bot, chat_id, msg_id)
    elif text == "/start" and game_started:
        msg = "Game is already started. Enter 'quit' to quit or answer the question with 'true' or 'false'"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    else:
        msg = "Not allowed input. Please click /start to start the quiz or answer the question with 'true' or 'false'"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    return 'ok'


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    # we use the bot object to link the bot to our app which live
    # in the link provided by URL
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    # something to let us know things work
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/')
def index():
    return '.'


if __name__ == '__main__':
    app.run(threaded=True)

# button implementation
# elif text == "buttons":
#     keyboard = [
#         [
#             InlineKeyboardButton("True", callback_data='true'),
#             InlineKeyboardButton("False", callback_data='false'),
#         ]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     update.message.reply_text('Please choose:', reply_markup=reply_markup) # elif text == "buttons":
#     #     keyboard = [
#     #         [
#     #             InlineKeyboardButton("True", callback_data='true'),
#     #             InlineKeyboardButton("False", callback_data='false'),
#     #         ]
#     #     ]
#     #     reply_markup = InlineKeyboardMarkup(keyboard)
#     #     update.message.reply_text('Please choose:', reply_markup=reply_markup)
