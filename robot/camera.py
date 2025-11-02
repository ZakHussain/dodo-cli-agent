"""
Camera management with auto-detection for Doda Terminal
Supports OpenCV camera auto-detection with manual fallback
"""

import cv2
from typing import Optional, Tuple
import numpy as np
from pathlib import Path


class CameraManager:
    """Manages camera connection with auto-detection"""

    def __init__(self, preferred_index: Optional[int] = None):
        """
        Initialize camera manager

        Args:
            preferred_index: Preferred camera index (None for auto-detect)
        """
        self.camera_index: Optional[int] = None
        self.cap: Optional[cv2.VideoCapture] = None
        self.preferred_index = preferred_index

        # Auto-detect on init
        if preferred_index is not None:
            self.connect(preferred_index)
        else:
            self.auto_detect()

    def auto_detect(self) -> bool:
        """
        Auto-detect camera by trying indices 0, 1, 2

        Returns:
            True if camera found and connected
        """
        print("Auto-detecting camera...")

        for idx in [0, 1, 2]:
            print(f"  Trying camera index {idx}...")
            if self.connect(idx):
                print(f"  ✓ Camera found at index {idx}")
                return True
            else:
                print(f"  ✗ No camera at index {idx}")

        print("\n⚠ Camera auto-detection failed!")
        self._show_manual_fallback_instructions()
        return False

    def _show_manual_fallback_instructions(self):
        """Show instructions for manual camera detection"""
        print("\nManual camera detection:")
        print("1. Connect your camera")
        print("2. Run this Python command to detect:")
        print("   >>> import cv2")
        print("   >>> for i in range(5):")
        print("   >>>     cap = cv2.VideoCapture(i)")
        print("   >>>     if cap.isOpened():")
        print("   >>>         print(f'Camera found at index {i}')")
        print("   >>>         cap.release()")
        print("\n3. Set camera index in .env file or use --camera-index parameter")
        print("\nTo test what changed when camera unplugged:")
        print("- Run detection WITH camera connected")
        print("- Unplug camera")
        print("- Run detection again and compare indices")

    def connect(self, index: int) -> bool:
        """
        Connect to camera at specific index

        Args:
            index: Camera index to try

        Returns:
            True if connection successful
        """
        # Close existing connection
        if self.cap is not None:
            self.cap.release()
            self.cap = None

        # Try to open camera
        cap = cv2.VideoCapture(index)

        if not cap.isOpened():
            return False

        # Verify we can read a frame
        ret, frame = cap.read()
        if not ret or frame is None:
            cap.release()
            return False

        # Success
        self.cap = cap
        self.camera_index = index
        return True

    def is_connected(self) -> bool:
        """Check if camera is connected"""
        return self.cap is not None and self.cap.isOpened()

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from camera

        Returns:
            Frame as numpy array, or None if failed
        """
        if not self.is_connected():
            print("Error: Camera not connected")
            return None

        ret, frame = self.cap.read()
        if not ret or frame is None:
            print("Error: Failed to capture frame")
            return None

        return frame

    def save_frame(self, filename: str) -> bool:
        """
        Capture and save frame to file

        Args:
            filename: Path to save image

        Returns:
            True if successful
        """
        frame = self.capture_frame()
        if frame is None:
            return False

        # Ensure directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        # Save image
        success = cv2.imwrite(filename, frame)
        if success:
            print(f"Frame saved to {filename}")
        else:
            print(f"Error: Failed to save frame to {filename}")

        return success

    def get_info(self) -> dict:
        """Get camera information"""
        if not self.is_connected():
            return {
                "connected": False,
                "index": None,
                "width": None,
                "height": None,
                "fps": None
            }

        return {
            "connected": True,
            "index": self.camera_index,
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": int(self.cap.get(cv2.CAP_PROP_FPS))
        }

    def disconnect(self):
        """Disconnect camera"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.camera_index = None
            print("Camera disconnected")

    def __del__(self):
        """Cleanup on deletion"""
        self.disconnect()


def detect_cameras(max_index: int = 5) -> list:
    """
    Utility function to detect all available cameras

    Args:
        max_index: Maximum index to check

    Returns:
        List of available camera indices
    """
    available = []

    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                available.append(i)
        cap.release()

    return available


if __name__ == "__main__":
    # Run detection when script is executed directly
    print("Detecting cameras...")
    cameras = detect_cameras()

    if cameras:
        print(f"\n✓ Found {len(cameras)} camera(s) at indices: {cameras}")
    else:
        print("\n✗ No cameras detected")

    # Test first camera if available
    if cameras:
        print(f"\nTesting camera at index {cameras[0]}...")
        cam = CameraManager(preferred_index=cameras[0])

        if cam.is_connected():
            info = cam.get_info()
            print(f"Camera info: {info}")

            # Capture test frame
            test_path = "test_frame.jpg"
            if cam.save_frame(test_path):
                print(f"✓ Test frame saved to {test_path}")

        cam.disconnect()
