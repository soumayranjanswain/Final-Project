import cv2
import pickle
import numpy as np
import os

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

if not video.isOpened():
    print("❌ Error: Could not access the camera")
    exit()

faces_data = []
i = 0

import sys
if len(sys.argv) > 1:
    name = sys.argv[1]
else:
    name = input("Enter Your Name: ")

print("Collecting face data... Press 'q' to stop or wait until 100 faces are collected")

while True:
    ret, frame = video.read()
    if not ret:
        print("❌ Failed to grab frame")
        break
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50, 50))

        # Collect face data (every 10th detection to avoid duplicates)
        if len(faces_data) < 100 and i % 10 == 0:
            faces_data.append(resized_img)

        i = i + 1
        cv2.putText(frame, str(len(faces_data)), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)
        cv2.putText(frame, name, (x, y-15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
    
    cv2.imshow("Frame", frame)
    k = cv2.waitKey(1)
    
    if k == ord('q') or len(faces_data) >= 100:
        break

video.release()
cv2.destroyAllWindows()

if len(faces_data) == 0:
    print("❌ No face data collected. Exiting...")
    exit()

# Process and save the collected face data
faces_data = np.asarray(faces_data)
faces_data = faces_data.reshape(len(faces_data), -1)  # Reshape based on actual number of faces

print(f"✅ Collected {len(faces_data)} face images for {name}")

# Save names data
if 'names.pkl' not in os.listdir('data/'):
    names = [name] * len(faces_data)
    with open('data/names.pkl', 'wb') as f:
        pickle.dump(names, f)
else:
    with open('data/names.pkl', 'rb') as f:
        names = pickle.load(f)
    names = names + [name] * len(faces_data)
    with open('data/names.pkl', 'wb') as f:
        pickle.dump(names, f)

# Save face data
if 'faces_data.pkl' not in os.listdir('data/'):
    with open('data/faces_data.pkl', 'wb') as f:
        pickle.dump(faces_data, f)
else:
    with open('data/faces_data.pkl', 'rb') as f:
        faces = pickle.load(f)
    faces = np.append(faces, faces_data, axis=0)
    with open('data/faces_data.pkl', 'wb') as f:
        pickle.dump(faces, f)

print(f"✅ Face data successfully saved for {name}")
