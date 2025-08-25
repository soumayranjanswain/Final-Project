from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from win32com.client import Dispatch

def speak(str1):
    speak = Dispatch(("SAPI.SpVoice"))
    speak.Speak(str1)

# Create Attendance directory if it doesn't exist
if not os.path.exists('Attendance'):
    os.makedirs('Attendance')

video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default (1).xml')  # Corrected filename

if not video.isOpened():
    print("❌ Error: Could not access the camera")
    exit()

with open('data/names.pkl', 'rb') as w:
    LABELS = pickle.load(w)
with open('data/faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)

print('Shape of Faces matrix --> ', FACES.shape)

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

# Check if background image exists, use photo_1.jpg if available
background_image_path = "background.png"
if os.path.exists(background_image_path):
    imgBackground = cv2.imread(background_image_path)
else:
    # Create a simple black background if no background image is found
    imgBackground = np.zeros((480+162, 640+55, 3), dtype=np.uint8)
    print("⚠️  No background image found. Using default black background.")

COL_NAMES = ['NAME', 'TIME']

while True:
    ret, frame = video.read()
    if not ret:
        print("❌ Failed to grab frame")
        break
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
        output = knn.predict(resized_img)
        predicted_name = str(output[0])  # Get the predicted name directly
        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")
        exist = os.path.isfile("Attendance/Attendance_" + date + ".csv")
        
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 2)
        cv2.rectangle(frame, (x, y-40), (x+w, y), (0, 0, 255), -1)  # Changed to red color
        cv2.putText(frame, predicted_name, (x, y-15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)  # Use predicted name
        
        attendance = [predicted_name, str(timestamp)]  # Use the predicted name directly
    
    imgBackground[162:162 + 480, 55:55 + 640] = frame
    cv2.imshow("soumya", imgBackground)  # Change window title to "soumya"
    k = cv2.waitKey(1)
    
    if k == ord('o'):
        speak("Attendance Taken..")
        time.sleep(5)
        with open("Attendance/Attendance_" + date + ".csv", "a", newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not exist:
                writer.writerow(COL_NAMES)  # Write header if file is new
            writer.writerow(attendance)
    
    if k == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
