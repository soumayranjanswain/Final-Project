import customtkinter as ctk
import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk, ImageDraw, ImageFilter
from customtkinter import CTkImage
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from threading import Thread
from win32com.client import Dispatch

# Text-to-speech function
def speak(text):
    speaker = Dispatch("SAPI.SpVoice")
    speaker.Speak(text)

# Custom widget for rounded frame with glowing border
class RoundedFrame(ctk.CTkFrame):
    def __init__(self, master=None, width=300, height=300, corner_radius=30, glow_color="#6a5acd", glow_width=10, **kwargs):
        super().__init__(master, width=width, height=height, corner_radius=corner_radius, **kwargs)
        self.glow_color = glow_color
        self.glow_width = glow_width
        self._corner_radius = corner_radius
        self.canvas = tk.Canvas(self, width=width, height=height, highlightthickness=0, bg=self._fg_color)
        self.canvas.place(x=0, y=0)
        self.bind("<Configure>", self._draw_glow)

    def _draw_glow(self, event=None):
        self.canvas.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        radius = self._corner_radius
        glow_w = self.glow_width

        # Create an image with glow effect
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw rounded rectangle
        rect = [glow_w, glow_w, w - glow_w, h - glow_w]
        draw.rounded_rectangle(rect, radius, fill=self._fg_color)

        # Create glow by blurring
        glow = img.filter(ImageFilter.GaussianBlur(glow_w))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.rounded_rectangle(rect, radius, fill=self.glow_color+(100,))

        # Composite glow and rectangle
        combined = Image.alpha_composite(glow, img)

        self.glow_img = ImageTk.PhotoImage(combined)
        self.canvas.create_image(0, 0, anchor="nw", image=self.glow_img)

# Animated label for color-changing title
class AnimatedLabel(ctk.CTkLabel):
    def __init__(self, master=None, text="", font=None, colors=None, delay=100, **kwargs):
        super().__init__(master, text=text, font=font, **kwargs)
        self.colors = colors or ["#6a5acd", "#483d8b", "#7b68ee", "#9370db"]
        self.delay = delay
        self.color_index = 0
        self.after(self.delay, self._animate)

    def _animate(self):
        self.configure(text_color=self.colors[self.color_index])
        self.color_index = (self.color_index + 1) % len(self.colors)
        self.after(self.delay, self._animate)

class FaceRecognitionApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("INNOVATIVE TECHNOLOGIES - Face Recognition Attendance System")
        self.geometry("1280x720")
        self.resizable(False, False)

        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Gradient background canvas
        self.bg_canvas = tk.Canvas(self, width=1280, height=720, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0)
        self._draw_gradient("#6a5acd", "#0000ff")

        # Glass effect panel for title
        self.title_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=20, border_width=2, border_color="#ffffff", width=400, height=60)
        self.title_frame.place(relx=0.5, y=40, anchor="center")

        # Animated title inside glass panel
        title_font = ctk.CTkFont(family="Montserrat", size=28, weight="bold")
        self.title_label = AnimatedLabel(self.title_frame, text="INNOVATIVE TECHNOLOGIES", font=title_font, colors=["#9b59b6", "#2980b9", "#8e44ad", "#3498db"], delay=200)
        self.title_label.place(relx=0.5, rely=0.5, anchor="center")

        # Webcam frame with rounded corners and glowing border
        self.webcam_frame = RoundedFrame(self, width=700, height=520, corner_radius=40, glow_color=(106, 90, 205), glow_width=15, fg_color="#1f1f2e")
        self.webcam_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Label inside webcam frame to show video
        self.video_label = ctk.CTkLabel(self.webcam_frame, text="")
        self.video_label.place(relx=0.5, rely=0.5, anchor="center")

        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.place(relx=0.5, y=680, anchor="center")

        self.attendance_button = ctk.CTkButton(self.buttons_frame, text="📷 Take Attendance", width=180, height=40, command=self.take_attendance, corner_radius=20, fg_color="#6a5acd", hover_color="#483d8b")
        self.attendance_button.grid(row=0, column=0, padx=20)

        self.stop_button = ctk.CTkButton(self.buttons_frame, text="⏸ Stop Camera", width=180, height=40, command=self.stop_camera, corner_radius=20, fg_color="#f39c12", hover_color="#e67e22")
        self.stop_button.grid(row=0, column=1, padx=20)

        self.quit_button = ctk.CTkButton(self.buttons_frame, text="🚪 Exit", width=180, height=40, command=self.quit_app, corner_radius=20, fg_color="#e74c3c", hover_color="#c0392b")
        self.quit_button.grid(row=0, column=2, padx=20)

        # Footer text
        footer_font = ctk.CTkFont(family="Montserrat", size=12)
        self.footer_label = ctk.CTkLabel(self, text="Powered by AI Smart Attendance System", font=footer_font, text_color="#888")
        self.footer_label.place(relx=0.5, y=710, anchor="center")

        # Digital clock
        self.clock_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(family="Montserrat", size=14), text_color="#fff")
        self.clock_label.place(relx=0.9, y=10, anchor="ne")
        self.update_clock()

        # Initialize face recognition components
        self.video = cv2.VideoCapture(0)
        self.facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

        with open('data/names.pkl', 'rb') as w:
            self.LABELS = pickle.load(w)
        with open('data/faces_data.pkl', 'rb') as f:
            self.FACES = pickle.load(f)

        from sklearn.neighbors import KNeighborsClassifier
        self.knn = KNeighborsClassifier(n_neighbors=1)
        self.knn.fit(self.FACES, self.LABELS)

        self.COL_NAMES = ['NAME', 'TIME']
        self.attendance_list = []

        self.running = True
        self.thread = Thread(target=self.video_loop)
        self.thread.start()

        self.bind("<KeyPress-o>", lambda e: self.take_attendance())
        self.bind("<KeyPress-q>", lambda e: self.quit_app())

    def update_clock(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.clock_label.configure(text=now)
        self.after(1000, self.update_clock)

    def _draw_gradient(self, color1, color2):
        # Draw vertical gradient on canvas
        width = 1280
        height = 720
        limit = height
        (r1, g1, b1) = self.winfo_rgb(color1)
        (r2, g2, b2) = self.winfo_rgb(color2)
        r_ratio = float(r2 - r1) / limit
        g_ratio = float(g2 - g1) / limit
        b_ratio = float(b2 - b1) / limit

        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = f'#{nr >> 8:02x}{ng >> 8:02x}{nb >> 8:02x}'
            self.bg_canvas.create_line(0, i, width, i, fill=color)

    def video_loop(self):
        while self.running:
            ret, frame = self.video.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.facedetect.detectMultiScale(gray, 1.3, 5)

            self.attendance_list.clear()

            for (x, y, w, h) in faces:
                crop_img = frame[y:y+h, x:x+w, :]
                resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
                output = self.knn.predict(resized_img)
                predicted_name = str(output[0])

                ts = time.time()
                timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")

                # Draw rounded rectangle around face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (106, 90, 205), 2)
                cv2.rectangle(frame, (x, y-40), (x+w, y), (106, 90, 205), -1)
                cv2.putText(frame, predicted_name, (x+5, y-10), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)

                self.attendance_list.append([predicted_name, timestamp])

            # Convert frame to RGB and resize to fit webcam frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (self.webcam_frame.winfo_width()-30, self.webcam_frame.winfo_height()-30))

            # Convert to CTkImage
            img = Image.fromarray(frame)
            width = self.webcam_frame.winfo_width() - 30
            height = self.webcam_frame.winfo_height() - 30
            ctk_img = CTkImage(light_image=img, size=(width, height))

            # Update video label
            self.video_label.configure(image=ctk_img)
            self.video_label.ctk_img = ctk_img

    def take_attendance(self):
        if not self.attendance_list:
            speak("No faces detected for attendance")
            return

        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        exist = os.path.isfile(f"Attendance/Attendance_{date}.csv")

        with open(f"Attendance/Attendance_{date}.csv", "a", newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not exist:
                writer.writerow(self.COL_NAMES)
            for attendance in self.attendance_list:
                writer.writerow(attendance)
                print(f"✅ Attendance recorded: {attendance[0]} at {attendance[1]}")

        speak(f"Attendance taken for {len(self.attendance_list)} person(s)")

    def stop_camera(self):
        self.running = False

    def quit_app(self):
        self.running = False
        self.thread.join()
        self.video.release()
        self.destroy()

if __name__ == "__main__":
    app = FaceRecognitionApp()
    app.mainloop()
