# Camera Detection Module

A real-time face pose detection and authentication system using computer vision and machine learning. This module provides secure login verification through facial pose sequences.

## Features

- **Real-time Face Detection**: Uses MediaPipe and OpenCV for accurate face detection
- **Pose Recognition**: Detects head movements (left, right, up) and facial expressions (smile)
- **Secure Authentication**: Multi-step pose sequence verification for enhanced security
- **Live Camera Streaming**: Real-time video feed with pose detection overlay
- **RESTful API**: FastAPI-based endpoints for integration with other services
- **Docker Support**: Containerized deployment with optimized dependencies

## Architecture

### Core Components

1. **OpenCam Class** (`model_cam.py`): Main camera and detection logic
2. **FastAPI Server** (`cam_api.py`): RESTful API endpoints
3. **Utils** (`utils.py`): Standalone camera testing script
4. **Web Interface** (`index.html`): Simple HTML viewer for camera stream

### Detection Pipeline

```
Camera Input → Face Detection → Pose Analysis → Sequence Verification → Authentication Result
```

## Installation

### Prerequisites

- Python 3.11+
- OpenCV
- MediaPipe
- FastAPI

### Local Development

1. **Install dependencies**:
   ```bash
   pip install opencv-python mediapipe fastapi uvicorn
   ```

2. **Run the standalone test**:
   ```bash
   python utils.py
   ```

3. **Start the API server**:
   ```bash
   cd api_endpoint
   uvicorn cam_api:app --host 0.0.0.0 --port 5006
   ```

### Docker Deployment

1. **Build the container**:
   ```bash
   docker build -t camera-detect .
   ```

2. **Run the container**:
   ```bash
   docker run -p 5006:5006 camera-detect
   ```

## API Endpoints

### Camera Streaming
- **GET** `/api/camera/stream` - Live camera feed with pose detection overlay
- **GET** `/api/camera/info` - Camera and system information

### Authentication
- **GET** `/api/face/status` - Current login verification status
- **POST** `/api/face/reset` - Reset the login verification process
- **GET** `/api/face/sequence` - Get required pose sequence

### General
- **GET** `/` - API information and available endpoints

## Usage Examples

### Basic Camera Stream
```bash
# View live camera feed
curl http://localhost:5006/api/camera/stream
```

### Check Authentication Status
```bash
curl http://localhost:5006/api/face/status
```

Response:
```json
{
  "current_step": 2,
  "total_steps": 4,
  "current_pose_required": "Looking Up",
  "login_finished": false,
  "progress_percentage": 50.0
}
```

### Reset Authentication
```bash
curl -X POST http://localhost:5006/api/face/reset
```

## Authentication Sequence

The system requires users to perform a specific sequence of poses:

1. **Looking Left** - Turn head to the left
2. **Looking Right** - Turn head to the right  
3. **Looking Up** - Tilt head upward
4. **Smile** - Show a smile

Each pose must be held for 1 second to be recognized.

## Technical Details

### Face Detection
- Uses MediaPipe Face Mesh for 468 facial landmarks
- OpenCV Haar Cascades for face and smile detection
- 3D pose estimation using solvePnP algorithm

### Pose Recognition
- **Head Movement**: Analyzes rotation angles from 3D face landmarks
- **Smile Detection**: Uses Haar cascade classifier for smile recognition
- **Confidence Thresholds**: 0.5 for detection and tracking confidence

### Performance
- **Frame Rate**: 30 FPS target
- **Resolution**: 640x480 default
- **Latency**: ~33ms per frame processing

## Configuration

### Camera Settings
```python
# Camera properties
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
self.cap.set(cv2.CAP_PROP_FPS, 30)
```

### Detection Parameters
```python
# MediaPipe settings
min_detection_confidence=0.5
min_tracking_confidence=0.5

# Pose hold time
hold_time = 3.0  # seconds
```

## Security Considerations

- **Liveness Detection**: Multi-step pose sequence prevents spoofing
- **Real-time Processing**: No stored biometric data
- **Session Management**: Reset capability for failed attempts
- **Privacy**: No persistent storage of facial data

## License

This module is part of the AI Banking App Backend project.

