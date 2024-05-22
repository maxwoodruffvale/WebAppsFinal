import flask as fk

from flask import render_template, redirect, url_for, session
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
import sqlite3
import hmac
from passlib.hash import sha256_crypt

global msg

def send_email(subject, message, to_email):
    print("gyat ballsamongus")
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

        server.sendmail(smtp_username, to_email, msg.as_string())

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

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

credentials_path = 'spreadsheet-data-422018-cceb62cdb5ee.json'
credentials = service_account.Credentials.from_service_account_file(
    credentials_path,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)


users = {
    'admin': {
        'password_hash': '$5$rounds=535000$oQnmhzF/IL71CDHt$98asW.DxEC4DF2dVeCKuWLORKDfhKcZghPc.fe3S2P1'  
    }
}



service = build('sheets', 'v4', credentials=credentials)
sheet_id = '1LFsGU5VC63-V084TI-kFo-nfRoMjBjSi2fyPZtcHr7A'
range_name = 'Sheet1!A1:D100'
range_name2 = 'Sheet1!A1:I100'
#password123

hashed_password = sha256_crypt.hash("password123")
print("bruh: " + hashed_password)

student_email=""

@app.route("/", methods = ["GET", "POST"])
def index():
    if(fk.request.method == "GET"):
        return(render_template("studentRequest.html")) #defualt to the student sign up page for when a student scans qr code
    else:
        name = request.form['name']
        grade = request.form['class']
        math_class = request.form['math_class']
        availability = request.form['availability']
        day_availability = request.form['day_availability']
        student_email = request.form['email']

        student = [name, grade, math_class, availability, day_availability, student_email]

        all_tutors = fetchTutors()
        
        filtered_tutors = filterTutors(all_tutors, grade, math_class, availability, day_availability)
        

        if filtered_tutors:
            return render_template("tutorSelectPage.html", tutors=filtered_tutors[:3] if len(filtered_tutors) >= 3 else filtered_tutors[:], Student=student)
        else:
            return "No tutors available"

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            stored_password_hash = users[username]['password_hash']
            if sha256_crypt.verify(password, stored_password_hash):
                session['logged_in'] = True
                return redirect(url_for('embedSpreadsheet'))
        error = "Invalid username or password. Please try again."
        return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/embedSpreadsheet', methods=["GET", "POST"])
def embedSpreadsheet():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
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
            day_availability = row[8] if len(row) > 8 else ""
            tutor = {'name': name, 'bio': bio, 'image': image, 'availability': availability, 'math_classes': math_classes, 'grade': grade, 'contact': contact, 'phone':phone, 'day_availability': day_availability}
            tutors_data.append(tutor)
        
        return tutors_data
    except Exception as e:
        print(f"Error fetching tutors from Google Sheet: {e}")
        return None

def filterTutors(tutors, grade, math_class, availability, day_availability):
    filtered_tutors = []

    for tutor in tutors:
        if availability in tutor['availability'] and math_class in tutor['math_classes'] and day_availability in tutor['day_availability']:
            filtered_tutors.append(tutor)

    return filtered_tutors

saved_tutor_info = ''  


from flask import g

DATABASE = 'tutor_info.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/tutorSelectPage", methods=["GET", "POST"])
def test_jawn():
    if fk.request.method == "GET":
        return "this was the get oh brother<br>Yeah my bad we're lowkey throwing at coding and my computer screen broke since my girlfriend dropped it. Try again I suppose?"
    else:
        info = request.form["tutor-data"]
        info = info[1:-1].split(", ")
        print(info)
        name = info[0][1:-1]
        contact=info[1][1:-1]

        student = request.form["student"]
        print(student)
        chars = "[]'\""
        for c in chars:
            student = student.replace(c, "")
        student=student.split(", ")
        print(student)

        student_msg = f'LASA Math Tutoring Service: Your tutor is {name}. You can contact them at {contact}. They also recieved an email and may reach out soon.'

        tutor_msg = f'LASA Math Tutoring Service: your new student is {student[0]} in {student[2]}. They are in {student[1]}th grade. They want to meet on {student[4]} in the {student[3]}. You can contact them at {student[5]}'
        
        harrelson_msg = f'LASA Math Tutoring Service: {student[0]} has been matched up with {name} to learn {student[2]} on {student[4]} in the {student[3]}. Tutor email: {contact}, student email: {student[5]}'
        
        print(student_msg)
        print(tutor_msg)
        print(harrelson_msg)
        
        send_email('Your Tutor for LASA Math Tutoring', student_msg, student[5])
        send_email("LASA Math Tutoring new student for you", tutor_msg, contact)
        #send_email("LASA Math Tutoring form matvch", harrelson_msg, "sarah.harrelson2@austinisd.org")
        #add jawn for the thingy
        return render_template("contacted.html", msg=student_msg)


@app.route('/save_tutor_info', methods=['POST'])
def save_tutor_info():
    tutor_info = request.json
    name = tutor_info['name']
    contact = tutor_info['contact']

    db = get_db()

    db.execute("INSERT INTO tutor_info (name, contact) VALUES (?, ?)", (name, contact))
    db.commit()

    msg = 'skibidi'

    contact = contact.replace("Contact:", "").strip()

    msg = f'LASA Math Tutoring Service: Your tutor is {name}. You can contact them at {contact}'
    #send_email('LASA Math Tutoring lets go', msg, student_email)
    return redirect(url_for('contacted'))

@app.route('/contacted', methods=["GET", "POST"])
def contacted():
    #db = get_db()

    #cur = db.execute("SELECT name, phone, contact FROM tutor_info ORDER BY ROWID ASC LIMIT 1")
    #row = cur.fetchone()
    #if row:
    #    name, phone, contact = row
    #    contact = contact.replace("Contact:", "").strip()
    #    msg = f'LASA Math Tutoring Service: Your tutor is {name}. You can contact them at {contact}'
    #else:
    #    msg = None

    return render_template("contacted.html", msg="")

@app.route('/support', methods=["GET"])
def support():
    return render_template("support.html")


if __name__ == "__main__":
    app.run(debug=True)

    