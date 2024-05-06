import flask as fk
import html
from flask import render_template
import logging
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from flask import request 

logging.basicConfig(level=logging.DEBUG)
app = fk.Flask(__name__)

credentials_path = 'spreadsheet-data-422018-cceb62cdb5ee.json'
credentials = service_account.Credentials.from_service_account_file(
    credentials_path,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

service = build('sheets', 'v4', credentials=credentials)
sheet_id = '1LFsGU5VC63-V084TI-kFo-nfRoMjBjSi2fyPZtcHr7A'
range_name = 'Sheet1!A1:C10'

@app.route("/", methods = ["GET", "POST"])
def index():
    if(fk.request.method == "GET"):
        return(render_template("studentRequest.html")) #defualt to the student sign up page for when a student scans qr code
    else:
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get('values', [])

        re=""

        if not values:
            re = 'No data found.'
        else:
            re += 'Data:'
            for row in values:
                re += str(row)
        return "you did it!\n" + re #post return, should eventually lead to suggested tutors page

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)  

    