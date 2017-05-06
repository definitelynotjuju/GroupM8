from flask import Flask, render_template, request, session, flash, redirect, url_for
#import db_functions2
import MySQLdb
import sys
import json
import re

import CASClient
#from flask_cas import CAS
#from flask_cas import login_required
app = Flask(__name__)
#conn = MySQLdb.connect(
#        db='groupm8',
#        user='root',
#        passwd='333groupm8',
#        host='localhost')
#c = conn.cursor()
#cas = CAS(app, '/cas')
#app.config['CAS_SERVER'] = 'https://fed.princeton.edu/cas'
#app.config['CAS_AFTER_LOGIN'] = 'index'
#userid="js45"
#groupid = "12"
#dept = "COS"
#courseN = "333"
firstVisit = True

@app.before_request
def session_management():
    session.permanent = True

@app.route("/")
#@login_required
def index():
    global firstVisit
    #C = CASClient.CASClient()
    #netid = C.Authenticate()
<<<<<<< HEAD
    if firstVisit:
        firstVisit = False
        session["logged_in"] = False

=======
    
>>>>>>> a3027355de4011a664657e7960bed829c77eac78
    if 'logged_in' in session and session["logged_in"]:
        return redirect(url_for('home'))
    return render_template("login.html")
    #return flask.render_template(
    #    'layout.html',
    #    username = cas.username,
    #    display_name = cas.attributes['cas:displayName']
    #    )
    #return render_template("login.html")
@app.route("/home")
def home():
    global firstVisit
    if 'logged_in' in session and session["logged_in"]:
        return render_template("home.html")
    return index()
@app.route("/group")
def group():
    global firstVisit
    if 'logged_in' in session and session["logged_in"]:
        return render_template("group.html")
    return index()
@app.route("/group/<gid>")
def group2(gid):
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()
<<<<<<< HEAD

    cmd = "SELECT Dept, CourseN FROM Groups WHERE ID = '" + gid + "'"
    c.execute(cmd)
=======
    
    cmd = "SELECT Dept, CourseN FROM Groups WHERE ID = %s"
    c.execute(cmd, (gid,))
>>>>>>> a3027355de4011a664657e7960bed829c77eac78
    result = c.fetchone()
    session["groupid"] = gid
    session["dept"] = result[0]
    session["courseN"] = result[1]
    return redirect(url_for('group'))
@app.route("/search")
def search():
    if 'logged_in' in session and session["logged_in"]:
        return render_template("search.html")
    return redirect(url_for('index'))
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/Authenticate", methods=['GET','POST'])
def Authenticate():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    netid = request.form['netid']
    pwd = request.form['pwd']
    cmd = "SELECT * FROM Users WHERE UserID = %s AND Password = %s"
    if c.execute(cmd, (netid, pwd,)) == 0:
        conn.commit()
        return "Invalid Login Info"
        flash ('Invalid Login Info')
        return index()
    else:
        conn.commit()
        #return "Successful Login"
        flash ('Successful Login')
        session["logged_in"] = True
        session["userid"] = netid
        return home()

@app.route("/logout")
def logout():
    session["logged_in"] = False
    return index()

@app.route("/current_gid")
def groupid():
    return session["groupid"] + session["dept"] + session["courseN"]
#@app.route("/process_query", methods=['GET','POST'])
#def process_query():
#    return request.form['query']

@app.route("/create_user", methods=['GET','POST'])
def create_user():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    netid = request.form['netid']
    first = request.form['first']
    last = request.form['last']
    pwd = request.form['pwd']
    #db_functions2.create_user(netid,first,last,pwd)
    cmd = "INSERT IGNORE INTO Users (UserID, FirstName, LastName, Password) Values (%s, %s, %s, %s)"
    c.execute(cmd, (netid, first, last, pwd,))
    conn.commit()
    return "New user " + netid + " has been successfully created."

@app.route("/search_user/")
def search_user():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

<<<<<<< HEAD
    cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Courses WHERE Courses.Dept = '" + session["dept"] + "' AND Courses.CourseN = '" + session["courseN"] + "' AND Users.UserID = Courses.UserID AND Courses.Availability = 'T'"
    if c.execute(cmd) == 0:
=======
    dept = session["dept"]
    courseN = session["courseN"]
    
    cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Courses WHERE Courses.Dept = %s AND Courses.CourseN = %s AND Users.UserID = Courses.UserID AND Courses.Availability = 'T'"
    if c.execute(cmd, (dept, courseN,)) == 0:
>>>>>>> a3027355de4011a664657e7960bed829c77eac78
        return "[]"
    else:
        result_set = c.fetchall()
        result = []
        for row in result_set:
            gid = session["groupid"]
            cmd = "SELECT * FROM Members WHERE GroupID = %s AND UserID = %s"
            if c.execute(cmd, (gid, row[0],)) == 0:
                cmd = "SELECT * FROM Requests WHERE GroupID = %s AND UserID = %s"
                if c.execute(cmd, (gid, row[0],)) == 0:
                    result.append(row)
       # conn.rollback()
       # conn.close()
       #f = open("/var/www/GroupM8/GroupM8/templates/file.txt", "w")
       #f.write(result_set)
        return json.dumps(result)

@app.route("/search_user/<query>")
def search_user2(query):
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    queryA = query.split()

    dept = session["dept"]
    courseN = session["courseN"]
    cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Courses WHERE Courses.Dept = %s AND Courses.CourseN = %s AND Users.UserID = Courses.UserID AND Courses.Availability = 'T'"
    if c.execute(cmd, (dept, courseN,)) == 0:
        return "[]"
    else:
        result_set = c.fetchall()
        result = []
        for row in result_set:
            gid = session["groupid"]
            cmd = "SELECT * FROM Members WHERE GroupID = %s AND UserID = %s"
            add = True
            if c.execute(cmd, (gid, row[0],)) == 0:
                for i in queryA:
                    if row[0].startswith(i):
                        continue
                    elif row[1].startswith(i):
                        continue
                    elif row[2].startswith(i):
                        continue
                    else:
                        add = False
                        break
                if add:
                    cmd = "SELECT * FROM Requests WHERE GroupID = %s AND UserID = %s"
                    if c.execute(cmd, (gid, row[0],)) == 0:
                        result.append(row)
        return json.dumps(result)

@app.route("/search_group", methods=['GET','POST'])
def search_group():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    result = "["
    uid = session["userid"]
    dept = request.form['dept']
    courseN = request.form['courseN']
    if dept and courseN:
        cmd = "SELECT ID, Name, Description FROM Groups WHERE Dept = %s AND CourseN = %s AND Availability = 'T'"
        if c.execute(cmd, (dept, courseN,)) == 0:
            return "F"
        else:
            result_set = c.fetchall()
            for row in result_set:
                cmd = "SELECT * FROM Requests WHERE GroupID = %s AND UserID = %s"
                if c.execute(cmd, (row[0],uid,)) == 0:
                                     
                    cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Members WHERE Members.GroupID = '" + str(row[0]) + "' AND Users.UserID = Members.UserID"
                    result += "{\"groupid\": \"" + str(row[0]) + "\", \"name\": \"" + str(row[1]) + "\", \"description\": \"" + str(row[2]) + "\", "
                    if c.execute(cmd) == 0:
                        return json.dumps("[]")
                    else:
                        result += "\"members\": ["
                        members = c.fetchall()
                        for member in members:
                            result += "{\"userid\": \"" + member[0] + "\", \"name\": \"" + member[1] + " " + member[2] + "\"},"
                            result = result[:-1] + "]},"
            result = result[:-1] + "]"
            return result

@app.route("/search_group/<dept>/<courseN>")
def search_group2(dept,courseN):
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    result = "["
    uid = session["userid"]
    #dept = request.form['dept']
    #courseN = request.form['courseN']
    if dept and courseN:
        cmd = "SELECT ID, Name, Description FROM Groups WHERE Dept = %s AND CourseN = %s AND Availability = 'T'"
        if c.execute(cmd, (dept, courseN,)) == 0:
            return "F"
        else:
            result_set = c.fetchall()
            for row in result_set:
                cmd = "SELECT * FROM Requests WHERE GroupID = %s AND UserID = %s"
                if c.execute(cmd, (uid, row[0])) == 0:
                    result += "{\"groupid\": \"" + str(row[0]) + "\", \"name\": \"" + str(row[1]) + "\", \"description\": \"" + str(row[2]) + "\"}, "
            result = result[:-2] + "]"
            return result

@app.route("/create_group", methods=['GET','POST'])
def create_group():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    name = request.form['groupname']
    dept = request.form['groupdept'].upper()
    courseN = request.form['groupnum']
    uid = session["userid"]

    if name and dept and courseN:
        cmd = "INSERT INTO Groups (Name,Dept,CourseN,Availability,Description) VALUES (%s, %s, %s, 'T', 'No description (yet)')"
        c.execute(cmd, (name, dept, courseN,))
        conn.commit()
        cmd = "SELECT MAX(ID) FROM Groups"
        c.execute(cmd)
        ID = str(c.fetchone()[0])
        session["groupid"] = ID
        session["dept"] = dept
        session["courseN"] = courseN
        tempid = ID + uid
        newtempid = uid + dept + courseN
        cmd = "INSERT IGNORE INTO Members (GroupID,UserID,Dept,CourseN,ID) VALUES (%s, %s, %s, %s, %s)"
        c.execute(cmd, (ID, uid, dept, courseN, tempid,))
        conn.commit()
        cmd = "INSERT IGNORE INTO Courses (UserID, Dept, CourseN, Availability,ID) Values (%s, %s, %s, 'T', %s)"
        c.execute(cmd, (uid, dept, courseN, newtempid,))
        conn.commit()
        return render_template("group.html")

@app.route("/add_course", methods=['GET', 'POST'])
def add_course():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    dept = request.form['coursedept'].upper()
    courseN = request.form['coursenum']
    uid = session["userid"]
<<<<<<< HEAD

=======
    tempid = uid + dept + courseN
    
>>>>>>> a3027355de4011a664657e7960bed829c77eac78
    if dept and courseN:
        cmd = "INSERT IGNORE INTO Courses (UserID,Dept,CourseN,Availability,ID) VALUES (%s, %s, %s, 'T', %s)"
        c.execute(cmd, (uid, dept, courseN, tempid,))
        conn.commit()
        return render_template("home.html")

@app.route("/group_info")
def group_info():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

<<<<<<< HEAD
    cmd = "SELECT Name, Description FROM Groups WHERE ID = '" + session["groupid"] + "'"
    if c.execute(cmd) != 0:
=======
    gid = session["groupid"]
    cmd = "SELECT Name, Description FROM Groups WHERE ID = %s"
    if c.execute(cmd, (gid,)) != 0:
>>>>>>> a3027355de4011a664657e7960bed829c77eac78
        result = c.fetchall()
        #return json.dumps(result)
        return "[{\"name\": \"" + result[0][0] + "\", \"description\": \"" + result[0][1] + "\"}]"
    return "not getting the group"

@app.route("/group_members")
def group_members():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

<<<<<<< HEAD
=======
    gid = session["groupid"]
>>>>>>> a3027355de4011a664657e7960bed829c77eac78
    result = "["
    cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Members WHERE Members.GroupID = %s AND Users.UserID = Members.UserID"
    if c.execute(cmd, (gid,)) == 0:
        return "[]"
    else:
        members = c.fetchall()
        for member in members:
            result += "{\"userid\": \"" + member[0] + "\", \"name\": \"" + member[1] + " " + member[2] + "\"},"
        result = result[:-1] + "]"
    return result

@app.route("/group_members/<id>")
def group_members2(id):
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    result = "["
    cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Members WHERE Members.GroupID = %s AND Users.UserID = Members.UserID"
    if c.execute(cmd, (id,)) == 0:
        return "[]"
    else:
        members = c.fetchall()
        for member in members:
            result += "{\"userid\": \"" + member[0] + "\", \"name\": \"" + member[1] + " " + member[2] + "\"},"
        result = result[:-1] + "]"
        return result

@app.route("/user_info")
def user_info():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

<<<<<<< HEAD
    cmd = "SELECT FirstName, LastName FROM Users WHERE UserID = '" + session["userid"] + "'"
    if c.execute(cmd) != 0:
=======
    uid = session["userid"]
    cmd = "SELECT FirstName, LastName FROM Users WHERE UserID = %s"
    if c.execute(cmd, (uid,)) != 0:
>>>>>>> a3027355de4011a664657e7960bed829c77eac78
        user = c.fetchone()
        return "[\"" + user[0] + " " + user[1] + "\"]"
    return "[]"

@app.route("/toggle_course_availability/<dept>/<coursen>")
def toggle_course_availability(dept, coursen):
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    uid = session["userid"]
    cmd = "SELECT Availability FROM Courses WHERE UserId = %s AND Dept = %s AND CourseN = %s"
    if c.execute(cmd, (uid, dept, coursen,)) != 0:
        availability = str(c.fetchone()[0])
        if availability == "T":
            cmd = "UPDATE Courses SET Availability = 'F' WHERE UserID = %s AND Dept = %s AND CourseN = %s"
            c.execute(cmd, (uid, dept, coursen,))
            conn.commit()
            return 'FALSE'
        elif availability == "F":
            cmd = "UPDATE Courses SET Availability = 'T' WHERE UserID = %s AND Dept = %s AND CourseN = %s"
            c.execute(cmd, (uid, dept, coursen,))
            conn.commit()
            return 'TRUE'
    return 'UNABLE TO SET COURSE AVAILABILITY'

@app.route("/toggle_group_availability")
def toggle_group_availability():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

<<<<<<< HEAD
    cmd = "SELECT Availability FROM Groups WHERE ID = '" + session["groupid"] + "'"
    if c.execute(cmd) != 0:
=======
    gid = session["groupid"]
    cmd = "SELECT Availability FROM Groups WHERE ID = %s"
    if c.execute(cmd, (gid,)) != 0:
>>>>>>> a3027355de4011a664657e7960bed829c77eac78
        availability = str(c.fetchone()[0])
        if availability == "T":
            cmd = "UPDATE Groups SET Availability = 'F' WHERE ID = %s"
            c.execute(cmd, (gid,))
            conn.commit()
            return 'FALSE'
        elif availability == "F":
            cmd = "UPDATE Groups SET Availability = 'T' WHERE ID = %s"
            c.execute(cmd, (gid,))
            conn.commit()
            return 'TRUE'
    return 'UNABLE TO SET GROUP AVAILABILITY'

@app.route("/remove_course/<dept>/<coursen>")
def remove_course(dept, coursen):
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    uid = session["userid"]
    cmd = "DELETE FROM Courses WHERE UserID = %s AND Dept = %s AND CourseN = %s"
    if c.execute(cmd, (uid, dept.upper(), coursen,)) != 0:
        conn.commit()
        return "Success!"
    return 'UNABLE TO REMOVE COURSE'

@app.route("/remove_group")
def remove_group():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    uid = session["userid"]
    groupid = session["groupid"]
    cmd = "DELETE FROM Members WHERE GroupID = %s AND UserID = %s"
    if c.execute(cmd, (groupid, uid)) != 0:
        conn.commit()
    else:
        return 'UNABLE TO REMOVE GROUP'
    cmd = "SELECT * FROM Members WHERE GroupID = %s"
    if c.execute(cmd, (groupid,)) == 0:
        cmd = "DELETE FROM Groups WHERE ID = %s"
        if c.execute(cmd, (groupid),) != 0:
            conn.commit()
    return "success!"
    


@app.route("/list_courses")
def list_courses():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    result = "["
    uid = session["userid"]
    cmd = "SELECT Dept, CourseN, Availability FROM Courses WHERE UserID = %s"
    if c.execute(cmd, (uid,)) == 0:
        return "[]"
    else:
        courses = c.fetchall()
        for clas in courses:
            result += "{\"dept\": \"" + clas[0] + "\", \"coursen\": \"" + clas[1] + "\", \"availability\": \"" + clas[2] + "\"},"
        result = result[:-1] + "]"
        return result

@app.route("/check_group_availability")
def check_group_availability():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

<<<<<<< HEAD
=======
    gid = session["groupid"]
>>>>>>> a3027355de4011a664657e7960bed829c77eac78
    result = "["
    cmd = "SELECT Availability FROM Groups WHERE ID = %s"
    if c.execute(cmd, (gid,)) == 0:
        return "ERROR"
    else:
        availability = str(c.fetchone() [0])
        return availability


@app.route("/list_groups")
def list_groups():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    uid = session["userid"]
    result = "["
    cmd = "SELECT GroupID FROM Members WHERE UserID = %s"
    if c.execute(cmd, (uid,)) == 0:
        return "[]"
    else:
        result_set = c.fetchall()
        for row in result_set:
            cmd = "SELECT Name, Dept, CourseN FROM Groups WHERE ID = %s"
            c.execute(cmd, (row[0],))
            groupName = c.fetchone()
            result += "{\"groupid\": \"" + row[0] + "\", \"groupname\": \"" + groupName[0] + "\", \"groupdept\": \"" + groupName[1] + "\", \"groupcoursenum\": \"" + groupName[2] +  "\"}, "
        return result[:-2] + "]"

@app.route("/list_events")
def list_events():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()
    
    uid = session["userid"]
    groupid = session["groupid"]
    result = "["
    cmd = "SELECT Date, Time, Description, Weekday, Name FROM Events WHERE GroupID = %s"
    if c.execute(cmd, (groupid,)) == 0:
        return "[]"
    else:
        events = c.fetchall()
        for event in events:
            result += "{\"date\": \"" + event[0] + "\",  \"time\": \"" + event[1] + "\", \"desc\": \"" + event[2] + "\",  \"day\": \"" + event[3] + "\",  \"name\": \"" + event[4] + "\"},"
        result = result[:-1] + "]"
        return result

@app.route("/add_event", methods=['GET', 'POST'])
def add_event():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    name = request.form['eventname']
    desc = request.form['eventdesc']
    day = request.form['day']
    hour = request.form['hour']
    minutes = request.form['minutes']
    ampm = request.form['ampm']
    repeating = request.form['repeating']
<<<<<<< HEAD

=======
    time = "" + hour + ":" + minutes + ampm
    
>>>>>>> a3027355de4011a664657e7960bed829c77eac78
    uid = session["userid"]
    groupid = session["groupid"]

    cmd = "INSERT INTO Events (GroupID,Date,Time,Description, Weekday, Name) VALUES (%s, %s, %s, %s, %s, %s)"
    c.execute(cmd, (groupid, day, time, desc, day, name))
    conn.commit()
    return render_template("group.html")

@app.route("/list_user_requests")
def list_user_requests():
    conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
    c = conn.cursor()
    result = ""
    uid = session["userid"]
    cmd = "SELECT ID, GroupID FROM Requests WHERE UserID = %s AND Type = 'G'"
    if c.execute(cmd, (uid,)) != 0:
        result = "["
        requests_set = c.fetchall()
        for row in requests_set:
            result += "{\"requestid\": \"" + row[0] + "\", \"groupid\": \"" + row[1] + "\", "
            cmd = "SELECT Name, Description FROM Groups WHERE ID = %s"
            c.execute(cmd, (row[1],))
            group_info = c.fetchone()
            result += "\"groupname\": \"" + group_info[0] + "\", \"groupdesc\": \"" + group_info[1] + "\"}, "
        result = result[:-2] + "]"
        return result
@app.route("/list_group_requests/<t>")
def list_group_requests(t):
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    result = ""
    gid = session["groupid"]
    cmd = "SELECT ID, UserID FROM Requests WHERE GroupID = %s and Type = %s"
    if c.execute(cmd, (gid,t,)) != 0:
        result = "["
        requests_set = c.fetchall()
        for row in requests_set:
            result += "{\"requestid\": \"" + row[0] + "\", \"userid\": \"" + row[1] + "\", "
            cmd = "SELECT FirstName, LastName FROM Users WHERE UserID = %s"
            c.execute(cmd, (row[1],))
            user_info = c.fetchone()
            name = user_info[0] + " " +  user_info[1]
            result += "\"username\": \"" + name  + "\"}, "
        result = result[:-2] + "]"
    return result

@app.route("/process_request/<rid>/<response>")
def process_request(rid, response):
    conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
    c = conn.cursor()

    if response == 'A':
        cmd = "SELECT UserID, GroupID FROM Requests WHERE ID = %s"
        if c.execute(cmd, (rid,)) != 0:
            request_info = c.fetchone()
            uid = request_info[0]
            gid = request_info[1]
            cmd = "SELECT Dept, CourseN FROM Groups WHERE ID = %s"
            if c.execute(cmd, (gid,)) != 0:
                group_info = c.fetchone()
                dept = group_info[0]
                courseN = group_info[1]
                cmd = "INSERT IGNORE INTO Members (GroupID,UserID,Dept,CourseN,ID) VALUES (%s, %s, %s, %s, %s)"
                c.execute(cmd,(gid, uid, dept, courseN, gid + uid,))
                conn.commit()
                cmd = "INSERT IGNORE INTO Courses (UserID, Dept, CourseN, Availability,ID) VALUES (%s, %s, %s, 'T', %s)"
                c.execute(cmd, (uid, dept, courseN, uid+dept+courseN))
                conn.commit()
    cmd = "DELETE FROM Requests WHERE ID = %s"
    c.execute(cmd, (rid,))
    conn.commit()
    return "Success"

@app.route("/send_invitation/<uid>")
def send_invitation(uid):
    conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
    c = conn.cursor()

    gid = session["groupid"]
    cmd = "INSERT IGNORE INTO Requests (UserID, GroupID, Type, ID) VALUES (%s, %s, 'G', %s)"
    c.execute(cmd, (uid, gid, gid + uid,))
    conn.commit()
    return "Success"

@app.route("/send_request/<gid>")
def send_request(gid):
    conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
    c = conn.cursor()
    gid = str(gid)
    uid = session["userid"]
    cmd = "INSERT IGNORE INTO Requests (UserID, GroupID, Type, ID) VALUES (%s, %s, 'U', %s)"
    c.execute(cmd, (uid, gid, gid + uid,))
    conn.commit()
    return "Success"

@app.route("/edit_group_text", methods=['POST'])
def edit_group_text():
    conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
    c = conn.cursor()
    name = request.form['editname']
    desc = request.form['editdesc']
    gid = session["groupid"]
    cmd = "UPDATE Groups SET Name=%s, Description=%s WHERE ID=%s)"
    if c.execute(cmd, (name, desc, gid,)) != 0:
        return "Success!"
    else:
        return "Failure!"

#@app.route("Authenticate", methods=['GET','POST'])
#def Auth():
#    netid = request.form['netid']
#    C = CASClient.CASClient()
#    netid = C.Authenticate()
#    return "Hurray!"
if __name__ == "__main__":
    app.run(debug=True, threaded=True)
