from flask import Flask, render_template, redirect, url_for, request
from app import app
from pymongo import MongoClient

def connect_users():
    client = MongoClient("mongodb+srv://test-user:1234@cluster0-zffwk.mongodb.net/test?retryWrites=true&w=majority")
    db = client.recruit
    userdata = db.users
    return userdata.find()

current_user=list()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route("/_signin", methods = ["POST"])
def _signin():
    if request.method == 'POST':
        userlist = connect_users()
        uid = request.form["userid"]
        upw = request.form["userpw"]
        stu = request.form["role"]
        match = False
        for user in userlist:
            if uid == user['username'] and upw == user['password'] and stu==user['student']:
                print("Match")
                match=True
                if stu=="student":
                    global current_user
                    current_user = user
                    return redirect(url_for('studentmypage', sid=user['sid'], Fname=user['fname']))
        if not match:
            print("No Match Found")

@app.route("/studentmypage/<sid>/<Fname>/")
def studentmypage(sid, Fname):
    # userlist = connect_users()
    # print(userlist)
    # print(sid)
    global current_user
    return render_template("studentmypage.html", sid = sid, Fname = Fname, courses=current_user['courses'])
    for user in userlist:
        if int(sid) == int(user['sid']):
            courses = user['courses']
            return render_template("studentmypage.html", sid = sid, Fname = Fname, courses=courses)
    return redirect(url_for('index'))
    