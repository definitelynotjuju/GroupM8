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
    if firstVisit:
        firstVisit = False
        session["logged_in"] = False
    
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
    if 'logged_in' in session and session["logged_in"]:
        return render_template("home.html")
    return redirect(url_for('index'))
@app.route("/group")
def group():
    if 'logged_in' in session and session["logged_in"]:
        return render_template("group.html")
    return redirect(url_for('index'))
@app.route("/group/<gid>")
def group2(gid):
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()
    
    cmd = "SELECT Dept, CourseN FROM Groups WHERE ID = '" + gid + "'"
    c.execute(cmd)
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
    cmd = "SELECT * FROM Users WHERE UserID = '" + netid + "' AND Password = '" + pwd + "'"
    if c.execute(cmd) == 0:
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
    cmd = "INSERT IGNORE INTO Users (UserID, FirstName, LastName, Password) Values ('" + netid + "', '" + first + "', '" + last + "', '" + pwd + "')"
    c.execute(cmd)
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
    
    cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Courses WHERE Courses.Dept = '" + session["dept"] + "' AND Courses.CourseN = '" + session["courseN"] + "' AND Users.UserID = Courses.UserID AND Courses.Availability = 'T'"
    if c.execute(cmd) == 0:
        return "[]"
    else:
        result_set = c.fetchall()
        result = []
        for row in result_set:
            cmd = "SELECT * FROM Members WHERE GroupID = '" + session["groupid"] + "' AND UserID = '" + row[0] + "'"
            if c.execute(cmd) == 0:
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
    cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Courses WHERE Courses.Dept = '" + session["dept"] + "' AND Courses.CourseN = '" + session["courseN"] + "' AND Users.UserID = Courses.UserID AND Courses.Availability = 'T'"
    if c.execute(cmd) == 0:
        return "[]"
    else:
        result_set = c.fetchall()
        result = []
        for row in result_set:
            cmd = "SELECT * FROM Members WHERE GroupID = '" + session["groupid"] + "' AND UserID = '" + row[0] + "'"
            add = True
            if c.execute(cmd) == 0:
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
    dept = request.form['dept']
    courseN = request.form['courseN']
    if dept and courseN:
        cmd = "SELECT ID, Name, Description FROM Groups WHERE Dept = '" + dept + "' AND CourseN = '" + courseN + "' AND Availability = 'T'"
        if c.execute(cmd) == 0:
            return "No groups found for this course."
        else:
            result_set = c.fetchall()
            for row in result_set:
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
    #dept = request.form['dept']
    #courseN = request.form['courseN']
    if dept and courseN:
        cmd = "SELECT ID, Name, Description FROM Groups WHERE Dept = '" + dept + "' AND CourseN = '" + courseN + "' AND Availability = 'T'"
        if c.execute(cmd) == 0:
            return "No groups found for this course."
        else:
            result_set = c.fetchall()
            for row in result_set:
                cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Members WHERE Members.GroupID = '" + str(row[0]) + "' AND Users.UserID = Members.UserID"
                result += "{\"groupid\": \"" + str(row[0]) + "\", \"name\": \"" + str(row[1]) + "\", \"description\": \"" + str(row[2]) + "\"}, "
                if c.execute(cmd) == 0:
                    return json.dumps("[]")
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
    dept = request.form['groupdept']
    courseN = request.form['groupnum']
    uid = session["userid"]
    
    if name and dept and courseN:
        cmd = "INSERT INTO Groups (Name,Dept,CourseN,Availability,Description) VALUES ('" + name + "', '" + dept + "', '" + courseN + "', 'T', '')"
        c.execute(cmd)
        conn.commit()
        cmd = "SELECT MAX(ID) FROM Groups"
        c.execute(cmd)
        ID = str(c.fetchone()[0])
        session["groupid"] = ID
        session["dept"] = dept
        session["courseN"] = courseN
        cmd = "INSERT IGNORE INTO Members (GroupID,UserID,Dept,CourseN,ID) VALUES ('" + ID + "', '" + uid + "', '" + dept + "', '" + courseN + "', '" + (ID + uid) + "')"
        c.execute(cmd)
        conn.commit()
        cmd = "INSERT IGNORE INTO Courses (UserID, Dept, CourseN, Availability,ID) Values ('" + uid + "', '" + dept + "', '" + courseN + "', 'T', '" + (uid + dept + courseN) + "')"
        c.execute(cmd)
        conn.commit()
        return render_template("group.html")

@app.route("/group_info")
def group_info():
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()
    
    cmd = "SELECT Name, Description FROM Groups WHERE ID = '" + session["groupid"] + "'"
    if c.execute(cmd) != 0:
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
    
    result = "["
    cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Members WHERE Members.GroupID = '" + session["groupid"] + "' AND Users.UserID = Members.UserID"
    if c.execute(cmd) == 0:
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
    cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Members WHERE Members.GroupID = '" + id + "' AND Users.UserID = Members.UserID"
    if c.execute(cmd) == 0:
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
    
    cmd = "SELECT FirstName, LastName FROM Users WHERE UserID = '" + session["userid"] + "'"
    if c.execute(cmd) != 0:
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
    cmd = "SELECT Availability FROM Courses WHERE UserId = '" + uid + "' AND Dept = '" + dept + "' AND CourseN = '" + coursen + "'"
    if c.execute(cmd) != 0:
        availability = str(c.fetchone()[0])
        if availability == "T":
            cmd = "UPDATE Courses SET Availability = 'F' WHERE UserID = '" + uid+ "' AND Dept = '" + dept + "' AND CourseN = '" + coursen + "'"
            c.execute(cmd)
            conn.commit()
            return 'FALSE'
        elif availability == "F":
            cmd = "UPDATE Courses SET Availability = 'T' WHERE UserID = '" + uid + "' AND Dept = '" + dept + "' AND CourseN = '" + coursen + "'"
            c.execute(cmd)
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
    
    cmd = "SELECT Availability FROM Groups WHERE ID = '" + session["groupid"] + "'"
    if c.execute(cmd) != 0:
        availability = str(c.fetchone()[0])
        if availability == "T":
            cmd = "UPDATE Groups SET Availability = 'F' WHERE ID = '" + session["groupid"] + "'"
            c.execute(cmd)
            conn.commit()
            return 'FALSE'
        elif availability == "F":
            cmd = "UPDATE Groups SET Availability = 'T' WHERE ID = '" + session["groupid"] + "'"
            c.execute(cmd)
            conn.commit()
            return 'TRUE'
    return 'UNABLE TO SET GROUP AVAILABILITY'

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
    cmd = "SELECT Dept, CourseN, Availability FROM Courses WHERE UserID = '" + uid + "'"
    if c.execute(cmd) == 0:
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
    
    result = "["
    cmd = "SELECT Availability FROM Groups WHERE ID = '" + session["groupid"] + "'"
    if c.execute(cmd) == 0:
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
    cmd = "SELECT GroupID FROM Members WHERE UserID = '" + uid + "'"
    if c.execute(cmd) == 0:
        return "[]"
    else:
        result_set = c.fetchall()
        for row in result_set:
            cmd = "SELECT Name FROM Groups WHERE ID = '" + row[0] + "'"
            c.execute(cmd)
            groupName = c.fetchone()
            result += "{\"groupid\": \"" + row[0] + "\", \"groupname\": \"" + groupName[0] + "\"}, "
        return result[:-2] + "]"

@app.route("/list_events")
def list_events():
    return "default message"

#@app.route("Authenticate", methods=['GET','POST'])
#def Auth():
#    netid = request.form['netid']
#    C = CASClient.CASClient()
#    netid = C.Authenticate()
#    return "Hurray!"
if __name__ == "__main__":
    app.run(debug=True, threaded=True)
