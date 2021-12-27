from telebot.quiz_game.question_model import *
from telebot.quiz_game.data import *
from telebot.quiz_game.quiz_brain import *


def quiz_start():
    question_bank = list()
    for mp in easy_general_questions:
        question_bank.append(Question(mp["question"], mp["correct_answer"]))
    quiz = QuizBrain(question_bank)
    return quiz



