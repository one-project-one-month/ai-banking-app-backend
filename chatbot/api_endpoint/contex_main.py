from utils import contextual_embed, chat_model_work
from fastapi import FastAPI
import uvicorn 
from contextlib import asynccontextmanager
from schema import textRequest
import os
import mlflow 
import traceback 

api_related_model = {}

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))  
mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the Refactor Model and Embed Model on startup and clean up on shutdown."""
    chat_model = chat_model_work.RefactorModel()
    api_related_model['RefactorModel'] = chat_model 
    contextual_embed_work = contextual_embed.ContextualEmbed()
    api_related_model['ContextualEmbed'] = contextual_embed_work
    yield 

    api_related_model.clear()

app = FastAPI(lifespan=lifespan)

@app.post("/queryRequest")
@mlflow.trace
def request_text(textRequest: textRequest) -> str:
    """Request Model"""
    db = api_related_model["ContextualEmbed"]
    db.connect()
    
    with mlflow.start_run(run_name="Chatbot Request Run"):
        mlflow.log_param("input_query", textRequest.SQL_QUERY)
        try:
            query =  textRequest.SQL_QUERY
            questions = db.retrieve_questions()
            answers = db.retrieve_answers()
            db.close()

            final_db = db.concat(questions, answers)
            response = db.retrieve_embed(query, final_db)
            
            result_work = api_related_model['RefactorModel'].model_work(response)

            mlflow.log_param("model_output", result_work)
            return result_work
        
        except Exception as e:

            error_trace = traceback.format_exc()
            mlflow.log_param("error_type", error_trace)
            
            return {"Error Occured"}
        
        finally:
            db.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=5008, reload=True)