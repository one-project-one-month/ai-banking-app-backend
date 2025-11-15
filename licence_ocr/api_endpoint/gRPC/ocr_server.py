from concurrent import futures

import grpc
import ocr_pb2
import ocr_pb2_grpc

from licence_ocr.api_endpoint.ocr_grpc_model import OCR_Model


class NrcOcrService(ocr_pb2_grpc.nrc_ocr_serviceServicer):
    def AddLicenceOCR(self, request, context):
        ocr = OCR_Model(image_bytes=request.licence)
        gray = ocr.preprocess_image_for_licence_ocr()
        nrc = ocr.licence_ocr_model(gray)

        return ocr_pb2.AddOutputNRC(output_nrc=nrc or "")

    def AddLicencePassport(self, request, context):
        ocr = OCR_Model(image_bytes=request.passport)
        gray = ocr.preprocess_image_for_passport_ocr()
        passport_no = ocr.passport_ocr_model(gray)
        return ocr_pb2.AddOutputNRC(output_nrc=passport_no or "")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ocr_pb2_grpc.add_nrc_ocr_serviceServicer_to_server(NrcOcrService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
