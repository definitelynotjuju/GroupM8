from flask import Flask, render_template, request, session
#import db_functions2
import MySQLdb
import sys
import json
import re

import CASClient
#from flask_cas import CAS
#from flask_cas import login_required
app = Flask(__name__)
conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
c = conn.cursor()
#cas = CAS(app, '/cas')
#app.config['CAS_SERVER'] = 'https://fed.princeton.edu/cas'
#app.config['CAS_AFTER_LOGIN'] = 'index'
userid="js45"
groupid = "12"
dept = "COS"
courseN = "333"

@app.before_request
def session_management():
    session.permanent = True
    session["userid"] = "js45"
    session["groupid"] = "12"
    session["dept"] = "COS"
    session["courseN"] = "333"

@app.route("/")
#@login_required
def index():
    #C = CASClient.CASClient()
    #netid = C.Authenticate()
    return render_template("login.html")
    #return flask.render_template(
    #    'layout.html',
    #    username = cas.username,
    #    display_name = cas.attributes['cas:displayName']
    #    )
    #return render_template("login.html")
@app.route("/home")
def home():
    return render_template("home.html")
@app.route("/group")
def group():
    return render_template("group.html")
@app.route("/search")
def search():
    return render_template("search.html")
@app.route("/about")
def about():
    return render_template("about.html")
#@app.route("/process_query", methods=['GET','POST'])
#def process_query():
#    return request.form['query']

@app.route("/Authenticate", methods=['GET','POST'])
def Authenticate:
    netid = request.form['netid']
    pwd = request.form['pwd']
    cmd = "SELECT * FROM Users WHERE UserID = '" + netid + "' AND Password = '" + pwd + "'"
    if c.execute(cmd) == 0:
        flash('Invalid Login Info.')
        return index()
    else:
        flash('Successful Login')
        return home()

@app.route("/logout")
def logout():
    return index()

@app.route("/create_user", methods=['GET','POST'])
def create_user():
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
#    conn = MySQLdb.connect(db='groupm8', user='root', passwd='333groupm8', host='localhost')
#    c = conn.cursor()
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
    name = request.form['groupname']
    dept = request.form['groupdept']
    courseN = request.form['groupnum']
    print(name)
    print(dept)
    print(courseN)

    if name and dept and courseN:
        cmd = "INSERT INTO Groups (Name,Dept,CourseN,Availability) VALUES ('" + name + "', '" + dept + "', '" + courseN + "', 'T')"
        c.execute(cmd)
        cmd = "SELECT MAX(ID) FROM Groups"
        c.execute(cmd)
        ID = str(c.fetchone()[0])
        cmd = "INSERT IGNORE INTO Members (GroupID,UserID,Dept,CourseN,ID) VALUES ('" + ID + "', '" + userid + "', '" + dept + "', '" + courseN + "', '" + (ID + userid) + "')"
        c.execute(cmd)
        cmd = "INSERT IGNORE INTO Courses (UserID, Dept, CourseN, Availability,ID) Values ('" + userid + "', '" + dept + "', '" + courseN + "', 'T', '" + (userid + dept + courseN) + "')"
        c.execute(cmd)
        conn.commit()
        return "Completed"

@app.route("/group_info")
def group_info():
    cmd = "SELECT Name, Description FROM Groups WHERE ID = '" + session["groupid"] + "'"
    if c.execute(cmd) != 0:
        result = c.fetchall()
        return "[{\"name\": \"" + result[0][0] + "\", \"description\": \"" + result[0][1] + "\"}]"
@app.route("/group_members")
def group_members():
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
    cmd = "SELECT FirstName, LastName FROM Users WHERE UserID = '" + session["userid"] + "'"
    if c.execute(cmd) != 0:
        user = c.fetchone()
        return "[\"" + user[0] + " " + user[1] + "\"]"
    return "[]"

@app.route("/toggle_course_availability")
def toggle_course_availability():
    cmd = "SELECT Availability FROM Courses WHERE UserId = '" + userid + "' AND Dept = '" + dept + "' AND CourseN = '" + courseN + "'"
    if c.execute(cmd) != 0:
        return 0
#@app.route("Authenticate", methods=['GET','POST'])
#def Auth():
#    netid = request.form['netid']
#    C = CASClient.CASClient()
#    netid = C.Authenticate()
#    return "Hurray!"
if __name__ == "__main__":
    app.run(debug=True, threaded=True)
