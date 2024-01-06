import cv2
import numpy as np
import dlib
import pickle
import tkinter as tk
from PIL import Image, ImageTk
import requests
from datetime import datetime
def call_save(user_id,date_time):
    url = "http://127.0.0.1:5023/unknow"
    payload = {'user_id': user_id,'date_time': date_time}
    headers = {}
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        # Handle exceptions here
        print(f"An error occurred: {e}")
        return None  # or raise a custom exception, log, etc.

# Function to update the video feed
old_name = ""
def update_frame():
    global old_name
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to capture frame")
        root.destroy()  # Close the Tkinter window if frame capture fails
        return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    my_label.config(text = "###############")

    for (x, y, w, h) in faces:
        img = frame[y-10:y+h+10, x-10:x+w+10][:, :, ::-1]

        dets = detector(img, 1)
        for k, d in enumerate(dets):
            shape = sp(img, d)
            face_desc0 = model.compute_face_descriptor(img, shape, 1)

            d = []
            for face_new in FACE_DESC:
                d.append(np.linalg.norm(face_new - face_desc0))
            d = np.array(d)
            idx = np.argmin(d)
            
            if d[idx] < 0.4:
                name = FACE_NAME[idx]
                current_datetime = datetime.now()
                formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                my_label.config(text = name + ", time : " + formatted_datetime + ", status = "+ " ## save success ## ")
                if old_name != name:
                    old_name = name
                    print(name)
                    call_save(name,formatted_datetime)
                cv2.putText(frame, name, (x, y-5), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 2)
            else:
                update_trainset()
                cv2.putText(frame, "unknow", (x, y-5), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 2)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # Convert the OpenCV frame to a PIL Image
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    # Convert the PIL Image to a Tkinter-compatible format
    img_tk = ImageTk.PhotoImage(image=img)

    # Update the label with the new image
    label.config(image=img_tk)
    label.image = img_tk

    # Call this function again after 10 milliseconds
    if not stop_flag:
        root.after(10, update_frame)
    else:
        root.destroy()  # Close the Tkinter window when stop_flag is True

# Function to stop the video feed and exit the program
def stop_video():
    global stop_flag
    stop_flag = True
    cap.release()

def update_trainset():
    global FACE_DESC, FACE_NAME
    FACE_DESC, FACE_NAME = pickle.load(open('trainset.pk', 'rb'))

# Load face recognition models
face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
model = dlib.face_recognition_model_v1('dlib_face_recognition_resnet_model_v1.dat')
FACE_DESC, FACE_NAME = pickle.load(open('trainset.pk', 'rb'))

# Create the main Tkinter window
root = tk.Tk()
root.title("Face Recognition")

# Create a label for displaying the video feed
label = tk.Label(root)
label.pack()

# Create a "Stop" button
my_label = tk.Label(root, text = "###############")
my_label.pack()
stop_button = tk.Button(root, text="Stop", command=stop_video)
stop_button.pack()

# Open the video capture
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera")
    root.destroy()  # Close the Tkinter window if the camera fails to open


# Variable to indicate whether to stop the video feed
stop_flag = False

# Call the update_frame function to start the video feed
update_frame()

# Start the Tkinter event loop
root.mainloop()
