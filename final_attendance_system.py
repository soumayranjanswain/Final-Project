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
    """Function to speak text using Windows text-to-speech"""
    speak = Dispatch(("SAPI.SpVoice"))
    speak.Speak(str1)

def create_dynamic_background(width=1280, height=720):
    # Create an empty image
    img = np.zeros((height, width, 3), dtype=np.uint8)

    # Create vertical gradient from dark blue to lighter blue
    for y in range(height):
        blue_intensity = 50 + int((y / height) * 100)  # from 50 to 150
        img[y, :, :] = (blue_intensity, blue_intensity // 2, 100)  # BGR format

    # Add styled text "INNOVATIVE TECHNOLOGIES"
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "INNOVATIVE", (20, 50), font, 2, (255, 255, 255), 3, cv2.LINE_AA)
    cv2.putText(img, "TECHNOLOGIES", (20, 120), font, 2, (200, 200, 255), 3, cv2.LINE_AA)

    # Add placeholder smaller text below
    cv2.putText(img, "Learn from data to make", (20, 180), font, 1, (180, 180, 255), 1, cv2.LINE_AA)
    cv2.putText(img, "decisions and gain deep", (20, 220), font, 1, (180, 180, 255), 1, cv2.LINE_AA)
    cv2.putText(img, "quantum ideas", (20, 260), font, 1, (180, 180, 255), 1, cv2.LINE_AA)

    return img

# Create Attendance directory if it doesn't exist
if not os.path.exists('Attendance'):
    os.makedirs('Attendance')

# Initialize camera
video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

if not video.isOpened():
    print("❌ Error: Could not access the camera")
    exit()

# Load trained face data and names
with open('data/names.pkl', 'rb') as w:
    LABELS = pickle.load(w)
with open('data/faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)

print('Shape of Faces matrix --> ', FACES.shape)

# Train KNN classifier
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

# Generate dynamic background with gradient and styled text
imgBackground = create_dynamic_background()

COL_NAMES = ['NAME', 'TIME']

print("Face Recognition Attendance System Started!")
print("Press 'o' to take attendance")
print("Press 'q' to quit")

attendance_list = []  # List to hold all detected attendances

while True:
    ret, frame = video.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    # Convert to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    # Clear attendance_list for each frame
    attendance_list = []

    for (x, y, w, h) in faces:
        # Crop and resize face for recognition
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)

        # Predict the name
        output = knn.predict(resized_img)
        predicted_name = str(output[0])  # Get the predicted name

        # Get current timestamp
        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")
        exist = os.path.isfile("Attendance/Attendance_" + date + ".csv")

        # Draw face detection box and name
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 2)
        cv2.rectangle(frame, (x, y-40), (x+w, y), (0, 0, 255), -1)
        cv2.putText(frame, predicted_name, (x, y-15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

        # Add to attendance list
        attendance_list.append([predicted_name, str(timestamp)])

    # Display the frame with background
    # Resize frame to fit nicely on the right side of the background
    frame_resized = cv2.resize(frame, (640, 480))
    # Position the frame on the right side with some margin
    x_offset = imgBackground.shape[1] - 640 - 30
    y_offset = (imgBackground.shape[0] - 480) // 2
    imgBackground[y_offset:y_offset + 480, x_offset:x_offset + 640] = frame_resized

    cv2.imshow("Face Recognition Attendance System", imgBackground)
    k = cv2.waitKey(1)

    # Take attendance when 'o' is pressed
    if k == ord('o'):
        if attendance_list:
            speak(f"Attendance Taken for {len(attendance_list)} person(s)")
            time.sleep(2)
            with open("Attendance/Attendance_" + date + ".csv", "a", newline='') as csvfile:
                writer = csv.writer(csvfile)
                if not exist:
                    writer.writerow(COL_NAMES)  # Write header if file is new
                for attendance in attendance_list:
                    writer.writerow(attendance)
                    print(f"✅ Attendance recorded: {attendance[0]} at {attendance[1]}")
        else:
            speak("No faces detected for attendance")
            print("⚠️ No faces detected")

    # Quit when 'q' is pressed
    if k == ord('q'):
        break

# Cleanup
video.release()
cv2.destroyAllWindows()
print("Attendance system closed.")
