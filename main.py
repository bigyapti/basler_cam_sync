import threading
import cv2
from camera_control import setup_cameras, stop_cameras
from frame_processing import save_frame, create_video
from utils import create_output_dir
import numpy as np
import datetime
import traceback

NUM_CAMERAS = 4

# Start grabbing
cam_array = setup_cameras(NUM_CAMERAS)

cam_array.StartGrabbing()

# Define a variable to keep track of any exceptions
exception_occurred = False

def trigger_and_grab(cam, start_barrier, end_barrier, frame_success, output_dir):
    global exception_occurred
    try:
        while True:
            start_barrier.wait()  # Wait for all threads to reach the barrier before starting grabbing
            cam.ExecuteSoftwareTrigger()
            try:
                with cam.RetrieveResult(1000) as res:
                    if res.GrabSucceeded():
                        img_nr = res.ImageNumber
                        cam_id = cam.GetCameraContext()
                        current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')[:-3]
                        print(f"Camera #{cam_id} | Image #{img_nr} | Time: {current_time}")

                        # Convert grabbed frame to numpy array
                        frame = np.array(res.Array)
                        
                        # Record that this frame was successfully grabbed for this camera
                        frame_success[cam.GetCameraContext()] = True
                        
                        # Check if this frame was successfully grabbed for all cameras
                        if all(frame_success.values()):
                            # Resize the frame to a fixed size
                            frame = cv2.resize(frame, (640, 480))
                            cv2.imshow(f"Camera {cam.GetCameraContext()}", frame)
                            save_frame(frame, cam_id, img_nr, output_dir)
                        else:
                            print("Skipping frame: Not grabbed for all cameras")
                    else:
                        # Record that this frame failed to be grabbed for this camera
                        frame_success[cam.GetCameraContext()] = False
                        
            except RuntimeError as e:
                print(f"Error grabbing frame from cam #{cam.GetCameraContext()}: {str(e)}")
                frame_success[cam.GetCameraContext()] = False
            
            try:
                end_barrier.wait(timeout=20)  # Wait for all threads to reach the barrier before proceeding to the next frame
            except threading.BrokenBarrierError:
                print("Barrier is broken.")
                break
                
            if cv2.waitKey(1) == ord('q'):
                end_barrier.abort()
                

                
    except KeyboardInterrupt:
        print("Terminating program...")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        traceback.print_exc()
        exception_occurred = True
    finally:
        end_barrier.abort()  # Abort the barrier to ensure threads waiting on it are released

start_barrier = threading.Barrier(NUM_CAMERAS)
end_barrier = threading.Barrier(NUM_CAMERAS)
frame_success = {cam.GetCameraContext(): False for cam in cam_array}  # Initialize frame success status for each camera
output_dir = create_output_dir()
threads = []

try:
    for cam in cam_array:
        thread = threading.Thread(target=trigger_and_grab, args=(cam, start_barrier, end_barrier, frame_success, output_dir))
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

finally:
    stop_cameras(cam_array)
    for cam in cam_array:
        cam.Close()
    cv2.destroyAllWindows()

    for cam_id in range(NUM_CAMERAS):
        create_video(cam_id, output_dir)

    print("Video creation completed!")
