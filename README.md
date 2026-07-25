# Smart Driver Monitoring System

Smart Driver Monitoring System is a Flask-based web application that uses a trained YOLO model to monitor driver behavior from a live camera feed and send alerts when unsafe driving behavior is detected.

## Description

This project detects driver activity such as drowsiness, distraction, phone usage, drinking, eating, smoking, seatbelt status, and safe driving. The frontend is built with Flask templates, the backend includes YOLO training notebooks and model outputs, and the application stores user login data in a MySQL database.

## Features

- Live webcam monitoring through a Flask video stream
- YOLO-based driver behavior detection
- Detection classes: Distracted, Drinking, Drowsy, Eating, PhoneUse, SafeDriving, Seatbelt, Smoking
- Email alerts for high-risk behavior
- User registration and login with MySQL
- Included training notebooks, trained weights, project report, presentations, and demo videos

## Project Structure

```text
Abstract/      Project abstract in PDF and Word formats
Code/
  Backend/     YOLO training notebooks, predictions, and training outputs
  Frontend/    Flask application, templates, static assets, database SQL, and model file
Document/      Final project document
PPT/           Project presentation files
Video/         Demo and execution videos
```

## Requirements

- Python 3.11.13
- MySQL
- Webcam
- Git LFS, for model weights, videos, and zip archives

Install the Python dependencies from:

```bash
Code/Frontend/requirements.txt
```

## Setup

1. Clone the repository.

```bash
git clone https://github.com/haritha74/smartdrive.git
cd smartdrive/Code/Frontend
```

2. Create and activate a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Import the MySQL database.

```bash
mysql -u root -p < db.sql
```

5. Configure email alert credentials.

Create environment variables using the names shown in `.env.example`:

```text
SMARTDRIVE_EMAIL=your-email@example.com
SMARTDRIVE_EMAIL_PASSWORD=your-app-password
```

6. Run the Flask app.

```bash
python app.py
```

Open the local Flask URL shown in the terminal, usually:

```text
http://127.0.0.1:5000
```

## Notes

- The trained model file `best.pt` must be available in `Code/Frontend`.
- Large files are tracked using Git LFS.
- Do not commit real email passwords or application secrets. Use environment variables instead.
