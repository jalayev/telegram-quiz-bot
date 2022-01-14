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
chosen_topic = "general"
chosen_difficulty = "normal"
lives_num = 5
quiz = quiz_start(chosen_topic, lives_num)


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    print(" \n ---local port--- \n")  # testing
    global game_started
    global quiz
    global chosen_topic
    global chosen_difficulty
    global lives_num
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
    if quiz.game_is_over:
        game_started = False

    if text == "/start" and not game_started:
        # print the welcoming message
        bot_welcome = f"""
        📖 You have now started the {chosen_topic} themed quiz.
        ⏩ You have {lives_num} lives remaining.
        ⏩ Enter 'quit' to quit the game.
        """
        # send the welcoming message
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)
        del quiz  # #####################################
        quiz = quiz_start(chosen_topic, lives_num)
        quiz.next_question(bot, chat_id, msg_id)
        game_started = True
    elif text == "/change_difficulty" and not game_started:
        msg = f"Current difficulty is {chosen_difficulty}.\n" \
              f"    type /easy to have 7 lives\n" \
              f"    type /normal to have 5 lives\n" \
              f"    type /hard to have 3 lives"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/easy" and not game_started:
        chosen_difficulty = "easy"
        lives_num = 7
        msg = f"You now have 7 lives for one quiz game.\n" \
              f"click /start to start the game."
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/normal" and not game_started:
        chosen_difficulty = "normal"
        lives_num = 5
        msg = f"You now have 5 lives for one quiz game.\n" \
              f"Click /start to start the game."
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/hard" and not game_started:
        chosen_difficulty = "hard"
        lives_num = 3
        msg = f"You now have 3 lives for one quiz game.\n" \
              f"Click /start to start the game."
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/change_topic" and not game_started:
        msg = f"Current topic is: {chosen_topic}.\n" \
              f"Available topics: \n" \
              f"🌍 /general \n" \
              f"🔭 /science \n" \
              f"🏞 /nature \n" \
              f"🧮 /history \n" \
              f"🖼 /animation \n" \
              f"🎮 /games \n" \
              f"🎬 /films_tv \n"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/general" and not game_started:
        chosen_topic = "general"
        msg = f"Successfully selected topic: {chosen_topic}"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/science" and not game_started:
        chosen_topic = "science"
        msg = f"Successfully selected topic: {chosen_topic}"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/nature" and not game_started:
        chosen_topic = "nature"
        msg = f"Successfully selected topic: {chosen_topic}"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/history" and not game_started:
        chosen_topic = "history"
        msg = f"Successfully selected topic: {chosen_topic}"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/animation" and not game_started:
        chosen_topic = "animation"
        msg = f"Successfully selected topic: {chosen_topic}"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/games" and not game_started:
        chosen_topic = "games"
        msg = f"Successfully selected topic: {chosen_topic}"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/films_tv" and not game_started:
        chosen_topic = "films_tv"
        msg = f"Successfully selected topic: {chosen_topic}"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text.lower() == 'quit' and game_started:
        msg = "The game is now over.\n"
        msg += f"Your final score is {quiz.score}/{quiz.question_number}\n" \
               f"Click /start to start a new quiz, /change_topic or /change_difficulty"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        game_started = False
    elif (text.lower() == "true" or text == '/true') and game_started:
        text = "true"
        quiz.check_answer(bot, chat_id, msg_id, text)
        if quiz.game_is_over:
            msg = "You don't have any more lives, the game is over.\n" \
                  f"Your final score is {quiz.score}/{quiz.question_number}\n" \
                  f"Click /start to start a new quiz, /change_topic or /change_difficulty"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            game_started = False
        else:
            msg = f"Remaining lives: {quiz.lives}\n" \
                  f"Current score is {quiz.score}/{quiz.question_number}"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            quiz.next_question(bot, chat_id, msg_id)
    elif (text.lower() == "false" or text == "/false") and game_started:
        text = "false"
        quiz.check_answer(bot, chat_id, msg_id, text)
        if quiz.game_is_over:
            msg = "You don't have any more lives, the game is over.\n" \
                  f"Your final score is {quiz.score}/{quiz.question_number}\n" \
                  f"Click /start to start a new quiz, /change_topic or /change_difficulty"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            game_started = False
        else:
            msg = f"Remaining lives: {quiz.lives}\n" \
                  f"Current score is {quiz.score}/{quiz.question_number}"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            quiz.next_question(bot, chat_id, msg_id)
    elif text == "/start" and game_started:
        msg = "Game is already started. Enter 'quit' to quit or answer the question with '/true' or '/false'"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/change_difficulty" and game_started:
        msg = "You cannot change the difficulty when the quiz is started.\n" \
              "Enter 'quit' to quit or answer the question with '/true' or '/false'"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/change_topic" and game_started:
        msg = "You cannot change the topic when the quiz is started.\n" \
              "Enter 'quit' to quit or answer the question with '/true' or '/false'"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/help":
        msg = "You can change the settings with /change_topic and /change_difficulty and click /start to play.\n" \
              "Type 'quit' to quit the game.\n" \
              "Settings can be changed only if the Quiz is not started."
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    else:
        msg = "Not allowed input. Please click /start to start the quiz or answer the question with '/true' or '/false'"
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
