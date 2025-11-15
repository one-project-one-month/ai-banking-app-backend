import numpy as np
import cv2
import mediapipe as mp
import time
import asyncio


class OpenCam:
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise Exception("Cannot open camera")

        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.smile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_smile.xml"
        )

        self.login_seq = ["Looking Left", "Looking Right", "Looking Up", "Smile"]
        self.current_step = 0
        self.login_finished = False
        self.hold_time = 1.0
        self.pose_start_time = None

    def detect_pose(self, image):
        """Detect face pose from image"""
        img_h, img_w, _ = image.shape
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.3, minNeighbors=5
        )

        pose = "Unknown"

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                face_2d, face_3d = [], []

                for idx, lm in enumerate(face_landmarks.landmark):
                    if idx in [33, 263, 1, 61, 291, 199]:
                        if idx == 1:
                            nose_2d = (lm.x * img_w, lm.y * img_h)
                            nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 3000)
                        x, y = int(lm.x * img_w), int(lm.y * img_h)
                        face_2d.append([x, y])
                        face_3d.append([x, y, lm.z])

                if len(face_2d) >= 6:  # Ensure we have enough points
                    face_2d = np.array(face_2d, dtype=np.float64)
                    face_3d = np.array(face_3d, dtype=np.float64)

                    focal_length = img_w
                    cam_matrix = np.array(
                        [
                            [focal_length, 0, img_h / 2],
                            [0, focal_length, img_w / 2],
                            [0, 0, 1],
                        ]
                    )
                    distortion_matrix = np.zeros((4, 1), dtype=np.float64)

                    success, rotation_vec, translation_vec = cv2.solvePnP(
                        face_3d, face_2d, cam_matrix, distortion_matrix
                    )

                    if success:
                        rmat, _ = cv2.Rodrigues(rotation_vec)
                        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

                        x_angle = angles[0] * 360
                        y_angle = angles[1] * 360

                        if y_angle < -3:
                            pose = "Looking Left"
                        elif y_angle > 3:
                            pose = "Looking Right"
                        elif x_angle > 3:
                            pose = "Looking Up"

        for x, y, w, h in faces:
            roi_gray = gray[y : y + h, x : x + w]
            smiles = self.smile_cascade.detectMultiScale(
                roi_gray, scaleFactor=1.8, minNeighbors=20, minSize=(25, 25)
            )
            if len(smiles) > 0:
                pose = "Smile"

        return pose

    def process_login_step(self, pose):
        """Process current login step"""
        if not self.login_finished:
            expected = self.login_seq[self.current_step]

            if pose == expected:
                if self.pose_start_time is None:
                    self.pose_start_time = time.time()
                elif time.time() - self.pose_start_time >= self.hold_time:
                    self.current_step += 1
                    self.pose_start_time = None
                    if self.current_step >= len(self.login_seq):
                        self.login_finished = True
            else:
                self.pose_start_time = None

    def add_overlay_text(self, image, pose):
        """Add text overlay to image"""
        if not self.login_finished:
            expected = self.login_seq[self.current_step]
            cv2.putText(
                image,
                f"Do: {expected}",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 0),
                2,
            )

            # Show progress
            progress = f"{self.current_step}/{len(self.login_seq)}"
            cv2.putText(
                image,
                f"Progress: {progress}",
                (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 0),
                2,
            )
        else:
            cv2.putText(
                image,
                "Login Successful!",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 0),
                3,
            )

        cv2.putText(
            image,
            f"Pose: {pose}",
            (20, 420),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 255),
            2,
        )

        return image

    async def generate_frames(self):
        """Generate frames for FastAPI streaming"""
        while True:
            success, image = self.cap.read()
            if not success:
                break

            image = cv2.flip(image, 1)

            pose = self.detect_pose(image)

            self.process_login_step(pose)

            image = self.add_overlay_text(image, pose)

            ret, buffer = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if not ret:
                continue

            frame = buffer.tobytes()

            # Yield frame in multipart format
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

            await asyncio.sleep(0.033)

    def release(self):
        """Release camera resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
