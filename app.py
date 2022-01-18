import logging

from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
# from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, Dispatcher
import telegram
from telebot.credentials import bot_token, bot_user_name, URL
from telebot.quiz_game.quiz_main import quiz_start

import pickle
import psycopg2
from sqlalchemy import create_engine
from contextlib import closing

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
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:010209500714@localhost/tg_quizbot_db'
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.secret_key = 'secret string'

# Quiz content
game_started = False
chosen_topic = "general"
chosen_difficulty = "normal"
lives_num = 5
quiz = quiz_start(chosen_topic, lives_num)


# accepts string score in form "int1/int2" and gives int1 in int type
def str_score_to_int(str_score):
    score = 0
    i = 0
    while str_score[i] != '/':
        score = score * 10 + int(str_score[i])
        i += 1
    return score


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    # print(" \n ---local port--- \n")  # testing
    print(" \n ---heroku server--- \n")  # testing
    global game_started
    global quiz
    global chosen_topic
    global chosen_difficulty
    global lives_num
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.effective_message.chat_id
    msg_id = update.effective_message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.effective_message.text.encode('utf-8').decode()

    # Pickling quiz object (to store its last state)
    pickled_quiz = pickle.dumps(quiz)
    # quiz = pickle.loads(pickled_quiz)  # unpickle it later

    username = update.message.from_user.first_name
    userid = update.message.from_user.id
    print("Bot is currently used by " + username + " userid: " + str(userid))
    # --- PostgreSql DB ---
    db_string = "postgres://qfcagbtgogiiqe:07bfd9a462edc706c037450f12c08ac4cc6934a2ed060f4a6ccc6e78a1c09e2d@ec2-99-81-177-233.eu-west-1.compute.amazonaws.com:5432/di7qmaduus4kp"
    # db_string = "postgresql://postgres:010209500714@localhost/tg_quizbot_db"  # local
    db = create_engine(db_string)
    print(db)
    # stats table
    con_stats = db.connect()
    cur_stats = con_stats.cursor()
    cur_stats.execute("CREATE TABLE IF NOT EXISTS stats (id INTEGER, username TEXT, "
                      "topic TEXT, difficulty TEXT, score TEXT, "
                      "UNIQUE(id, topic, difficulty))")
    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'general', 'easy', '0/0')", (userid, username))
    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'general', 'normal', '0/0')", (userid, username))
    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'general', 'hard', '0/0')", (userid, username))

    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'history', 'easy', '0/0')", (userid, username))
    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'history', 'normal', '0/0')", (userid, username))
    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'history', 'hard', '0/0')", (userid, username))

    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'science', 'easy', '0/0')", (userid, username))
    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'science', 'normal', '0/0')", (userid, username))
    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'science', 'hard', '0/0')", (userid, username))

    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'nature', 'easy', '0/0')", (userid, username))
    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'nature', 'normal', '0/0')", (userid, username))
    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'nature', 'hard', '0/0')", (userid, username))

    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'animation', 'easy', '0/0')", (userid, username))
    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'animation', 'normal', '0/0')", (userid, username))
    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'animation', 'hard', '0/0')", (userid, username))

    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'games', 'easy', '0/0')", (userid, username))
    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'games', 'normal', '0/0')", (userid, username))
    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'games', 'hard', '0/0')", (userid, username))

    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'films_tv', 'easy', '0/0')", (userid, username))
    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'films_tv', 'normal', '0/0')", (userid, username))
    cur_stats.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, 'films_tv', 'hard', '0/0')", (userid, username))

    # quiz_db table - first connection (insert row with unique chat_id)
    connection = db.connect()
    print(" -chat_id: " + str(chat_id) + ", connection.total_changes: " + str(connection.total_changes))
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS quiz_db (chat_id INT, game_started TEXT, quiz BYTEA, "
                   "chosen_topic TEXT, chosen_difficulty TEXT, lives_num INTEGER, "
                   "UNIQUE(chat_id))")
    cursor.execute("INSERT OR IGNORE INTO quiz_db VALUES (?, 'false', ?, 'general', 'normal', 5)", (chat_id, pickled_quiz))
    # consequent connections (read)
    rows = cursor.execute(
        "SELECT game_started, quiz, chosen_topic, chosen_difficulty, lives_num FROM quiz_db WHERE chat_id = ?",
        (chat_id,)).fetchall()
    print(rows)
    game_started_str = rows[0][0]
    if game_started_str == "false":
        game_started = False
    elif game_started_str == "true":
        game_started = True
    pickled_quiz = rows[0][1]
    quiz = pickle.loads(pickled_quiz)
    chosen_topic = rows[0][2]
    chosen_difficulty = rows[0][3]
    lives_num = rows[0][4]

    # for debugging purposes only
    print("got text message :", text)
    print(f"\nGame started: {game_started}\n")
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
        del quiz  # ###
        quiz = quiz_start(chosen_topic, lives_num)
        quiz.next_question(bot, chat_id, msg_id)
        game_started = True
        # update quiz_db sqlite table
        pickled_quiz = pickle.dumps(quiz)
        cursor.execute(
            "UPDATE quiz_db SET game_started = ?, quiz = ? WHERE chat_id = ?",
            ('true', pickled_quiz, chat_id)
        )
    elif text == "/change_difficulty" and not game_started:
        msg = f"Current difficulty is {chosen_difficulty}.\n" \
              f"❄ type /easy to have 7 lives\n" \
              f"❄❄ type /normal to have 5 lives\n" \
              f"❄❄❄ type /hard to have 3 lives"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/easy" and not game_started:
        chosen_difficulty = "easy"
        lives_num = 7
        msg = f"You now have 7 lives for one quiz game.\n" \
              f"click /start to start the game."
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db sqlite table
        cursor.execute(
            "UPDATE quiz_db SET chosen_difficulty = ?, lives_num = ? WHERE chat_id = ?",
            (chosen_difficulty, lives_num, chat_id)
        )
    elif text == "/normal" and not game_started:
        chosen_difficulty = "normal"
        lives_num = 5
        msg = f"You now have 5 lives for one quiz game.\n" \
              f"Click /start to start the game."
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db sqlite table
        cursor.execute(
            "UPDATE quiz_db   SET chosen_difficulty = ?, lives_num = ? WHERE chat_id = ?",
            (chosen_difficulty, lives_num, chat_id)
        )
    elif text == "/hard" and not game_started:
        chosen_difficulty = "hard"
        lives_num = 3
        msg = f"You now have 3 lives for one quiz game.\n" \
              f"Click /start to start the game."
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db sqlite table
        cursor.execute(
            "UPDATE quiz_db SET chosen_difficulty = ?, lives_num = ? WHERE chat_id = ?",
            (chosen_difficulty, lives_num, chat_id)
        )
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
        # update quiz_db sqlite table
        cursor.execute(
            "UPDATE quiz_db SET chosen_topic = ? WHERE chat_id = ?",
            (chosen_topic, chat_id)
        )
    elif text == "/science" and not game_started:
        chosen_topic = "science"
        msg = f"Successfully selected topic: {chosen_topic}"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db sqlite table
        cursor.execute(
            "UPDATE quiz_db SET chosen_topic = ? WHERE chat_id = ?",
            (chosen_topic, chat_id)
        )
    elif text == "/nature" and not game_started:
        chosen_topic = "nature"
        msg = f"Successfully selected topic: {chosen_topic}"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db sqlite table
        cursor.execute(
            "UPDATE quiz_db SET chosen_topic = ? WHERE chat_id = ?",
            (chosen_topic, chat_id)
        )
    elif text == "/history" and not game_started:
        chosen_topic = "history"
        msg = f"Successfully selected topic: {chosen_topic}"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db sqlite table
        cursor.execute(
            "UPDATE quiz_db SET chosen_topic = ? WHERE chat_id = ?",
            (chosen_topic, chat_id)
        )
    elif text == "/animation" and not game_started:
        chosen_topic = "animation"
        msg = f"Successfully selected topic: {chosen_topic}"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db sqlite table
        cursor.execute(
            "UPDATE quiz_db SET chosen_topic = ? WHERE chat_id = ?",
            (chosen_topic, chat_id)
        )
    elif text == "/games" and not game_started:
        chosen_topic = "games"
        msg = f"Successfully selected topic: {chosen_topic}"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db sqlite table
        cursor.execute(
            "UPDATE quiz_db SET chosen_topic = ? WHERE chat_id = ?",
            (chosen_topic, chat_id)
        )
    elif text == "/films_tv" and not game_started:
        chosen_topic = "films_tv"
        msg = f"Successfully selected topic: {chosen_topic}"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db sqlite table
        cursor.execute(
            "UPDATE quiz_db SET chosen_topic = ? WHERE chat_id = ?",
            (chosen_topic, chat_id)
        )
    elif text.lower() == 'quit' and game_started:
        msg = "The game is now over.\n"
        msg += f"📊 Your final score: {quiz.score}/{quiz.question_number}\n" \
               f"Click /start to start a new quiz, /change_topic, /change_difficulty or view /stats"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        game_started = False
        # update quiz_db sqlite table
        cursor.execute(
            "UPDATE quiz_db SET game_started = ? WHERE chat_id = ?",
            ('false', chat_id)
        )
        # update stats sqlite table
        final_score = f"{quiz.score}/{quiz.question_number}"
        stats_score = cur_stats.execute(
            "SELECT score FROM stats WHERE id = ? AND topic = ? AND difficulty = ?",
            (userid, chosen_topic, chosen_difficulty)
        ).fetchall()
        final_score_int = str_score_to_int(final_score)
        stats_score_int = str_score_to_int(stats_score[0][0])
        print(f"Final score = {final_score_int}, stats_score = {stats_score_int}")
        if final_score_int > stats_score_int:
            cur_stats.execute(
                "UPDATE stats SET score = ? WHERE id = ? AND topic = ? AND difficulty = ?",
                (final_score, userid, chosen_topic, chosen_difficulty)
            )
    elif (text.lower() == "true" or text == '/true') and game_started:
        text = "true"
        quiz.check_answer(bot, chat_id, msg_id, text)
        if quiz.game_is_over:
            msg = "💔 You don't have any more lives, the game is over 💔\n" \
                  f"Your final score is {quiz.score}/{quiz.question_number}\n" \
                  f"Click /start to start a new quiz, /change_topic, /change_difficulty or view /stats"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            game_started = False
            # update quiz_db sqlite table
            cursor.execute(
                "UPDATE quiz_db SET game_started = ? WHERE chat_id = ?",
                ('false', chat_id)
            )
            # update stats sqlite table
            final_score = f"{quiz.score}/{quiz.question_number}"
            stats_score = cur_stats.execute(
                "SELECT score FROM stats WHERE id = ? AND topic = ? AND difficulty = ?",
                (userid, chosen_topic, chosen_difficulty)
            ).fetchall()
            final_score_int = str_score_to_int(final_score)
            stats_score_int = str_score_to_int(stats_score[0][0])
            print(f"Final score = {final_score_int}, stats_score = {stats_score_int}")
            if final_score_int > stats_score_int:
                cur_stats.execute(
                    "UPDATE stats SET score = ? WHERE id = ? AND topic = ? AND difficulty = ?",
                    (final_score, userid, chosen_topic, chosen_difficulty)
                )
        else:
            msg = f"💕 Remaining lives: {quiz.lives}\n" \
                  f"📊 Current score: {quiz.score}/{quiz.question_number}"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            quiz.next_question(bot, chat_id, msg_id)
            # update quiz_db sqlite table
            pickled_quiz = pickle.dumps(quiz)
            cursor.execute(
                "UPDATE quiz_db SET quiz = ? WHERE chat_id = ?",
                (pickled_quiz, chat_id)
            )
    elif (text.lower() == "false" or text == "/false") and game_started:
        text = "false"
        quiz.check_answer(bot, chat_id, msg_id, text)
        if quiz.game_is_over:
            msg = "💔 You don't have any more lives, the game is over 💔\n" \
                  f"Your final score is {quiz.score}/{quiz.question_number}\n" \
                  f"Click /start to start a new quiz, /change_topic, /change_difficulty or view /stats"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            game_started = False
            # update quiz_db sqlite table
            cursor.execute(
                "UPDATE quiz_db SET game_started = ? WHERE chat_id = ?",
                ('false', chat_id)
            )
            # update stats sqlite table
            final_score = f"{quiz.score}/{quiz.question_number}"
            stats_score = cur_stats.execute(
                "SELECT score FROM stats WHERE id = ? AND topic = ? AND difficulty = ?",
                (userid, chosen_topic, chosen_difficulty)
            ).fetchall()
            final_score_int = str_score_to_int(final_score)
            stats_score_int = str_score_to_int(stats_score[0][0])
            print(f"Final score = {final_score_int}, stats_score = {stats_score_int}")
            if final_score_int > stats_score_int:
                cur_stats.execute(
                    "UPDATE stats SET score = ? WHERE id = ? AND topic = ? AND difficulty = ?",
                    (final_score, userid, chosen_topic, chosen_difficulty)
                )
        else:
            msg = f"💕 Remaining lives: {quiz.lives}\n" \
                  f"📊 Current score: {quiz.score}/{quiz.question_number}"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            quiz.next_question(bot, chat_id, msg_id)
            # update quiz_db sqlite table
            pickled_quiz = pickle.dumps(quiz)
            cursor.execute(
                "UPDATE quiz_db SET quiz = ? WHERE chat_id = ?",
                (pickled_quiz, chat_id)
            )
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
        msg = "⚙ You can change the settings with /change_topic and /change_difficulty and click /start to play.\n" \
              "Type 'quit' to quit the game.\n" \
              "Settings can be changed only if the Quiz is not started.\n" \
              "bot creator's telegram username: @tima_1j ⚙"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/stats":
        stats_rows = cur_stats.execute(
            "SELECT username, difficulty, topic, score FROM stats WHERE id = ?",
            (userid,)).fetchall()
        print(f"\nstats_rows:\n {stats_rows} \n")
        if len(stats_rows) == 0:
            msg = "Sadly, you haven't played anything or there is something wrong with statistics."
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        else:
            msg = ""
            for user in stats_rows:
                if user[3] != "0/0":
                    msg += f"User: {user[0]} | difficulty: {user[1]} | topic: {user[2]} | score: {user[3]}\n"
            if msg == "":
                msg = "Sadly, you haven't played anything or there is something wrong with statistics."
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    else:
        msg = "Not allowed input. Please click /start to start the quiz or answer the question with '/true' or '/false'"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)

    con_stats.commit()
    con_stats.close()
    cur_stats.close()

    connection.commit()
    connection.close()
    cursor.close()

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
