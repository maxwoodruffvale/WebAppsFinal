import flask as fk

from flask import render_template, redirect, url_for
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from flask import request 
import sqlite3

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
            return redirect(url_for('index'))
        else: 
            error = "Invalid username or password. Please try again."
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route("/tutorSelect", methods=["GET", "POST"])
def tutors():
    tutors_data = [{'name': 'Duke Dennis', 
         'bio': "Hey there! I'm Duke Dennis, your favorite content creator and gaming enthusiast! I'm all about bringing the hype and excitement to the gaming world through my epic gameplay videos and hilarious commentary. From dominating the virtual courts in NBA 2K to conquering the streets in GTA, I'm here to entertain and inspire with my passion for gaming. Join me on this wild ride as we embark on epic adventures together and create unforgettable memories. Stay tuned for more epic content, because with Duke Dennis, the fun never stops!",
         'image': "https://netstorage-legit.akamaized.net/images/135d63472efd5e68.jpg?imwidth=900"},

        {'name': "Sebastian Hill",
         'bio': "Hey, Im Sebastian Hill, a high school student on a mission to explore every corner of the world and beyond. From the classroom to the stage, Im always seeking new adventures and challenges to conquer. Youll often find me buried in books, diving into the mysteries of science and technology, or leading my peers in spirited debates about the issues that matter most. But dont let my academic pursuits fool you—Ive got a creative side too. Whether Im painting a masterpiece or performing in the school play, I thrive on the thrill of expression and connection.",
         'image': "https://media.licdn.com/dms/image/D5603AQGG2S7UCPstkg/profile-displayphoto-shrink_200_200/0/1694816573197?e=2147483647&v=beta&t=yzDYEQ4ue-uOjBa6In-hLXkoikm1AJ_T47lP040-GtY"},

        {'name': "Ahantya Sharma",
         "bio": "Best Shawarma in the world no doubt",
         'image': "https://antalyashawarma.com/Content/Images/photos/home_antalya_shawarma_restaurant_photo_01.png"}]
    
    if(fk.request.method=="GET"):
        return "Tutors ig"
    else:
        return "Yeah idk how you posted bruh theres no form even"

if __name__ == "__main__":
    app.run(debug=True)  

    