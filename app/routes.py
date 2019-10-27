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
    global current_user
    if current_user and current_user["sid"]==sid:
        return render_template("studentmypage.html", sid = sid, Fname = Fname, courses=current_user['courses'], works=current_user['works'])
    else:
        userlist = connect_users()
        for user in userlist:
            if int(sid) == int(user['sid']):
                courses = user['courses']
                works = user['works']
                return render_template("studentmypage.html", sid = sid, Fname = Fname, courses=courses, works=works)
        return redirect(url_for('index'))

# Page - Add Work
@app.route("/studentmypage/<sid>/<Fname>/addwork")
def addwork(sid, Fname):
    return render_template("addwork.html")

# Process - Add Work
@app.route("/studentmypage/<sid>/<Fname>/_addwork", methods = ["POST"])
def _addwork(sid, Fname):
    client = MongoClient("mongodb+srv://test-user:1234@cluster0-zffwk.mongodb.net/test?retryWrites=true&w=majority")
    db = client.recruit
    userdata = db.users
    if request.method == "POST":
        obj = list()
        obj.append(request.form["name"])
        obj.append(request.form["description"])
        obj.append(request.form["category"])
        userdata.update({'sid':sid},{'$push': {'works':obj}})
        return redirect(url_for('studentmypage', sid = sid, Fname = Fname))

# Page - Add Course
@app.route("/studentmypage/<sid>/<Fname>/addcourse")
def addcourse(sid, Fname):
    return render_template("addcourse.html")

# Process - Add Course
@app.route("/studentmypage/<sid>/<Fname>/_addcourse", methods = ["POST"])
def _addcourse(sid, Fname):
    client = MongoClient("mongodb+srv://test-user:1234@cluster0-zffwk.mongodb.net/test?retryWrites=true&w=majority")
    db = client.recruit
    userdata = db.users
    obj=list()
    for field in ["code", "name", "credit", "professor", "grade", "year", "semester"]:
        obj.append(request.form[field])
    userdata.update({'sid':sid},{'$push': {'courses':obj}})
    return redirect(url_for('studentmypage', sid = sid, Fname = Fname))