from flask import Flask, render_template, redirect, url_for, request, flash
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
            user=db['students'].find_one({'username':uid, 'password':upw})
            if user:
                return redirect(url_for('studentmypage', username=user['username'], Fname=user['Fname']))
        if stu=="company":
            user=db['companies'].find_one({'name':uid, 'password':upw})
            if user:
                return redirect(url_for('companymypage', name=uid))
        return redirect(url_for('index'))

@app.route("/studentmypage/<username>/<Fname>/")
def studentmypage(username, Fname):
    # Calling Messages
    global db
    mymsg = db['messages'].find({'studentname':username, 'towhom':'student'})
    mycourse = db['student-course'].find({'username':username})
    mywork = db['student-work'].find({'username':username})
    courses = list()
    works = list()
    for course in mycourse:
        total = dict()
        courseinfo = db['courses'].find_one({'code':course['code'], 'Institution':course['institution']})
        total['code']=course['code']
        total['institution']=course['institution']
        total['grade']=course['grade']
        total['year']=course['year']
        total['semester']=course['semester']
        total['name']=courseinfo['name']
        total['professor']=courseinfo['Professor']
        total['credit']=courseinfo['credit']
        courses.append(total)

    for work in mywork:
        total = dict()
        workinfo = db['works'].find_one({'workname':work['workname']})
        total['workname']=work['workname']
        total['description']=workinfo['description']
        total['duration']=work['duration']
        total['occupation']=work['occupation']
        total['category']=workinfo['category']
        works.append(total)
    return render_template("studentmypage.html", username = username, Fname = Fname, courses=courses, works=works, messages=mymsg)
    # else:
    #     userlist = db['users'].find()
    #     for user in userlist:
    #         if int(sid) == int(user['sid']):
    #             courses = user['courses']
    #             works = user['works']
    #             return render_template("studentmypage.html", sid = sid, Fname = Fname, courses=courses, works=works, messages=mymsg)
    #     return redirect(url_for('index'))

# Page - Add Work
@app.route("/studentmypage/<username>/<Fname>/addwork")
def addwork(username, Fname):
    return render_template("addwork.html", username= username)

# Process - Add Work
@app.route("/studentmypage/<username>/<Fname>/_addwork", methods = ["POST"])
def _addwork(username, Fname):
    global db
    relationcollection= db['student-work']
    workcollection=db['works']
    workinfo = dict()
    relation = dict()
    relation['username']=username
    relation['workname']=request.form['name']
    relation['duration']=request.form['duration']
    relation['occupation']=request.form['occupation']

    workinfo['workname']=request.form['name']
    workinfo['description']=request.form['description']
    workinfo['category']=request.form['category']
    relationcollection.insert_one(relation)
    workcollection.insert_one(workinfo)
    return redirect(url_for('studentmypage', username = username, Fname = Fname))

# Page - Add Course
@app.route("/studentmypage/<username>/<Fname>/addcourse")
def addcourse(username, Fname):
    return render_template("addcourse.html",Fname=Fname)

# Process - Add Course
@app.route("/studentmypage/<username>/<Fname>/_addcourse", methods = ["POST"])
def _addcourse(username, Fname):
    global db
    relationcollection=db['student-course']
    coursecollection=db['courses']
    relation=dict()
    courseinfo=dict()
    relation['code']=request.form['code']
    relation['username']=username
    relation['semester']=request.form['semester']
    relation['year']=request.form['year']
    relation['grade']=request.form['grade']
    relation['institution']=request.form['institution']

    courseinfo['code']=request.form['code']
    courseinfo['name']=request.form['name']
    courseinfo['Professor']=request.form['professor']
    courseinfo['Institution']=request.form['institution']
    courseinfo['credit']=request.form['credit']
    # for field in ["code", "name", "credit", "professor", "grade", "year", "semester"]:
    #     obj.append(request.form[field])
    relationcollection.insert_one(relation)
    coursecollection.insert_one(courseinfo)
    return redirect(url_for('studentmypage', username = username, Fname = Fname)) 

# Process - Send Message to Company
@app.route("/studentmypage/<username>/<Fname>/_sendtocompany", methods = ["POST"])
def _sendtocompany(username, Fname):
    if request.method == "POST":
        global db
        msgcollection = db.messages

        message = request.form['message']
        name = request.form['name']
        msgcollection.insert_one({'username':username, 'cid':name, 'contents':message, 'towhom': 'company'})

        return redirect(url_for("studentmypage", username=username, Fname=Fname))

# Process - Send Message to Company via Direct Reply
@app.route("/studentmypage/<username>/<Fname>/_sendtocompany/<name>", methods = ["POST"])
def _sendtothecompany(username, Fname, name):
    if request.method == "POST":
        global db
        msgcollection = db.messages

        message = request.form['message']
        msgcollection.insert_one({'username':username, 'cid':name, 'contents':message, 'towhom':'company'})

        return redirect(url_for("studentmypage", username = username, Fname = Fname))

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
    positions = db['positions'].find({'company':name})
    # allpositions=list()
    # for position in positions:
    #     thisposition = dict()
    #     thisposition['company']=position['company']


    mymsg = db['messages'].find({'towhom':'company','cid':name})
    return render_template("companymypage.html", name = name, positions = positions, messages = mymsg)

# Page - Add Position
@app.route("/companymypage/<name>/addposition")
def addposition(name):
    return render_template("addposition.html")

# Process - Add Position
@app.route("/companymypage/<name>/_addposition", methods = ["POST"])
def _addposition(name):
    global db
    position = dict()
    position['company'] = name
    position['name']= request.form['name']
    position['description']= request.form['description']
    position['wage']= request.form['wage']
    position['skills']= request.form['skills']
    db['positions'].insert_one(position)
    return redirect(url_for('companymypage', name = name))

# Process - Send Message to Student
@app.route("/companymypage/<name>/_sendtostudent", methods = ["POST"])
def _sendtostudent(name):
    if request.method == "POST":
        global db
        msgcollection = db.messages

        message = request.form['message']
        sid = request.form['sid']
        msgcollection.insert_one({'sid':sid, 'cid':name, 'contents':message, 'towhom': 'student'})

        return redirect(url_for('companymypage', name = name))

# Process - Send Message to Student
@app.route("/companymypage/<name>/_sendtostudent/<sid>", methods = ["POST"])
def _sendtothestudent(name, sid):
    if request.method == "POST":
        global db
        msgcollection = db.messages

        message = request.form['message']
        msgcollection.insert_one({'sid':sid, 'cid':name, 'contents':message, 'towhom':'student'})

        return redirect(url_for('companymypage', name = name))

@app.route("/search")
def search():
    return render_template("search.html", students=[], companies=[], courses=[],positions=[])

# Process - Search
@app.route("/_search", methods=["POST"])
def _search():
    if request.method == "POST":
        query = request.form['query']
        return redirect(url_for('searchquery', query = query))

# Page - Search with query
@app.route("/searchquery/<query>")
def searchquery(query):
    global db
    student=db['students'].find({'$or':[{"Fname":{'$regex':query, '$options':'i'}}, {"Lname":{'$regex':query, '$options':'i'}}, {"Major":{'$regex':query, '$options':'i'}}, {"Institution":{'$regex':query, '$options':'i'}}]})

    company=db['companies'].find({'$or':[{"name":{'$regex':query, '$options':'i'}}, {"address":{'$regex':query, '$options':'i'}}, {"email":{'$regex':query, '$options':'i'}}]})

    position=db['positions'].find({'$or':[{"name":{'$regex':query, '$options':'i'}}, {"company":{'$regex':query, '$options':'i'}}, {"description":{'$regex':query, '$options':'i'}}]})

    course=db['courses'].find({'$or':[{"name":{'$regex':query, '$options':'i'}}, {"Professor":{'$regex':query, '$options':'i'}}, {"Institution":{'$regex':query, '$options':'i'}}, {"credit":{'$regex':query, '$options':'i'}}]})

    # for item in db['users'].find():
    #     for value in item.items():
    #         if value==query:s
    #             switch()
    return render_template("search.html", students = student, companies = company, positions = position, courses = course)


# Page - Student Enroll
@app.route("/student")
def student():
    return render_template("student.html")

# Process - Student Enroll
@app.route("/_studentenroll", methods=["POST"])
def _studentenroll():
    global db
    student = dict()
    if db['students'].find_one({'username':request.form['username']}):
        flash("Username already exists. Choose another name")

    if request.method == "POST":
        student['Fname']=request.form['fname']
        student['Lname']=request.form['lname']
        student['password']=request.form['password']
        student['Major']=request.form['major']
        student['Institution']=request.form['school']
        student['username']=request.form['username']
        db['students'].insert_one(student)
        return redirect(url_for('studentmypage', username = request.form["username"], Fname = request.form["fname"]))