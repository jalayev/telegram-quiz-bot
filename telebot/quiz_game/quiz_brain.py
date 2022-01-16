import random


class QuizBrain:

    def __init__(self, question_list, lives_num):
        self.question_list = question_list
        self.question_number = 0
        self.score = 0
        self.lives = lives_num
        self.game_is_over = False
        self.current_question = self.question_list[0]

    def has_questions(self):
        return self.question_number < len(self.question_list)

    def check_answer(self, bot, chat_id, msg_id, user_answer):
        correct_answer = ""
        if self.current_question.answer.lower() == user_answer:
            correct_answer += "That's right  ✅  "
            self.score += 1
        else:
            correct_answer += "That's wrong  ❌  "
            self.lives -= 1
            if self.lives == 0:
                self.game_is_over = True
        correct_answer += f"The correct answer was: {self.current_question.answer}."
        bot.sendMessage(chat_id=chat_id, text=correct_answer, reply_to_message_id=msg_id)
        del self.current_question

    def next_question(self, bot, chat_id, msg_id):
        if not self.has_questions():
            msg = "✨🏆✨ There is no more questions, you win ✨🏆✨\n" \
                  f"📊 Your final score: {self.score}/{self.question_number}\n" \
                   "Click /start to start a new quiz, /change_topic, /change_difficulty or view /stats"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            self.game_is_over = True
            return
        rand_ind = random.randint(0, len(self.question_list) - 1)
        self.current_question = self.question_list[rand_ind]
        self.question_number += 1

        question_text = f"Q.{self.question_number}: {self.current_question.text} /true or /false ❔: "
        bot.sendMessage(chat_id=chat_id, text=question_text, reply_to_message_id=msg_id)
