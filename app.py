import flask as fk
import html
from flask import render_template
import logging
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

logging.basicConfig(level=logging.DEBUG)
app = fk.Flask(__name__)

credentials_path = 'spreadsheet-data-422018-cceb62cdb5ee.json'
credentials = service_account.Credentials.from_service_account_file(
    credentials_path,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

service = build('sheets', 'v4', credentials=credentials)
sheet_id = '1LFsGU5VC63-V084TI-kFo-nfRoMjBjSi2fyPZtcHr7A'
range_name = 'Sheet1!A1:D100'

@app.route("/", methods = ["GET", "POST"])
def index():
    if(fk.request.method == "GET"):
        return(render_template("studentRequest.html")) #defualt to the student sign up page for when a student scans qr code
    else:
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get('values', [])

        #values is good
        return (render_template("tutorSelectPage.html", tutors = values[1:]))


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