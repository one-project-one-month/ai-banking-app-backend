import grpc
import chatbot_pb2, chatbot_pb2_grpc

channel = grpc.insecure_channel("localhost:50051")
stub = chatbot_pb2_grpc.chatbot_serviceStub(channel)

text = "How can i log in to banking account?"
request1 = chatbot_pb2.AddRequest(request=text)
response = stub.AddChatRequest(request1)
print(response.response)
