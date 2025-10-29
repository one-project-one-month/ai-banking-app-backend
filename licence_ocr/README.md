# AI Banking App Backend (NRC-OCR)

A FastAPI-based backend application for AI-powered banking services, featuring OCR capabilities for document processing including license and passport recognition.

## Features

- **Document OCR Processing**: Extract text from license and passport images
- **FastAPI REST API**: High-performance async API endpoints
- **gRPC**: High-performance async protobufs endpoints
- **Error Monitoring**: Integrated Sentry for error tracking and monitoring
- **Image Preprocessing**: Advanced image enhancement for better OCR accuracy
- **Comprehensive Testing**: Unit tests for OCR functionality

## Tech Stack

- **Python**: 3.11.13
- **FastAPI**: Modern, fast web framework for building APIs
- **gRPC**: Modern open source high performance Remote Procedure Call (RPC) framework 
- **OpenCV**: Computer vision library for image processing
- **Tesseract OCR**: Optical character recognition engine
- **Sentry**: Error monitoring and performance tracking
- **Uvicorn**: ASGI server for FastAPI

## Project Structure

```
licence_ocr/
├── api_endpoint
│   ├── Dockerfile
│   ├── gRPC
│   │   ├── ocr_client.py
│   │   ├── ocr_grpc_model.py
│   │   ├── ocr_pb2_grpc.py
│   │   ├── ocr_pb2.py
│   │   ├── ocr_server.py
│   │   └── ocr.proto
│   ├── main.py
│   ├── ocr_model_work.ipynb
│   └── utils
│       ├── __init__.py
│       └── model_ocr.py
└── README.md
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-banking-app-backend/licence_ocr/api_endpoint
   ```

2. **Install dependencies using pipenv**
   ```bash
   pipenv install
   ```

3. **Activate the virtual environment**
   ```bash
   pipenv shell
   ```

4. **Install Tesseract OCR**
   - **macOS**: `brew install tesseract`
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **Windows**: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

## Usage

### gRPC Server & Client 

The `licence_ocr/api_endpoint/gRPC/` directory provides a gRPC-based interface for OCR services, in addition to the REST API.

**Key files:**

- `ocr_server.py`: gRPC server for OCR processing
- `ocr_client.py`: Example gRPC client
- `ocr_pb2.py`, `ocr_pb2_grpc.py`: Generated from `ocr.proto` (do not edit manually)
- `ocr_grpc_model.py`: Model logic for gRPC

#### Running the gRPC Server

```bash
cd licence_ocr/api_endpoint/gRPC
python ocr_server.py
```

#### Running the gRPC Client

```bash
python ocr_client.py
```

#### Regenerating gRPC Code 

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ocr.proto
```

---


### Starting the API Server in *licence_ocr/api_endpoint* directory

```bash
uvicorn main:app --reload --port 5001 
```

The server will start on `http://127.0.0.1:5001/`

### API Endpoints

#### OCR Processing
- **POST** `/ocr`
  - **Description**: Process license or passport images for text extraction
  - **Parameters**:
    - `file`: Image file (UploadFile)
    - `class_name`: Document type - either "passport" or "licence" (Form)
  - **Response**: JSON with extracted text data

## Docker 
### Docker build
```
docker build -f licence_ocr/api_endpoint/Dockerfile -t nrc-ocr .
```

### Docker run 

```bash
docker run -p 5001:5000 nrc-ocr
```


**Example Request:**
```bash
curl -X POST "http://127.0.0.1:5001/ocr" \
  -F "file=@path/to/your/image.jpg" \
  -F "class_name=licence"
```

**Example Response:**
```json
{
  "data": {
    "kyc": "123456A",
    "dateOfBirth": "XXXX-XX-XX"
  }
}
```

## Testing

Run the unit tests to verify OCR functionality:

```bash
python tests/test_ocr.py
```

## OCR Capabilities

### License OCR
- **Pattern Recognition**: Extracts NRC (National Registration Card) numbers and DOB
- **Format**: `DD/NAME(N)XXXXXXX` where:
  - `DD`: 1-2 digit day
  - `NAME`: Name in uppercase letters
  - `N`: Literal "N"
  - `XXXXXXX`: 5-7 digit/alphanumeric code
- **Preprocessing**: Brightness and contrast enhancement for better accuracy

### Passport OCR
- **Pattern Recognition**: Extracts passport numbers and DOB
- **Format**: `XX########` where:
  - `XX`: 1-2 uppercase letters
  - `########`: 6-8 digits
- **Preprocessing**: Grayscale conversion for optimal text recognition

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
SENTRY_DSN=your_sentry_dsn_here
```

### Sentry Integration

The application includes Sentry integration for:
- Error tracking and monitoring
- Performance monitoring
- Transaction tracing for OCR operations


## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:5001/docs`
- **ReDoc**: `http://localhost:5001/redoc`

