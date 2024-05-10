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




@app.route("/", methods = ["GET", "POST"])
def index():
    if(fk.request.method == "GET"):
        return(render_template("studentRequest.html")) #defualt to the student sign up page for when a student scans qr code
    if request.method == "POST":
        name = request.form['name']
        grade = request.form['class']
        math_class = request.form['math_class']
        availability = request.form['availability']
        

        all_tutors = fetchTutors()

        filtered_tutors = filterTutors(all_tutors, grade, math_class, availability)
        

        if filtered_tutors:
            return render_template("tutorSelectPage.html", tutors=filtered_tutors)
        else:
            return "No tutors available"
        
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
            name = row[0] if len(row) > 0 else ""
            bio = row[1] if len(row) > 1 else ""
            image = row[2] if len(row) > 2 else ""
            availability = row[3] if len(row) > 3 else ""
            math_classes = row[4] if len(row) > 4 else ""
            grade = row[5] if len(row) > 5 else ""
            contact = row[6] if len(row) > 6 else ""
            tutor = {'name': name, 'bio': bio, 'image': image, 'availability': availability, 'math_classes': math_classes, 'grade': grade}
            tutors_data.append(tutor)
        
        return tutors_data
    except Exception as e:
        print(f"Error fetching tutors from Google Sheet: {e}")
        return None


def filterTutors(tutors, grade, math_class, availability):
    filtered_tutors = []

    for tutor in tutors:
        if tutor['availability'] == availability or math_class in tutor['math_classes']:
            filtered_tutors.append(tutor)

    return filtered_tutors

    


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

    