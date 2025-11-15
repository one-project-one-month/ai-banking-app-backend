from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from utils import model_cam

camera_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage camera lifecycle"""
    global camera_instance
    try:
        camera_instance = model_cam.OpenCam()
        print("Camera initialized successfully")
    except Exception as e:
        print(f"Failed to initialize camera: {e}")
        camera_instance = None

    yield

    # Cleanup
    if camera_instance:
        try:
            camera_instance.release()
            print("Camera released successfully")
        except Exception as e:
            print(f"Error releasing camera: {e}")


app = FastAPI(
    title="Face Recognition API",
    description="API for face pose detection and login verification",
    lifespan=lifespan,
)


@app.get("/api/camera/stream")
async def stream_camera():
    """
    Stream camera feed with face pose detection overlay
    """
    global camera_instance

    if camera_instance is None:
        raise HTTPException(status_code=503, detail="Camera not available")

    try:
        return StreamingResponse(
            camera_instance.generate_frames(),
            media_type="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming error: {str(e)}")


@app.get("/api/face/status")
async def get_login_status():
    """
    Get current login verification status
    """
    global camera_instance

    if camera_instance is None:
        raise HTTPException(status_code=503, detail="Camera not available")

    return {
        "current_step": camera_instance.current_step,
        "total_steps": len(camera_instance.login_seq),
        "current_pose_required": (
            camera_instance.login_seq[camera_instance.current_step]
            if camera_instance.current_step < len(camera_instance.login_seq)
            else None
        ),
        "login_finished": camera_instance.login_finished,
        "progress_percentage": (
            camera_instance.current_step / len(camera_instance.login_seq)
        )
        * 100,
    }


@app.post("/api/face/reset")
async def reset_login():
    """
    Reset the login verification process
    """
    global camera_instance

    if camera_instance is None:
        raise HTTPException(status_code=503, detail="Camera not available")

    camera_instance.current_step = 0
    camera_instance.login_finished = False
    camera_instance.pose_start_time = None

    return {"message": "Login process reset successfully"}


@app.get("/api/face/sequence")
async def get_login_sequence():
    """
    Get the required pose sequence for login
    """
    global camera_instance

    if camera_instance is None:
        raise HTTPException(status_code=503, detail="Camera not available")

    return {
        "sequence": camera_instance.login_seq,
        "hold_time": camera_instance.hold_time,
    }


@app.get("/api/camera/info")
async def camera_info():
    """
    Get camera and system information
    """
    global camera_instance

    if camera_instance is None:
        raise HTTPException(status_code=503, detail="Camera not available")

    return {
        "camera_available": True,
        "detection_confidence": 0.5,
        "tracking_confidence": 0.5,
        "status": "ready",
    }


@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Face Recognition API",
        "endpoints": {
            "stream": "/api/camera/stream",
            "status": "/api/face/status",
            "reset": "/api/face/reset",
            "sequence": "/api/face/sequence",
            "info": "/api/camera/info",
        },
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
