import flask as fk

from flask import render_template, redirect, url_for
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from flask import request 
import sqlite3
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject, message, to_email):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'lasamathtutoringsite@gmail.com'
    smtp_password = 'wdoe ocaa dxuh pfyu'

    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        server.login(smtp_username, smtp_password)

        server.send_message(msg)

        print('Email sent successfully.')
    except Exception as e:
        print('Error occurred while sending email:', str(e))
    finally:
        server.quit()






def send_sms(to_phone, message):
    account_sid = 'ACafffbe5893fc5c4dc679f3985ea11ff8'
    auth_token = '41b1a7e63bcf856c87c0488d046527c8'

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message,
        from_='+18333662406',
        to=to_phone
    )

    print('Message sent. SID:', message.sid)

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
range_name2 = 'Sheet1!A1:G100'


student_number="5128770023"
student_email="maxv8978@gmail.com"

@app.route("/", methods = ["GET", "POST"])
def index():
    if(fk.request.method == "GET"):
        return(render_template("studentRequest.html")) #defualt to the student sign up page for when a student scans qr code
    else:
        name = request.form['name']
        grade = request.form['class']
        math_class = request.form['math_class']
        availability = request.form['availability']
        student_number = request.form['phone_number']
        student_email = request.form['email']
        print(student_number)
        all_tutors = fetchTutors()

        filtered_tutors = filterTutors(all_tutors, grade, math_class, availability)
        

        if filtered_tutors:
            return render_template("tutorSelectPage.html", tutors=filtered_tutors)
        else:
            return "No tutors available"

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
            phone = row[7] if len(row) > 7 else ""
            tutor = {'name': name, 'bio': bio, 'image': image, 'availability': availability, 'math_classes': math_classes, 'grade': grade, 'contact':contact, 'phone':phone}
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

saved_tutor_info = ''  

@app.route('/save_tutor_info', methods=['POST'])
def save_tutor_info():
    tutor_info = request.json
    saved_tutor_info = tutor_info
    print(tutor_info)
    print(student_number)
    msg = 'LASA Math Tutoring Service: Your tutor is ' + tutor_info['name'] + ". You can contact them at " + tutor_info['phone'] + " or " + tutor_info['contact']
    #send_sms("5128770023", 'LASA Math Tutoring Service: Your tutor is ' + tutor_info['name'] + ". You can contact them at " + tutor_info['phone'] + " or " + tutor_info['contact'])
    print(student_email)
    send_email('LASA MAth tutoring lets go', msg, student_email)
    return "something"


@app.route('/contacted', methods=["GET", "POST"])
def contacted():
    if(fk.request.method=="GET"):
        return render_template("contacted.html", tutor=saved_tutor_info)

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

    