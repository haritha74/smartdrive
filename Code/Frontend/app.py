from flask import Flask,render_template,redirect,request,url_for, send_file,flash,Response
import mysql.connector
from ultralytics import YOLO
import cv2
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread
import os
import numpy as np


app = Flask(__name__)

# MySQL connection setup
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3306",
    database='smartdriver'
)
mycursor = mydb.cursor()

#MySQL query functions
def executionquery(query, values):
    mycursor.execute(query, values)
    mydb.commit()

def retrivequery1(query, values):
    mycursor.execute(query, values)
    return mycursor.fetchall()

def retrivequery2(query):
    mycursor.execute(query)
    return mycursor.fetchall()

@app.route('/')
def index():
    return render_template('index.html')


# Load your trained YOLOv10 model
model = YOLO('best.pt')  # Make sure best.pt is in the same folder



# Global variable to store logged-in user's email
user_email = None

# Email Alert System (Simple & Safe)
last_alert_time = 0
ALERT_COOLDOWN = 60  # Send alert only once every 60 seconds

# Class names from your model
class_names = ['Distracted', 'Drinking', 'Drowsy', 'Eating', 'PhoneUse', 'SafeDriving', 'Seatbelt', 'Smoking']

# ================ EMAIL FUNCTION ================

def send_alert_email(to_email, behavior):
    global last_alert_time
    if time.time() - last_alert_time < 60:
        return
    last_alert_time = time.time()

    # ←←← CHANGE THESE TWO LINES ONLY ←←←
    sender_email = os.getenv("SMARTDRIVE_EMAIL")
    sender_password = os.getenv("SMARTDRIVE_EMAIL_PASSWORD")
    if not sender_email or not sender_password:
        print("Email credentials are not configured.")
        return
    # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = f"ALERT: {behavior} Detected!"

        body = f"""
        DRIVER SAFETY ALERT

        Detected: {behavior}
        Time: {time.strftime('%d-%m-%Y %H:%M:%S')}
        Driver: {to_email}

        Stay Alert & Drive Safely!

        — Smart Driver Monitoring System
          cse.takeoffprojects.com
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()

        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Email failed: {e}")

# ================ VIDEO STREAM WITH DETECTION ================
# REMOVE this global line:
# camera = cv2.VideoCapture(0)   ← DELETE THIS

# ADD this function instead:
def get_camera():
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("ERROR: Cannot open camera!")
        return None
    # Optional: Set resolution for better performance
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cam.set(cv2.CAP_PROP_FPS, 30)
    return cam

# ─────── FINAL WORKING generate_frames() ───────
def generate_frames():
    while True:
        # Open camera fresh EVERY FRAME (this fixes everything)
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            cap.release()
            time.sleep(0.5)
            # Show error frame instead of dying
            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_frame, "Camera Not Available", (50, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            ret, buffer = cv2.imencode('.jpg', error_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            continue

        success, frame = cap.read()
        cap.release()  # Release immediately

        if not success:
            continue

        # Resize for speed
        frame = cv2.resize(frame, (640, 480))

        # YOLO Detection
        try:
            results = model(frame, conf=0.5, verbose=False)[0]
        except:
            results = None

        annotated_frame = frame.copy()

        if results and results.boxes is not None:
            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                conf = box.conf[0]
                label = class_names[cls]

                color = (0, 0, 255) if label in ['Drowsy', 'Distracted'] else (0, 255, 0)
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 3)
                cv2.putText(annotated_frame, f"{label} {conf:.2f}", (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                # Send alert
                if label in ['Drowsy', 'Distracted'] and user_email:
                    send_alert_email(user_email, label)

        # Add status text
        cv2.putText(annotated_frame, "LIVE - YOLOv10 Detection Active", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Encode and yield
        ret, buffer = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/register', methods=["GET", "POST"])
def register():
        if request.method == "POST":
            name = request.form.get('name')
            email = request.form['email']
            password = request.form['password']
            confirmpassword = request.form['confirmpassword']
            if password == confirmpassword:
                query = "SELECT UPPER(email) FROM users"
                email_data = retrivequery2(query)
                email_data_list = []
                for i in email_data:
                    email_data_list.append(i[0])
                if email.upper() not in email_data_list:
                    query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                    values = (name, email, password)
                    executionquery(query, values)

                    return render_template('login.html', message="Successfully Registered!")
                return render_template('register.html', message="This email ID is already exists!")
            return render_template('register.html', message="Confirm password is not match!")
        return render_template('register.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        query = "SELECT UPPER(email) FROM users"
        email_data = retrivequery2(query)
        email_data_list = []
        for i in email_data:
            email_data_list.append(i[0])

        if email.upper() in email_data_list:
            query = "SELECT UPPER(password) FROM users WHERE email = %s"
            values = (email,)
            password__data = retrivequery1(query, values)
            if password.upper() == password__data[0][0]:
                global user_email
                user_email = email

                return redirect("/home")
            return render_template('login.html', message= "Invalid Password!!")
        return render_template('login.html', message= "This email ID does not exist!")
    return render_template('login.html')


# @app.route('/home', methods=["GET", "POST"])
# def home():

#     return render_template('home.html')


@app.route('/home')
def home():
    if not user_email:
        return redirect('/login')
    return render_template('home.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/test_camera')
def test_camera():
    return """
    <h1>Camera Test</h1>
    <img src="{{ url_for('video_feed') }}" width="800">
    <p>If you see video above → Everything is working!</p>
    """



if __name__ == '__main__':
    app.run(debug = True)
