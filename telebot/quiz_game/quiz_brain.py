import random


class QuizBrain:

    def __init__(self, question_list):
        self.question_list = question_list
        self.question_number = 0
        self.score = 0
        self.lives = 3
        self.game_is_over = False

    def has_questions(self):
        return self.question_number < len(self.question_list)

    def check_answer(self, current_question, user_answer):
        if current_question.answer.lower() == user_answer:
            print("That's right.")
            self.score += 1
        else:
            print("That's wrong.")
            self.lives -= 1
            if self.lives == 0:
                self.game_is_over = True
        print(f"The correct answer was: {current_question.answer}.")

    def next_question(self, user_answer):
        rand_ind = random.randint(0, len(self.question_list) - 1)
        current_question = self.question_list[rand_ind]
        self.question_number += 1
        # user_answer = input(f"Q.{self.question_number}: {current_question.text} (True/False)?: ").lower()

        self.check_answer(current_question, user_answer)

        if not self.game_is_over:
            print(f"Remaining lives: {self.lives}")
            print(f"Your current score is: {self.score}/{self.question_number}\n")
            del self.question_list[rand_ind]
        else:
            print("The game is over.")