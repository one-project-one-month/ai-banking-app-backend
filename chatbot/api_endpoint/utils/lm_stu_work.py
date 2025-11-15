from openai import OpenAI
from db_access import RetrieveData
import os

base_url = os.getenv("LM_STUDIO")


class LM_Stu_Model:
    def __init__(self):
        pass

    def model_work(self, result_data: str):
        client = OpenAI(base_url=base_url, api_key="lm-studio")

        print(result_data)

        messages = [
            {
                "role": "system",
                "content": """
                - The tone is polite, professional, and grammatically correct.
                - The original meaning and context remain accurate.
                - If the text sounds too casual or emotional, rephrase it into a neutral and refined style.""",
            },
            {"role": "user", "content": result_data},
        ]

        response = client.chat.completions.create(
            model="llama-3.2-3b-instruct", messages=messages
        )

        return response.choices[0].message.content


if __name__ == "__main__":
    db = RetrieveData()
    db.connect()
    db.user_input = "How to login to banking account"
    ques_ret = db.retrieve_questions()
    ans_ret = db.retrieve_answers()
    db.close()
    concat_qa = db.concat(ques_ret, ans_ret)
    pre_dc = db.preprocessing_doc()
    take_sim = db.most_sim(concat_qa, pre_dc)

    model = LM_Stu_Model()
    result_work = model.model_work(take_sim)
    print(result_work)
