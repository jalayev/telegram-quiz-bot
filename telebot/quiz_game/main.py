from question_model import Question
from data import *
from quiz_brain import QuizBrain

question_bank = list()
for mp in easy_general_questions:
    question_bank.append(Question(mp["question"], mp["correct_answer"]))

# print(question_bank)
quiz = QuizBrain(question_bank)
# while quiz.has_questions() and not quiz.game_is_over:
#     quiz.next_question()

# print(f"\nYou have completed the quiz\nYour final score is: {quiz.score}/{quiz.question_number}")
