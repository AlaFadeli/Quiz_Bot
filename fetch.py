import requests
import json

base_url = "https://api.fs-quiz.eu/2/quiz/{}"
max_id = 104
cv_quizzes = []

for quiz_id in range(1, max_id+1):
    try:
        resp = requests.get(base_url.format(quiz_id))
        print(resp.status_code)
        if resp.status_code == 200:
            quiz = resp.json()
            if quiz.get("class") == "cv":
                cv_quizzes.append(quiz)
                print(f"Found CV quiz: {quiz_id}")
        else:
            print(f"Skipped {quiz_id}")
    except Exception as e:
        print(f"Error with quiz {quiz_id}: {e}")



with open("cv_quizzes.json", "w", encoding="utf-8") as f:
    json.dump(cv_quizzes, f, indent = 2, ensure_ascii = False)
print(f"Saved{len(cv_quizzes)} CV quizzes to cs_quizzes.json")

