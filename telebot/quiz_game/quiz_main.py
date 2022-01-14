from telebot.quiz_game.question_model import *
from telebot.quiz_game.data import *
from telebot.quiz_game.quiz_brain import *


def quiz_start(topic, lives_num):
    question_bank = list()
    if topic == "general":
        for mp in general:
            question_bank.append(Question(mp["question"], mp["correct_answer"]))
    elif topic == "animation":
        for mp in animation:
            question_bank.append(Question(mp["question"], mp["correct_answer"]))
    elif topic == "history":
        for mp in history:
            question_bank.append(Question(mp["question"], mp["correct_answer"]))
    elif topic == "games":
        for mp in games:
            question_bank.append(Question(mp["question"], mp["correct_answer"]))
    elif topic == "films_tv":
        for mp in films_tv:
            question_bank.append(Question(mp["question"], mp["correct_answer"]))
    elif topic == "nature":
        for mp in nature:
            question_bank.append(Question(mp["question"], mp["correct_answer"]))
    elif topic == "science":
        for mp in science:
            question_bank.append(Question(mp["question"], mp["correct_answer"]))

    quiz = QuizBrain(question_bank, lives_num)
    return quiz



