import requests
import random

class Answer:
    answer: str
    correct: bool

    def __init__(self, answer: str, correct: bool):
        self.answer = answer
        self.correct = correct


class Question:
    id: int
    prompt: str
    times_asked: int
    times_correct: int
    answers: list[Answer]

    def __init__(self, id: int, prompt: str, times_asked: int, times_correct: int, answers: list[Answer]):
        self.id = id
        self.prompt = prompt
        self.times_asked = times_asked
        self.times_correct = times_correct
        self.answers = answers


class API:
    def get_questions(self) -> list[Question]:
        raise NotImplementedError

    def post_answer(self, question: Question, answer: Answer):
        raise NotImplementedError


class User:
    def ask_question(self, question: Question) -> Answer:
        raise NotImplementedError

class WebAPI(API):
    url: str

    def __init__(self, url: str):
        self.url = url

    def get_questions(self) -> list[Question]:
        questions = []
        for question in requests.get(self.url).json()["questions"]:
            id = int(question["id"])
            prompt = question["prompt"]
            times_asked = question["times_asked"]
            times_correct = question["times_correct"]

            answers = [Answer(answer["answer"], answer["correct"]) for answer in question["answers"]]

            questions.append(Question(id, prompt, times_asked, times_correct, answers))

        return questions

    def post_answer(self, question: Question, answer: Answer):
        requests.post(self.url, json={"id": question.id, "correct": answer.correct})


class ConsoleUser(User):
    def ask_question(self, question: Question) -> Answer:
        print(question.prompt)
        for i, ans in enumerate(question.answers, start=1):
            print(f"{i}: {ans.answer}")

        user_answer = int(input(">"))
        return question.answers[user_answer-1]


class CheatingUser(User):
    def ask_question(self, question: Question) -> Answer:
        print(question.prompt)
        for i, ans in enumerate(question.answers, start=1):
            print(f"{i}: {ans.answer}")

        for ans in question.answers:
            if ans.correct:
                return ans


class Quiz:
    api: API
    user: User
    __questions: list[Question]

    def __init__(self, api: API, user: User, num_questions: int):
        self.api = api
        self.user = user
        self.__questions = random.sample(self.api.get_questions(), num_questions)

    def run(self):
        score = 0
        wrong_answers = []
        for question in self.__questions:
            ans = self.user.ask_question(question)
            if ans.correct:
                score += 1
                print("Correct!")
            else:
                print("Wrong!")
                wrong_answers.append(question)
            self.api.post_answer(question, ans)
        print(f"You got a score of {score}")
        print("Things you got wrong")
        for q in wrong_answers:
            print(q.prompt)

if __name__ == '__main__':
    api = WebAPI("https://bjornkjellgren.se/quiz/v2/questions")
    user = ConsoleUser()
    #user = CheatingUser()
    quiz = Quiz(api, user, 5)
    quiz.run()
