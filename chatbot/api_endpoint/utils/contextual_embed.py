from sentence_transformers import SentenceTransformer, util
import os
import psycopg2
from dotenv import load_dotenv 

load_dotenv()

class ContextualEmbed:
    def __init__(self, embed_model: str = "google/embeddinggemma-300m"):
        self.model = SentenceTransformer(embed_model)
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
        return [q[0] for q in question_rows]

    def retrieve_answers(self):
        """Fetch all answers from the faq table."""
        self.cur.execute("SELECT answer FROM faq;")
        answer_rows = self.cur.fetchall()
        return [a[0] for a in answer_rows]
    
    def concat(self, questions, answers):
        """Pair questions with answers."""
        return dict(zip(questions, answers))
    
    def retrieve_embed(self, query, final_db):
        """Retrieve the most similar document to the query."""
        documents = list(final_db.keys())

        query_embedding = self.model.encode(query, convert_to_tensor=True)
        document_embeddings = self.model.encode(documents, convert_to_tensor=True)

        similarities = util.cos_sim(query_embedding, document_embeddings)
        ranking = similarities.argsort(descending=True)[0]

        threshold = 0.4 

        for idx in ranking:
            i = idx.item()
            score = similarities[0][i].item()
            if score > threshold:
                return final_db[documents[i]]
        return "There is no answer for you."

#if __name__ == "__main__":
#    db = ContextualEmbed()
#    db.connect()

#    query = "လိမ်လည်မှုကို ဘယ်လိုကာကွယ်ရမလဲ"
#    questions = db.retrieve_questions()
#    answers = db.retrieve_answers()
#    db.close()

#    final_db = db.concat(questions, answers)
#    response = db.retrieve_embed(query, final_db)
