from groq import Groq
import os
from dotenv import load_dotenv
from utils.db_access import RetrieveData

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)


class RefactorModel:
    def __init__(self):
        pass

    def model_work(self, result_data: str):
        """Refactor Model work on db access"""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """
                - The tone is polite, professional, and grammatically correct.
                - The original meaning and context remain accurate.
                - If the text sounds too casual or emotional, rephrase it into a neutral and refined style.""",
                },
                {"role": "user", "content": result_data},
            ],
            temperature=1,
            max_completion_tokens=8192,
            top_p=1,
            # reasoning_effort="medium",
            # stream=True,
            # stop=None
        )

        result = completion

        return result.choices[0].message.content


# if __name__ == "__main__":
#    db = RetrieveData()
#    db.connect()
#    db.user_input = "How to login to banking account"
#    ques_ret = db.retrieve_questions()
#    ans_ret = db.retrieve_answers()
#    db.close()
#    concat_qa = db.concat(ques_ret, ans_ret)
#    pre_dc = db.preprocessing_doc(concat_qa)
#    take_sim = db.most_sim(concat_qa, pre_dc)

#   model = RefactorModel()
#    result_work = model.model_work(take_sim)
#    print(result_work)
