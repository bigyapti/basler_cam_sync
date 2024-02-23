import os
import datetime

def create_output_dir():
    output_dir = f"output_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir
