import dateparser
import datetime
import dbconfig
from flask import Flask
from flask import render_template
from flask import request
import json
import string

if dbconfig.test:
    from mockdbhelper import MockDBHelper as DBHelper
else:
    from dbhelper import DBHelper



app = Flask(__name__)
DB = DBHelper()
categories = ['mugging', 'break-in']


@app.route("/")
def home(error_message=None):
    try:
        crimes = DB.get_all_crimes()
        print crimes
        crimes = json.dumps(crimes)
    except Exception as e:
        print e
        crimes = []
    return render_template("home.html", crimes=crimes, categories=categories, error_message=error_message)

@app.route("/submitcrime", methods=['POST'])
def submitcrime():
    print 'Submitting crime'
    category = request.form.get("category")
    print category
    if category not in categories:
        return home()
    date = format_date(request.form.get("date"))
    print date
    if not date:
        return home("Invalid date. Please use yyyy-mm-dd format")
    try:
        latitude = float(request.form.get("latitude"))
        longitude = float(request.form.get("longitude"))
    except ValueError():
        return home()
    description = sanitize_string(request.form.get("description"))
    print "inserting query"
    DB.add_crime( category, date,latitude, longitude, description)
    return home()

def format_date(userdate):
    date = dateparser.parse(userdate)
    try:
        return datetime.datetime.strftime(date, "%Y-%m-%d")
    except TypeError: #if dateparser cannot parse, it will return None
        return None

def sanitize_string(userinput):
    whitelist = string.letters + string.digits + " !?$.,;:-'()$"
    return filter(lambda x: x in whitelist, userinput)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
