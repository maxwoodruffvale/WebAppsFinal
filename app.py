import flask as fk

from flask import render_template, redirect, url_for
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from flask import request 
import sqlite3
import gspread
from oauth2client.service_account import ServiceAccountCredentials

logging.basicConfig(level=logging.DEBUG)
app = fk.Flask(__name__)

credentials_path = 'spreadsheet-data-422018-cceb62cdb5ee.json'
credentials = service_account.Credentials.from_service_account_file(
    credentials_path,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)


users = {
    'admin': '@',
}


service = build('sheets', 'v4', credentials=credentials)
sheet_id = '1LFsGU5VC63-V084TI-kFo-nfRoMjBjSi2fyPZtcHr7A'
range_name = 'Sheet1!A1:D100'
range_name2 = 'Sheet1!A1:F100'


def initializeDatabase():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            grade TEXT NOT NULL,
            math_class TEXT NOT NULL,
            availability TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

initializeDatabase()


@app.route("/", methods = ["GET", "POST"])
def index():
    if(fk.request.method == "GET"):
        return(render_template("studentRequest.html")) #defualt to the student sign up page for when a student scans qr code
    if request.method == "POST":
        name = request.form['name']
        grade = request.form['class']
        math_class = request.form['math_class']
        availability = request.form['availability']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (name, grade, math_class, availability)
            VALUES (?, ?, ?, ?)
        ''', (name, grade, math_class, availability))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template("studentRequest.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            return redirect(url_for('embedSpreadsheet'))
        else: 
            error = "Invalid username or password. Please try again."
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route("/embedSpreadsheet", methods=["GET", "POST"])
def embedSpreadsheet():
    return render_template("spreadSheetPage.html")

def fetchTutors():
    try:
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range=range_name2).execute()
        values = result.get('values', [])
        
        if not values:
            return None

        tutors_data = []
        for row in values[1:]: 
            name, bio, image, availability, math_classes, grade = row
            tutor = {'name': name, 'bio': bio, 'image': image, 'availability': availability, 'math_classes': math_classes, 'grade': grade}
            tutors_data.append(tutor)
        
        return tutors_data
    except Exception as e:
        print(f"Error fetching tutors from Google Sheet: {e}")
        return None

    


@app.route("/tutorSelect", methods=["GET", "POST"])
def tutors():
    if fk.request.method == "GET":
        tutors_data = fetchTutors()
        if tutors_data:
            return fk.render_template("tutorSelectPage.html", tutors=tutors_data)
        else:
            return "No tutors available"

if __name__ == "__main__":
    app.run(debug=True)  

    