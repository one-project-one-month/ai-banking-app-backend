import os

import nltk
import psycopg2
from dotenv import load_dotenv
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize

nltk.download("punkt")

load_dotenv()


class RetrieveData:
    def __init__(self):
        self.user_input = None
        self.conn = None
        self.cur = None

    def connect(self):
        """Establish a database connection and create a cursor."""
        DB_URI = os.getenv("DB_URI")
        self.conn = psycopg2.connect(DB_URI)
        self.cur = self.conn.cursor()

    def close(self):
        """Close the cursor and connection cleanly."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def retrieve_questions(self):
        """Fetch all questions from the faq table."""
        self.cur.execute("SELECT question FROM faq;")
        question_rows = self.cur.fetchall()
        return question_rows

    def retrieve_answers(self):
        """Fetch all answers from the faq table."""
        self.cur.execute("SELECT answer FROM faq;")
        answer_rows = self.cur.fetchall()
        return answer_rows

    def concat(self, question_rows, answer_rows):
        """Structure the desire format"""
        concat_qa = dict(zip(question_rows, answer_rows))
        sg_q = [question[0] for question, answer in concat_qa.items()]
        sg_a = [answer[0] for question, answer in concat_qa.items()]
        final_db = dict(zip(sg_q, sg_a))
        return final_db

    def preprocessing_doc(self):
        """Tokenize the data"""
        # tokenized_data = [word_tokenize(document.lower()) for document in final_db]
        # tagged_data = [TaggedDocument(words=words, tags=[str(idx)])
        #       for idx, words in enumerate(tokenized_data)]
        model = Doc2Vec.load("doc2vec_model.model")
        inferred_vector = model.infer_vector(word_tokenize(self.user_input.lower()))
        similar_documents = model.dv.most_similar([inferred_vector], topn=len(model.dv))
        return similar_documents

    def most_sim(self, final_db, similar_documents):
        """Take most similarity data"""
        threshold = 0.8
        questions = list(final_db.keys())

        for index, score in similar_documents:
            index = int(index)

            if score < threshold:
                result_data = "There is no exact answer for that question"
                break
            else:
                question = questions[index]
                result_data = final_db[question]
                break

        return result_data


if __name__ == "__main__":
    db = RetrieveData()
    db.connect()
    db.user_input = "what is programming"
    ques_ret = db.retrieve_questions()
    ans_ret = db.retrieve_answers()
    db.close()
    concat_qa = db.concat(ques_ret, ans_ret)
    pre_dc = db.preprocessing_doc()
    take_sim = db.most_sim(concat_qa, pre_dc)
    print(take_sim)
