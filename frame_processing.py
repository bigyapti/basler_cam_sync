import cv2
import os
import datetime

def save_frame(frame, cam_id, img_nr, output_dir):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')[:-3]
    folder_path = os.path.join(output_dir, f"camera_{cam_id}")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    cv2.imwrite(os.path.join(folder_path, f"{current_time}_frame_{img_nr}.jpg"), frame)

def create_video(cam_id, output_dir):
    folder_path = os.path.join(output_dir, f"camera_{cam_id}")
    video_path = os.path.join(output_dir, f"camera_{cam_id}_output.avi")
    images = [img for img in os.listdir(folder_path) if img.endswith(".jpg")]
    frame = cv2.imread(os.path.join(folder_path, images[0]))
    height, width, layers = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video = cv2.VideoWriter(video_path, fourcc, 20.0, (width, height))
    for image in images:
        video.write(cv2.imread(os.path.join(folder_path, image)))
    cv2.destroyAllWindows()
    video.release()
