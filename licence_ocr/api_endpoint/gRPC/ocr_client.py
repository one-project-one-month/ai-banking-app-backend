import grpc
import ocr_pb2, ocr_pb2_grpc

# Connect to gRPC server
channel = grpc.insecure_channel("localhost:50051")
stub = ocr_pb2_grpc.nrc_ocr_serviceStub(channel)

# Licence OCR
with open(
    "/Users/yebhonelin/Documents/github/ai-banking-app-backend/IMG_6805.jpg", "rb"
) as f:
    licence_bytes = f.read()
request = ocr_pb2.AddLICENCEOCR(licence=licence_bytes)
response = stub.AddLicenceOCR(request)
print("Detected NRC:", response.output_nrc)
