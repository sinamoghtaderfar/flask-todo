# Flask-TODO App

This is a simple web application for keeping track of your daily tasks (a TODO list) using **Flask** and **MySQL**.  
You can easily add new tasks, edit them, delete them, and mark them as done. The interface is simple and clean so you can focus on managing your tasks.

## 1. Features

- Quickly add, edit, and remove tasks
- Keep track of completed and pending tasks
- Simple and user-friendly interface
- Data is stored safely in **MySQL**
- OTP (one-time password) can be sent to email for verification
- System errors are logged and saved in the `logs` folder

Some features might seem extra, but they were included mainly for **learning and experimentation** while exploring different aspects of Flask.

## 2. Stress Testing

Stress tests have been performed, and the results are saved in the `results test` folder.  
You can check them to see how the app behaves under load.  

These tests and extra features are primarily for **learning purposes**, so some parts might feel unnecessary for a basic TODO app. They helped me practice and understand more about web development with Flask.

## 3. Demo Video

You can watch a short demo of the app on YouTube: (https://youtu.be/vJp9Q4pQh08)](https://www.youtube.com/watch?v=vJp9Q4pQh08)

## 4. Requirements
- Python 3.8+  
- MySQL  
- pip  

## 5. Installation & Running
1. git or bash or cmd...
git clone https://github.com/sinamoghtaderfar/flask-todo.git

cd flask-todo

2. Create and activate a virtual environment

- Windows:
python -m venv venv
venv\Scripts\activate

- Linux / macOS:
python3 -m venv venv
source venv/bin/activate

3. Install dependencies

- pip install -r requirements.txt

4. Setup MySQL Database

- Login to MySQL: mysql -u root -p

 5. Create a database: CREATE DATABASE flask_todo;

* Update the database URI in app/__init__: 

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/flask_todo'

6. Create tables

7. Or using Flask CLI:
# Linux / macOS
export FLASK_APP=run.py

export FLASK_ENV=development

flask run

# Windows
set FLASK_APP=run.py

set FLASK_ENV=development

flask run

app should now be running at: http://127.0.0.1:5000
