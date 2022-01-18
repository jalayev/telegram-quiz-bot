from flask import Flask, request

import telegram
from telebot.credentials import bot_token, URL
from telebot.quiz_game.quiz_main import quiz_start

import pickle
import psycopg2

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


# accepts string score in form "int1/int2" and gives int1 in int type
def str_score_to_int(str_score):
    score = 0
    i = 0
    while str_score[i] != '/':
        score = score * 10 + int(str_score[i])
        i += 1
    return score


# updates statistics in postgresql stats table
def update_stats_table(cur_stats, cur_quiz, userid, topic, difficulty):
    final_score = f"{cur_quiz.score}/{cur_quiz.question_number}"
    cur_stats.execute(
        "SELECT score FROM stats WHERE id = %s AND topic = %s AND difficulty = %s",
        (userid, topic, difficulty)
    )
    stats_score = cur_stats.fetchall()
    final_score_int = str_score_to_int(final_score)
    stats_score_int = str_score_to_int(stats_score[0][0])
    print(f"Final score = {final_score_int}, stats_score = {stats_score_int}")
    if final_score_int > stats_score_int:
        cur_stats.execute(
            "UPDATE stats SET score = %s WHERE id = %s AND topic = %s AND difficulty = %s",
            (final_score, userid, topic, difficulty)
        )


def create_stats_table(cur_stats, userid, username):
    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'general', 'easy', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))
    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'general', 'normal', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))
    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'general', 'hard', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))

    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'history', 'easy', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))
    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'history', 'normal', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))
    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'history', 'hard', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))

    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'science', 'easy', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))
    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'science', 'normal', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))
    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'science', 'hard', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))

    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'nature', 'easy', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))
    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'nature', 'normal', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))
    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'nature', 'hard', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))

    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'animation', 'easy', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))
    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'animation', 'normal', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))
    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'animation', 'hard', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))

    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'games', 'easy', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))
    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'games', 'normal', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))
    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'games', 'hard', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))

    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'films_tv', 'easy', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))
    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'films_tv', 'normal', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))
    cur_stats.execute(
        "INSERT INTO stats VALUES (%s, %s, 'films_tv', 'hard', '0/0') ON CONFLICT (id, topic, difficulty) DO NOTHING",
        (userid, username))


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    print(" \n ---heroku server--- \n")  # testing
    global game_started
    global quiz
    # Pickling quiz object (to store its last state)
    pickled_quiz = pickle.dumps(quiz)
    global chosen_topic
    global chosen_difficulty
    global lives_num

    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.effective_message.chat_id
    msg_id = update.effective_message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.effective_message.text.encode('utf-8').decode()

    username = update.message.from_user.first_name
    userid = update.message.from_user.id
    print("Bot is currently used by " + username + " userid: " + str(userid))

    # --- PostgreSql DB ---
    # stats table
    con_stats = psycopg2.connect(
        host="ec2-99-81-177-233.eu-west-1.compute.amazonaws.com",
        database="di7qmaduus4kp",
        user="qfcagbtgogiiqe",
        password="07bfd9a462edc706c037450f12c08ac4cc6934a2ed060f4a6ccc6e78a1c09e2d")
    cur_stats = con_stats.cursor()
    cur_stats.execute("CREATE TABLE IF NOT EXISTS stats (id INTEGER, username TEXT, "
                      "topic TEXT, difficulty TEXT, score TEXT, "
                      "UNIQUE(id, topic, difficulty))")
    create_stats_table(cur_stats, userid, username)

    # quiz_db table - first connection (insert row with unique chat_id)
    connection = psycopg2.connect(
        host="ec2-99-81-177-233.eu-west-1.compute.amazonaws.com",
        database="di7qmaduus4kp",
        user="qfcagbtgogiiqe",
        password="07bfd9a462edc706c037450f12c08ac4cc6934a2ed060f4a6ccc6e78a1c09e2d")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS quiz_db (chat_id INT, game_started TEXT, quiz BYTEA, "
                   "chosen_topic TEXT, chosen_difficulty TEXT, lives_num INTEGER, "
                   "UNIQUE(chat_id))")
    cursor.execute(
        "INSERT INTO quiz_db VALUES (%s, 'false', %s, 'general', 'normal', 5) ON CONFLICT (chat_id) DO NOTHING",
        (chat_id, pickled_quiz))
    # consequent connections (read)
    cursor.execute(
        "SELECT game_started, quiz, chosen_topic, chosen_difficulty, lives_num FROM quiz_db WHERE chat_id = %s",
        (chat_id,))
    rows = cursor.fetchall()
    print(rows)

    game_started_str = rows[0][0]
    print(game_started_str)
    if game_started_str == "false":
        game_started = False
    elif game_started_str == "true":
        game_started = True

    pickled_quiz = rows[0][1]
    quiz = pickle.loads(pickled_quiz)
    print(quiz)

    chosen_topic = rows[0][2]
    print(chosen_topic)
    chosen_difficulty = rows[0][3]
    print(chosen_difficulty)
    lives_num = rows[0][4]
    print(f"Current lives: {lives_num}")

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
        del quiz  # ###                put lives num
        quiz = quiz_start(chosen_topic, 1000)
        quiz.next_question(bot, chat_id, msg_id)
        game_started = True
        # update quiz_db table
        pickled_quiz = pickle.dumps(quiz)
        cursor.execute(
            "UPDATE quiz_db SET game_started = %s, quiz = %s WHERE chat_id = %s",
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
        # update quiz_db table
        cursor.execute(
            "UPDATE quiz_db SET chosen_difficulty = %s, lives_num = %s WHERE chat_id = %s",
            (chosen_difficulty, lives_num, chat_id)
        )
    elif text == "/normal" and not game_started:
        chosen_difficulty = "normal"
        lives_num = 5
        msg = f"You now have 5 lives for one quiz game.\n" \
              f"Click /start to start the game."
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db table
        cursor.execute(
            "UPDATE quiz_db   SET chosen_difficulty = %s, lives_num = %s WHERE chat_id = %s",
            (chosen_difficulty, lives_num, chat_id)
        )
    elif text == "/hard" and not game_started:
        chosen_difficulty = "hard"
        lives_num = 3
        msg = f"You now have 3 lives for one quiz game.\n" \
              f"Click /start to start the game."
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db table
        cursor.execute(
            "UPDATE quiz_db SET chosen_difficulty = %s, lives_num = %s WHERE chat_id = %s",
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
        msg = f"Successfully selected topic: {chosen_topic}.\nClick /start to start the game."
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db table
        cursor.execute(
            "UPDATE quiz_db SET chosen_topic = %s WHERE chat_id = %s",
            (chosen_topic, chat_id)
        )
    elif text == "/science" and not game_started:
        chosen_topic = "science"
        msg = f"Successfully selected topic: {chosen_topic}.\nClick /start to start the game."
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db table
        cursor.execute(
            "UPDATE quiz_db SET chosen_topic = %s WHERE chat_id = %s",
            (chosen_topic, chat_id)
        )
    elif text == "/nature" and not game_started:
        chosen_topic = "nature"
        msg = f"Successfully selected topic: {chosen_topic}.\nClick /start to start the game."
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db table
        cursor.execute(
            "UPDATE quiz_db SET chosen_topic = %s WHERE chat_id = %s",
            (chosen_topic, chat_id)
        )
    elif text == "/history" and not game_started:
        chosen_topic = "history"
        msg = f"Successfully selected topic: {chosen_topic}.\nClick /start to start the game."
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db table
        cursor.execute(
            "UPDATE quiz_db SET chosen_topic = %s WHERE chat_id = %s",
            (chosen_topic, chat_id)
        )
    elif text == "/animation" and not game_started:
        chosen_topic = "animation"
        msg = f"Successfully selected topic: {chosen_topic}.\nClick /start to start the game."
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db table
        cursor.execute(
            "UPDATE quiz_db SET chosen_topic = %s WHERE chat_id = %s",
            (chosen_topic, chat_id)
        )
    elif text == "/games" and not game_started:
        chosen_topic = "games"
        msg = f"Successfully selected topic: {chosen_topic}.\nClick /start to start the game."
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db table
        cursor.execute(
            "UPDATE quiz_db SET chosen_topic = %s WHERE chat_id = %s",
            (chosen_topic, chat_id)
        )
    elif text == "/films_tv" and not game_started:
        chosen_topic = "films_tv"
        msg = f"Successfully selected topic: {chosen_topic}.\nClick /start to start the game."
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        # update quiz_db table
        cursor.execute(
            "UPDATE quiz_db SET chosen_topic = %s WHERE chat_id = %s",
            (chosen_topic, chat_id)
        )
    elif text.lower() == 'quit' and game_started:
        msg = "The game is now over.\n"
        msg += f"📊 Your final score: {quiz.score}/{quiz.question_number}\n" \
               f"Click /start to start a new quiz, /change_topic, /change_difficulty or view /stats"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        game_started = False
        # update quiz_db table
        cursor.execute(
            "UPDATE quiz_db SET game_started = %s WHERE chat_id = %s",
            ('false', chat_id)
        )
        # update stats table
        update_stats_table(cur_stats, quiz, userid, chosen_topic, chosen_difficulty)
    elif (text.lower() == "true" or text == '/true') and game_started:
        text = "true"
        quiz.check_answer(bot, chat_id, msg_id, text)
        if quiz.game_is_over:
            msg = "💔 You don't have any more lives, the game is over 💔\n" \
                  f"Your final score is {quiz.score}/{quiz.question_number}\n" \
                  f"Click /start to start a new quiz, /change_topic, /change_difficulty or view /stats"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            game_started = False
            # update quiz_db table
            cursor.execute(
                "UPDATE quiz_db SET game_started = %s WHERE chat_id = %s",
                ('false', chat_id)
            )
            # update stats table
            update_stats_table(cur_stats, quiz, userid, chosen_topic, chosen_difficulty)
        else:
            msg = f"💕 Remaining lives: {quiz.lives}\n" \
                  f"📊 Current score: {quiz.score}/{quiz.question_number}"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            quiz.next_question(bot, chat_id, msg_id)
            if quiz.game_is_over:  # if there is no more questions in db
                update_stats_table(cur_stats, quiz, userid, chosen_topic, chosen_difficulty)
                game_started = False
            # update quiz_db table
            pickled_quiz = pickle.dumps(quiz)
            cursor.execute(
                "UPDATE quiz_db SET quiz = %s WHERE chat_id = %s",
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
            # update quiz_db table
            cursor.execute(
                "UPDATE quiz_db SET game_started = %s WHERE chat_id = %s",
                ('false', chat_id)
            )
            # update stats table
            update_stats_table(cur_stats, quiz, userid, chosen_topic, chosen_difficulty)
        else:
            msg = f"💕 Remaining lives: {quiz.lives}\n" \
                  f"📊 Current score: {quiz.score}/{quiz.question_number}"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            quiz.next_question(bot, chat_id, msg_id)
            if quiz.game_is_over:  # if there is no more questions in db
                update_stats_table(cur_stats, quiz, userid, chosen_topic, chosen_difficulty)
                game_started = False
            # update quiz_db table
            pickled_quiz = pickle.dumps(quiz)
            cursor.execute(
                "UPDATE quiz_db SET quiz = %s WHERE chat_id = %s",
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
              "Game settings can be changed only if the Quiz is not started.\n" \
              "Click /stats to view statistics or /clear_stats to erase every game record.\n" \
              "Bot creator's telegram username: @tima_1j ⚙"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/stats":
        cur_stats.execute(
            "SELECT username, difficulty, topic, score FROM stats WHERE id = %s",
            (userid,))
        stats_rows = cur_stats.fetchall()

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
                msg = "Sadly, you either haven't played anything or called /clear_stats or there is something wrong with statistics (see /help)."
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    elif text == "/clear_stats":
        cur_stats.execute("DROP TABLE stats")
        msg = "Stats cleared."
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
