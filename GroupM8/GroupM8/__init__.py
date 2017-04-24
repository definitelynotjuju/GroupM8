from flask import Flask, render_template, request
#import db_functions2
import MySQLdb
import sys
import json
app = Flask(__name__)
conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
c = conn.cursor()
groupid = "12"
dept = "COS"
courseN = "333"

@app.route("/")
def index():
    return render_template("login.html")
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

@app.route("/search_user", methods=['GET', 'POST'])
def search_user():
#    conn = MySQLdb.connect(db='groupm8', user='root', passwd='333groupm8', host='localhost')
#    c = conn.cursor()
    cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Courses WHERE Courses.Dept = '" + dept + "' AND Courses.CourseN = '" + courseN + "' AND Users.UserID = Courses.UserID AND Courses.Availability = 'T'"
    if c.execute(cmd) == 0:
        return "No results"
    else:
        conn.commit()
        result_set = c.fetchall()
        for row in result_set:
            cmd = "SELECT * FROM Members WHERE GroupID = '" + groupid + "' AND UserID = '" + row[0] + "'"
            if c.execute(cmd) == 0:
                print ("%s %s %s" % (row[0], row[1], row[2]))
        conn.commit()
       # conn.rollback()
       # conn.close()
       #f = open("/var/www/GroupM8/GroupM8/templates/file.txt", "w")
       #f.write(result_set)
        return json.dumps(result_set)

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
        cmd = "SELECT FROM Groups WHERE ID = '" + ID + "'"
        c.execute(cmd)
        return json.dumps(c.fetchall())
if __name__ == "__main__":
    app.run(debug=True)
