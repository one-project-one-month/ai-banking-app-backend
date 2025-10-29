from utils import chat_model_work
from db_access import RetrieveData
from fastapi import FastAPI
import uvicorn 
from contextlib import asynccontextmanager
from schema import textRequest
import mlflow 
import os
import traceback 

model = {}

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))  
mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the Refactor model on startup and clean up on shutdown."""
    model_work = chat_model_work.RefactorModel() # RefactorModel
    model['RefactorModel'] = model_work 
    yield 

    model.clear()

app = FastAPI(lifespan=lifespan)

@app.post("/queryRequest")
@mlflow.trace
def request_text(textRequest: textRequest) -> str:
    """Request Model"""
    db = RetrieveData()
    db.connect()
    db.user_input = textRequest.SQL_QUERY

    with mlflow.start_run(run_name="API_Request_Run"):
        mlflow.log_param("input_query", textRequest.SQL_QUERY)
        try:
            ques_ret = db.retrieve_questions()
            ans_ret = db.retrieve_answers()
            concat_qa = db.concat(ques_ret, ans_ret)
            pre_dc = db.preprocessing_doc()
            take_sim = db.most_sim(concat_qa, pre_dc)
            
            result_work = model['RefactorModel'].model_work(take_sim)

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