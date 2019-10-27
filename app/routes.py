from flask import Flask, render_template, redirect, url_for, request
from app import app
from pymongo import MongoClient


client = MongoClient("mongodb+srv://test-user:1234@cluster0-zffwk.mongodb.net/test?retryWrites=true&w=majority")
db = client['recruit']
current_user=list()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route("/_signin", methods = ["POST"])
def _signin():
    if request.method == 'POST':
        global db
        uid = request.form["userid"]
        upw = request.form["userpw"]
        stu = request.form["role"]

        if stu == 'student':
            user=db['users'].find({'username':uid, 'password':upw, 'student':stu})
            if user:
                return redirect(url_for('studentmypage', sid=user['sid'], Fname=user['fname']))
        if stu=="company":
            user=db['users'].find({'username':uid, 'password':upw, 'student':stu})
            if user:
                return redirect(url_for('companymypage', name=uid))

@app.route("/studentmypage/<sid>/<Fname>/")
def studentmypage(sid, Fname):
    # Calling Messages
    global db
    mymsg = db['messages'].find({'sid':sid, 'towhom':'student'})
    user=db['users'].find_one({'sid':sid})
    courses = user['courses']
    works = user['works']
    return render_template("studentmypage.html", sid = sid, Fname = Fname, courses=courses, works=works, messages=mymsg)
    # else:
    #     userlist = db['users'].find()
    #     for user in userlist:
    #         if int(sid) == int(user['sid']):
    #             courses = user['courses']
    #             works = user['works']
    #             return render_template("studentmypage.html", sid = sid, Fname = Fname, courses=courses, works=works, messages=mymsg)
    #     return redirect(url_for('index'))

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
    global db
    userdata = db.users
    obj=list()
    for field in ["code", "name", "credit", "professor", "grade", "year", "semester"]:
        obj.append(request.form[field])
    userdata.update({'sid':sid},{'$push': {'courses':obj}})
    return redirect(url_for('studentmypage', sid = sid, Fname = Fname)) 

# Process - Send Message to Company
@app.route("/studentmypage/<sid>/<Fname>/_sendtocompany", methods = ["POST"])
def _sendtocompany(sid, Fname):
    if request.method == "POST":
        global db
        msgcollection = db.messages

        message = request.form['message']
        name = request.form['name']
        msgcollection.insert_one({'sid':sid, 'cid':name, 'contents':message, 'towhom': 'company'})

        return redirect(url_for("studentmypage", sid = sid, Fname = Fname))

# Process - Send Message to Company via Direct Reply
@app.route("/studentmypage/<sid>/<Fname>/_sendtocompany/<name>", methods = ["POST"])
def _sendtothecompany(sid, Fname, name):
    if request.method == "POST":
        global db
        msgcollection = db.messages

        message = request.form['message']
        msgcollection.insert_one({'sid':sid, 'cid':name, 'contents':message, 'towhom':'company'})

        return redirect(url_for("studentmypage", sid = sid, Fname = Fname))

#--------------------------------------------------------------------------------
# Company
#

# Page - Company Enroll
@app.route("/company")
def company():
    return render_template("company.html")

# Process - Company Enroll
@app.route("/_companyenroll", methods=["POST"])
def _companyenroll():
    if request.method == "POST":
        db.add(request.form, "company")

        return redirect(url_for('companymypage', name = request.form["name"]))

# Page - Company MyPage
@app.route("/companymypage/<name>/")
def companymypage(name):
    global db
    user = db['users'].find_one({'student':'company','username':name})
    position = user['position']

    mymsg = db['messages'].find({'towhom':'company','cid':name})
    return render_template("companymypage.html", name = name, positions = position, messages = mymsg)