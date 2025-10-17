import os
import sys
import grpc
from concurrent import futures
import chatbot_pb2_grpc, chatbot_pb2
from utils.model_work import RefactorModel
from utils.db_access import RetrieveData

class RefactorChatbotService(chatbot_pb2_grpc.chatbot_serviceServicer):
    def AddChatRequest(self, request, context):
        db = RetrieveData()
        db.connect()
        db.user_input = request.request
        ques_ret = db.retrieve_questions()
        ans_ret = db.retrieve_answers()
        db.close()
        concat_qa = db.concat(ques_ret, ans_ret)
        pre_dc = db.preprocessing_doc(concat_qa)
        take_sim = db.most_sim(concat_qa, pre_dc)

        model = RefactorModel()
        result_work = model.model_work(take_sim)
        return chatbot_pb2.ResponseModel(response=result_work)
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chatbot_pb2_grpc.add_chatbot_serviceServicer_to_server(RefactorChatbotService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()