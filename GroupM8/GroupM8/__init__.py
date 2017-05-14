from flask import Flask, render_template, request, session, flash, redirect, url_for, send_from_directory
import MySQLdb
import sys
import json
import re
from datetime import datetime, timedelta
import pytz

from flask_cas import CAS
from flask_cas import login
from flask_cas import logout
from flask_cas import login_required

app = Flask(__name__)
cas = CAS(app, '/cas')
app.config['CAS_SERVER'] = 'https://fed.princeton.edu/cas'
app.config['CAS_AFTER_LOGIN'] = 'home'
app.config['CAS_AFTER_LOGOUT'] = 'home'

@app.before_request
def session_management():
    #makes the session permanent as long as not logged out through CAS
    session.permanent = True

@app.route("/")
@login_required
def index():
    #redirects to the home page
    return redirect(url_for('home'))

@app.route("/home")
@login_required
def home():
    #catch the netid/userid from CAS
    session["userid"] = cas.username
    uid = session["userid"]

    #connect to the database
    conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
    c = conn.cursor()

    #check to see if it is a new user
    cmd = "SELECT * FROM Users WHERE UserID = %s"

    if c.execute(cmd, (uid,)) == 0:
        #add new user to the database
        cmd = "INSERT IGNORE INTO Users (UserID) VALUES (%s)"
        c.execute(cmd, (uid,))
        conn.commit()
        
    #render the template for the home page        
    return render_template("home.html")

@app.route("/group")
@login_required
def group():
    #redirect to home if netid/userid has not been saved from CAS
    if 'userid' not in session:
        return redirect(url_for('home'))

    #connect to the database
    conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
    c = conn.cursor()

    uid = session["userid"]
    gid = session["groupid"]

    #Check to see if user is part of group with ID = gid
    cmd = "SELECT * FROM Members WHERE UserID = %s AND GroupID = %s"
    
    if c.execute(cmd, (uid, gid,)) == 0:
        return render_template("access.html")
    
    #render the group page
    return render_template("group.html")

@app.route("/group/<gid>")
@login_required
def group2(gid):
    #Check to see if netid/userid is saved from CAS
    if 'userid' not in session:
        return redirect(url_for('home'))

    #connect to the database
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()
    
    uid = session["userid"]

    #Check if user is in the group with ID = gid
    cmd = "SELECT * FROM Members WHERE UserID = %s AND GroupID = %s"

    if c.execute(cmd, (uid, gid,)) == 0:
        return render_template("access.html")

    #Save the new current group, its dept, and courseN
    cmd = "SELECT Dept, CourseN FROM Groups WHERE ID = %s"
    c.execute(cmd, (gid,))
    result = c.fetchone()
    session["groupid"] = gid
    session["dept"] = result[0]
    session["courseN"] = result[1]

    #redirect to group function @ route ("/group")
    return redirect(url_for('group'))

@app.route("/search")
@login_required
def search():
    #Check if netid/userid is saved from CAS
    if 'userid' not in session:
        return redirect(url_for('home'))
    
    #render the search page
    return render_template("search.html")

@app.route("/about")
def about():
    #render the group project status page
    return render_template("about.html")

@app.route("/static/<path:path>")
def load_static_files(path):
    #returns the files in the static directory
    return send_from_directory("", path)

#returns the current group's id, dept, and courseN
@app.route("/current_gid")
def groupid():
    return session["groupid"] + session["dept"] + session["courseN"]

#Returns a list of potential members for the group with an empty query
@app.route("/search_user/")
def search_user():
    #connect to the database
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    dept = session["dept"]
    courseN = session["courseN"]

    #Grabs a list of Users in the course that have their availability set to 'T' (True)
    cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Courses WHERE Courses.Dept = %s AND Courses.CourseN = %s AND Users.UserID = Courses.UserID AND Courses.Availability = 'T'"
    if c.execute(cmd, (dept, courseN,)) == 0:
        return "[]"
    else:
        result_set = c.fetchall()
        result = []
        for row in result_set:
            #Filter our users already in the group or have requests/invitations for the group
            gid = session["groupid"]
            cmd = "SELECT * FROM Members WHERE GroupID = %s AND UserID = %s"
            if c.execute(cmd, (gid, row[0],)) == 0:
                cmd = "SELECT * FROM Requests WHERE GroupID = %s AND UserID = %s"
                if c.execute(cmd, (gid, row[0],)) == 0:
                    result.append(row)

        #return a JSON of the list of users
        return json.dumps(result)

#Returns a list of potential members for the group filtered with a query
@app.route("/search_user/<query>")
def search_user2(query):
    #Connect to the database
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()
    
    queryA = query.split()

    dept = session["dept"]
    courseN = session["courseN"]

    #Grabs a list of users currently looking for a group for the group's course
    cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Courses WHERE Courses.Dept = %s AND Courses.CourseN = %s AND Users.UserID = Courses.UserID AND Courses.Availability = 'T'"
    if c.execute(cmd, (dept, courseN,)) == 0:
        return "[]"
    else:
        result_set = c.fetchall()
        result = []
        for row in result_set:
            #Filter out users already in the group or has a request/invitation for the group
            #Filters the remaining list with a query
            gid = session["groupid"]
            cmd = "SELECT * FROM Members WHERE GroupID = %s AND UserID = %s"
            add = True
            if c.execute(cmd, (gid, row[0],)) == 0:
                for i in queryA:
                    if (row[0].upper()).startswith(i.upper()):
                        continue
                    elif (row[1].upper()).startswith(i.upper()):
                        continue
                    elif (row[2].upper()).startswith(i.upper()):
                        continue
                    else:
                        add = False
                        break
                if add:
                    cmd = "SELECT * FROM Requests WHERE GroupID = %s AND UserID = %s"
                    if c.execute(cmd, (gid, row[0],)) == 0:
                        result.append(row)
        if len(result) == 0:
            return "[]"
        return json.dumps(result)
            
#Returns a list of groups for the course (dept, courseN) in JSON and "F" if the resulting list is empty
@app.route("/search_group/")
def search_group2():
    #connect to the database
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()
    
    result = "["
    uid = session["userid"]
    dept = request.args.get('dept', '', type=str)
    courseN = request.args.get('courseN', '', type=str)
    
    if dept and courseN:
        #Grabs a list of groups with the corresponding dept and courseN
        cmd = "SELECT ID, Name, Description FROM Groups WHERE Dept = %s AND CourseN = %s AND Availability = 'T'"
        if c.execute(cmd, (dept, courseN,)) == 0:
            return "F"
        else:
            #Filter out groups the user is already in and groups that the user has a request/invitation for
            result_set = c.fetchall()
            for row in result_set:
                cmd = "SELECT * FROM Members WHERE GroupID = %s AND UserID = %s"
                if c.execute(cmd, (row[0], uid,)) == 0:
                    cmd = "SELECT * FROM Requests WHERE GroupID = %s AND UserID = %s"
                    if c.execute(cmd, (row[0], uid,)) == 0:
                        result += "{\"groupid\": \"" + str(row[0]) + "\", \"name\": \"" + str(row[1]) + "\", \"description\": \"" + str(row[2]) + "\"}, "
            if len(result) == 1:
                return "F"
            result = result[:-2] + "]"
            return result


#Creates a new group (Add a new entry to the Groups table in the database)
@app.route("/create_group", methods=['GET','POST'])
def create_group():
    #connect to the database                 
    conn = MySQLdb.connect(
        db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    #Retrieve input from the html form
    name = request.form['groupname']
    dept = request.form['groupdept'].upper()
    courseN = request.form['groupnum']
    uid = session["userid"]
    
    if name and dept and courseN:
        #Insert a new entry into the Groups table in the database
        cmd = "INSERT INTO Groups (Name,Dept,CourseN,Availability,Description) VALUES (%s, %s, %s, 'T', 'No description (yet)')"
        c.execute(cmd, (name, dept, courseN,))
        conn.commit()
        cmd = "SELECT MAX(ID) FROM Groups"
        c.execute(cmd)
        ID = str(c.fetchone()[0])
        
        #Update current group information
        session["groupid"] = ID
        session["dept"] = dept
        session["courseN"] = courseN

        #Add user as member of the group created (Add a new entry to the Members table)
        tempid = ID + uid
        newtempid = uid + dept + courseN
        cmd = "INSERT IGNORE INTO Members (GroupID,UserID,Dept,CourseN,ID) VALUES (%s, %s, %s, %s, %s)"
        c.execute(cmd, (ID, uid, dept, courseN, tempid,))
        conn.commit()

        #Add the course to the user's course list if its not already added (Add a new course to the Course table if it doesn't exist for the user)
        cmd = "INSERT IGNORE INTO Courses (UserID, Dept, CourseN, Availability,ID) Values (%s, %s, %s, 'T', %s)"
        c.execute(cmd, (uid, dept, courseN, newtempid,))
        conn.commit()

        #Renders the group page (refreshes the page to correct the address bar)
        return render_template("group.html", refresh = "True")

#Adds a course for the user to the Course table in the database
@app.route("/add_course", methods=['GET', 'POST'])
def add_course():
    #Connect to the database
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    #Retrieve inputs from the HTML form
    dept = request.form['coursedept'].upper()
    courseN = request.form['coursenum']
    uid = session["userid"]
    tempid = uid + dept + courseN

    #Add the course for the user if it the user does not have the course added
    if dept and courseN:
        cmd = "INSERT IGNORE INTO Courses (UserID,Dept,CourseN,Availability,ID) VALUES (%s, %s, %s, 'T', %s)"
        c.execute(cmd, (uid, dept, courseN, tempid,))
        conn.commit()
        return render_template("home.html", refresh = "True")

#Returns a JSON of the current group's information (name, description, dept, and courseN)
@app.route("/group_info")
def group_info():
    #Connect to the database
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    gid = session["groupid"]
    cmd = "SELECT Name, Description, Dept, CourseN FROM Groups WHERE ID = %s"
    if c.execute(cmd, (gid,)) != 0:
        result = c.fetchone()
        return json.dumps(result)
    
    return "[]"

#Returns a list of the members in the current group (JSON format)
#Returns userid and name ("FirstName LastName")
@app.route("/group_members")
def group_members():
    #Connect to the database
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    gid = session["groupid"]
    result = "["

    #Grabs a list of Users that are in the current group
    cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Members WHERE Members.GroupID = %s AND Users.UserID = Members.UserID"
    if c.execute(cmd, (gid,)) == 0:
        return "[]"
    else:
        members = c.fetchall()
        for member in members:
            result += "{\"userid\": \"" + member[0] + "\", \"name\": \"" + member[1] + " " + member[2] + "\"},"
        result = result[:-1] + "]"
    return result

#Returns a list of members for the group with the given GroupID (id) (JSON format)
@app.route("/group_members/")
def group_members2():
    #Connect to the database
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    result = "["
    gid = request.args.get('gid', '', type=str)
    #Grabs a list of Users that are in the given group (from the id)
    cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Members WHERE Members.GroupID = %s AND Users.UserID = Members.UserID"
    if c.execute(cmd, (gid,)) == 0:
        return "[]"
    else:
        members = c.fetchall()
        for member in members:
            result += "{\"userid\": \"" + member[0] + "\", \"name\": \"" + member[1] + " " + member[2] + "\"},"
        result = result[:-1] + "]"
        return result


#Returns the user's information (currently the user's full name)
@app.route("/user_info")
def user_info():
    #Connect to the database
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    uid = session["userid"]
    cmd = "SELECT FirstName, LastName FROM Users WHERE UserID = %s"
    if c.execute(cmd, (uid,)) != 0:
        user = c.fetchone()
        return "[\"" + user[0] + " " + user[1] + "\"]"
    return "[]"

#Toggles the availability for the user's given course ("T" -> "F" or "F" -> "T")
@app.route("/toggle_course_availability/<dept>/<coursen>")
def toggle_course_availability(dept, coursen):
    #Connect to the database
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    uid = session["userid"]

    #Get the availability for the user's course
    cmd = "SELECT Availability FROM Courses WHERE UserId = %s AND Dept = %s AND CourseN = %s"
    if c.execute(cmd, (uid, dept, coursen,)) != 0:
        availability = str(c.fetchone()[0])
        #Change the availability
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

#Toggles the availability for the current group ("T" -> "F" or "F" -> "T")
@app.route("/toggle_group_availability/<value>")
def toggle_group_availability(value):
    #Connect to the database
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    gid = session["groupid"]
    
    #Get the current availability for the current group
    cmd = "SELECT Availability FROM Groups WHERE ID = %s"
    if c.execute(cmd, (gid,)) != 0:
        availability = str(c.fetchone()[0])
        #Change the availability
        if availability == "T":
            if value == "no":
                cmd = "UPDATE Groups SET Availability = 'F' WHERE ID = %s"
                c.execute(cmd, (gid,))
                conn.commit()
                return 'FALSE'
            else:
                return 'TRUE'
        elif availability == "F":
            if value == "yes":
                cmd = "UPDATE Groups SET Availability = 'T' WHERE ID = %s"
                c.execute(cmd, (gid,))
                conn.commit()
                return 'TRUE'
            else:
                return 'FALSE'
    return 'UNABLE TO SET GROUP AVAILABILITY'

#Removes the given course for the user (Remove the entry from the Courses table)
@app.route("/remove_course/<dept>/<coursen>")
def remove_course(dept, coursen):
    #Connect to the database                   
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    uid = session["userid"]

    #Delete the corresponding course entry from the Courses table
    cmd = "DELETE FROM Courses WHERE UserID = %s AND Dept = %s AND CourseN = %s"
    if c.execute(cmd, (uid, dept.upper(), coursen,)) != 0:
        #Are we supposed to do this?
        cmd = "DELETE FROM Members WHERE UserID = %s AND Dept = %s AND CourseN = %s"
        c.execute(cmd, (uid, dept.upper(), coursen,))
        conn.commit()
        return "Success!"
    return 'UNABLE TO REMOVE COURSE'

#Removes the group for the user (ie. leave the group)
@app.route("/remove_group", methods=['POST'])
def remove_group():
    #Connect to the database
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    uid = session["userid"]
    groupid = session["groupid"]

    #Delete the user's member entry for the group in the Members table
    cmd = "DELETE FROM Members WHERE GroupID = %s AND UserID = %s"
    if c.execute(cmd, (groupid, uid)) != 0:
        conn.commit()
    else:
        return 'UNABLE TO REMOVE GROUP'

    #If there are no more members in the group, delete the group and all its events and requests
    cmd = "SELECT * FROM Members WHERE GroupID = %s"
    if c.execute(cmd, (groupid,)) == 0:
        cmd = "DELETE FROM Groups WHERE ID = %s"
        c.execute(cmd, (groupid,))
        conn.commit()
        cmd = "DELETE FROM Requests WHERE GroupID = %s"
        c.execute(cmd, (groupid,))
        conn.commit()
        cmd = "DELETE FROM Events WHERE GroupID = %s"
        c.execute(cmd, (groupid,))
        conn.commit()
        
    return "success!"

#Returns a list of the user's courses (JSON)
@app.route("/list_courses")
def list_courses():
    #Connect to the database
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()
    
    result = "["
    uid = session["userid"]

    #Grabs a list of courses the user is currently in
    cmd = "SELECT Dept, CourseN, Availability FROM Courses WHERE UserID = %s"
    if c.execute(cmd, (uid,)) == 0:
        return "[]"
    else:
        courses = c.fetchall()
        for clas in courses:
            result += "{\"dept\": \"" + clas[0] + "\", \"coursen\": \"" + clas[1] + "\", \"availability\": \"" + clas[2] + "\"},"
        result = result[:-1] + "]"
        return result

#Returns the availability for the current group
@app.route("/check_group_availability")
def check_group_availability():
    #Connect to the database                 
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    gid = session["groupid"]
    result = "["
    cmd = "SELECT Availability FROM Groups WHERE ID = %s"
    if c.execute(cmd, (gid,)) == 0:
        return "ERROR"
    else:
        availability = str(c.fetchone() [0])
        return availability

#Returns a list of groups that the user is currently in (JSON)
#attributes: groupid, groupname, groupdept, groupcoursenum
@app.route("/list_groups")
def list_groups():
    #Connect to the database
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    uid = session["userid"]
    result = "["

    #Grabs a list of groups the user is currently in
    #Construct a JSON string from the data
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

#Returns a list of events for the current group (JSON)
#attributes: id, name, date, time, desc (description), repeating (frequency)
@app.route("/list_events")
def list_events():
    #Connect to the database
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()
    
    uid = session["userid"]
    groupid = session["groupid"]

    #calibrates the date and time of the server
    local_tz = pytz.timezone('US/Eastern')
    f = '%m/%d/%Y %I:%M %p'
    
    local_dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(local_tz)

    event_tuples = []
    results = "["

    #Grabs a list of events for the current group
    #Construct a JSON string from the data
    cmd = "SELECT Date, Time, Description, Name, Repeating, ID FROM Events WHERE GroupID = %s"
    if c.execute(cmd, (groupid,)) == 0:
        return "[]"
    else:
        events = c.fetchall()
        for event in events:
            date_string = event[0] + " " + event[1]
            event_dt = local_tz.localize(datetime.strptime(date_string, f))
            #Displays all events that are in the future and none that are in the past
            if local_dt <= event_dt:
                event_tuples.append((event_dt, str(event[5]), event[3], event[2], event[4]))
            else:
                #Removes events from the past and replaces them with the next repeating event (if there is one)
                freq = event[4]
                #Deletes a one-time event that has already passed
                if freq == "never":
                    cmd = "DELETE FROM Events WHERE ID = %s"
                    c.execute(cmd, (event[5],))
                    conn.commit()
                #Updates a repeating event to its next meeting
                else:
                    d = timedelta()
                    if freq == "daily":
                        d = timedelta(days=1)
                    elif freq == "weekly":
                        d = timedelta(weeks=1)
                    else:
                        d = timedelta(weeks=2)
                    new_dt = event_dt + d
                    cmd = "UPDATE Events SET Date = %s, Time = %s WHERE ID = %s"
                    c.execute(cmd, (new_dt.strftime("%m/%d/%Y"), new_dt.strftime("%I:%M %p"), str(event[5]),))
                    conn.commit()
                    event_tuples.append((new_dt, str(event[5]), event[3], event[2], event[4]))
                        
        sorted_events = sorted(event_tuples, key = lambda tup: tup[0])

        if len(sorted_events) == 0:
            return "[]"

        for e in sorted_events:
            results += ("{\"date\": \"" + e[0].strftime("%m/%d/%Y") + "\", \"time\": \"" + e[0].strftime("%I:%M %p") +
                        "\", \"id\": \"" + e[1] + "\", \"name\": \"" + e[2] + "\", \"desc\": \"" + e[3] + 
                        "\", \"repeating\": \"" + e[4] + "\"}, ")
        return results[:-2] + "]"

    
#Add a new event for the current group
@app.route("/add_event", methods=['GET', 'POST'])
def add_event():
    #Connect to the database          
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    #Retrieve the inputs from the HTML form
    name = request.form['eventname']
    desc = request.form['eventdesc']
    date = request.form['date']
    hour = request.form['hour']
    minutes = request.form['minutes']
    ampm = request.form['ampm']
    repeating = request.form['repeating']
    time = "" + hour + ":" + minutes + " " + ampm
    dt_string = date + " " + time

    if date == "":
        return render_template("group.html")

    #Calibrates the time of the server
    local_tz = pytz.timezone('US/Eastern')
    f = '%m/%d/%Y %I:%M %p'

    event_dt = local_tz.localize(datetime.strptime(dt_string, f))
    local_dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(local_tz)

    #Prevents adding events that would have happened in the past
    if event_dt < local_dt:
        return render_template("group.html", passed = "True")
    
    uid = session["userid"]
    groupid = session["groupid"]

    #Insert the new event entry into the Event table in the database
    cmd = "INSERT INTO Events (GroupID,Date,Time,Description, Name, Repeating) VALUES (%s, %s, %s, %s, %s, %s)"
    c.execute(cmd, (groupid, date, time, desc, name, repeating))
    conn.commit()

    #Render the group page and refresh it
    return render_template("group.html", refresh = "True")


#Remove the event entry with ID = eventid (Delete the event for the group.)
@app.route("/remove_event", methods=['POST'])
def remove_event():

    #connects to database
    conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
    c = conn.cursor()

    #deletes selected event
    eventid = request.form['id']
    cmd =  "DELETE FROM Events WHERE ID = %s"
    c.execute(cmd, (eventid,))
    conn.commit()
    return "Success"

#Returns a list of invitations sent to the user (JSON)
#attributes: requestid, groupid, groupname, groupdesc
@app.route("/list_user_requests")
def list_user_requests():

    #Connects to database
    conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
    c = conn.cursor()

    #Grab a list of invitations sent to the user
    #Formats data as a JSON string
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
    else:
        return "[]"

#Returns a list of pending requests the user has sent out (JSON)
#attributes: requestid, groupid, groupname, groupdesc
@app.route("/list_user_requests2")
def list_user_requests2():

    #connects to database
    conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
    c = conn.cursor()

    #Grabs the list of requests a user has sent out
    #Formats data as a JSON string
    result = ""
    uid = session["userid"]
    cmd = "SELECT ID, GroupID FROM Requests WHERE UserID = %s AND Type = 'U'"
    if c.execute(cmd, (uid,)) != 0:
        result = "["
        requests_set = c.fetchall()
        for row in requests_set:
            result += "{\"requestid\": \"" + row[0] + "\", \"groupid\": \"" + row[1] + "\", "
            cmd = "SELECT Name, Description FROM Groups WHERE ID = %s"
            if c.execute(cmd, (row[1],)) != 0:
                group_info = c.fetchone()
                result += "\"groupname\": \"" + group_info[0] + "\", \"groupdesc\": \"" + group_info[1] + "\"}, "
        result = result[:-2] + "]"
        return result
    else:
        return "[]"
                                                                                                            
#Returns a list of requests based on the type t for the group (JSON)
#type t: "U" -> sent by user  "G" -> sent by groups
#attributes: requestid, userid, username("FirstName LastName")
@app.route("/list_group_requests/<t>")
def list_group_requests(t):
                                            
    #Connects to database
    conn = MySQLdb.connect(
                db='groupm8',
                user='root',
                passwd='333groupm8',
                host='localhost')
    c = conn.cursor()

    #Grabs the list of requests sent to a group
    #Returns result as a JSON string
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

#Process the coreesponding request(rid) based on the response ("A" to accept)
#Accept: add a new entry to the Members table for the user that just joined (the course as well if the user does not already have it)
@app.route("/process_request/<rid>/<response>")
def process_request(rid, response):

    #Connects to database
    conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
    c = conn.cursor()

    #Accepting adds a user to the given group based off the data in the request table
    #Removes request when processsing is complete
    if response == 'A':
        cmd = "SELECT UserID, GroupID FROM Requests WHERE ID = %s"
        if c.execute(cmd, (rid,)) != 0:
            request_info = c.fetchone()
            uid = request_info[0]
            gid = request_info[1]
            cmd = "SELECT Dept, CourseN, Availability FROM Groups WHERE ID = %s"
            if c.execute(cmd, (gid,)) != 0:
                group_info = c.fetchone()
                dept = group_info[0]
                courseN = group_info[1]
                a = group_info[2]
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

#Send an invitation from the current group to the user (uid)
@app.route("/send_invitation/<uid>")
def send_invitation(uid):
                                            
    #Connects to database
    conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
    c = conn.cursor()

    gid = session["groupid"]
    dept = session["dept"]
    courseN = session["courseN"]
    #Checks to see whether a user has marked themselves as unavailable
    cmd = "SELECT Availability FROM Courses WHERE UserID = %s AND Dept = %s AND CourseN = %s"
    if c.execute(cmd, (uid, dept, courseN,)) == 0:
        return "[]"
    else:
        a = c.fetchone()
        if a[0] == "F":
            return "[]"
        else:
            #Sends a request when a user has marked themselves as available
            cmd = "INSERT IGNORE INTO Requests (UserID, GroupID, Type, ID) VALUES (%s, %s, 'G', %s)"
            c.execute(cmd, (uid, gid, gid + uid,))
            conn.commit()
            return "[]"

#Send a request from the user to the corresponding group (gid)
@app.route("/send_request/<gid>")
def send_request(gid):
                                                
    #Connects to database
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

#Edit the group's name and/or description
@app.route("/edit_group_text", methods=['POST'])
def edit_group_text():
                                                
    #Connects to database
    conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
    c = conn.cursor()
    name = request.form['editname']
    desc = request.form['editdesc']
    gid = session["groupid"]
    cmd = "UPDATE Groups SET Name=%s, Description=%s WHERE ID=%s"
    if c.execute(cmd, (name, desc, gid,)) != 0:
        conn.commit()
        return "Success!"
    else:
        return "Failure!"


#Edit the name of the user
@app.route("/edit_username", methods=['POST'])
def edit_username():
                                                
    #Connects to database
    conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
    c = conn.cursor()

    #Updates the user's name based on their input. On a user's first login, the field will be blank
    name = request.form['editname']
    names = name.split(' ');
    uid = session["userid"]
    cmd = "UPDATE Users SET FirstName=%s, LastName=%s WHERE UserID=%s"
    if c.execute(cmd, (names[0], names[1], uid,)) != 0:
        conn.commit()
        return "Success!"
    else:
        return "Failure."


#List the upcoming n events for the user (from all the groups the user is currently in)
@app.route("/list_user_events")
def list_next_n_events():
                                                
    #Connects to the database
    conn = MySQLdb.connect(
        db='groupm8',
        user='root',
        passwd='333groupm8',
        host='localhost')
    c = conn.cursor()

    n = 3
    event_tuples = []
    uid = session["userid"]
    local_tz = pytz.timezone('US/Eastern')
    f = '%m/%d/%Y %I:%M %p'
    
    cmd = "SELECT GroupID FROM Members WHERE UserID = %s"
    if c.execute(cmd, (uid,)) != 0:
        groups = c.fetchall()

        #Get a list of events that have not passed (for the user)
        for group in groups:
            now = datetime.utcnow()
            local_dt = now.replace(tzinfo=pytz.utc).astimezone(local_tz)

            cmd = "SELECT ID, Name, Description, Date, Repeating, Time FROM Events WHERE GroupID = %s"
            if c.execute(cmd, (group[0],)) != 0:
                events = c.fetchall()
                for event_info in events: 
                    date_string = event_info[3] + " " + event_info[5]
                    event_dt = datetime.strptime(date_string, f)
                    new_event_dt = local_tz.localize(event_dt)
                    if local_dt <= new_event_dt:
                        cmd = "SELECT Name, Dept, CourseN FROM Groups WHERE ID = %s"
                        if c.execute(cmd, (group[0],)) != 0:
                            group_info = c.fetchone()
                            event_tuples.append((new_event_dt, str(event_info[0]), event_info[1], event_info[2], group[0], group_info[0], group_info[1], group_info[2]))
                    else:
                        freq = event_info[4]
                        cmd = "SELECT Name, Dept, CourseN FROM Groups WHERE ID = %s"
                        if freq == "never" or c.execute(cmd, (group[0],)) == 0:
                            cmd = "DELETE FROM Events WHERE ID = %s"
                            c.execute(cmd, (event_info[0],))
                            conn.commit()
                        else:
                            group_info = c.fetchone()
                            d = timedelta()
                            if freq == "daily":
                                d = timedelta(days=1)
                            elif freq == "weekly":
                                d = timedelta(weeks=1)
                            else:
                                d = timedelta(weeks=2)
                            new_dt = new_event_dt + d
                            cmd = "UPDATE Events SET Date = %s, Time = %s WHERE ID = %s"
                            c.execute(cmd, (new_dt.strftime("%m/%d/%Y"), new_dt.strftime("%I:%M %p"), event_info[0],))
                            conn.commit()
                            event_tuples.append((new_dt, str(event_info[0]), even_info[1], event_info[2], group[0], group_info[0], group_info[1], group_info[2]))
        #Sort the events by their date and time
        sorted_events = sorted(event_tuples, key = lambda tup: tup[0])
        if len(sorted_events) == 0:
            return "[]"

        #Return the first n events
        results = "["
        for i in range(0, min(n, len(sorted_events))):
            e = sorted_events[i]
            results += ("{\"eventid\": \"" + e[1] + "\", \"eventname\": \"" + e[2] + "\", \"eventdesc\": \"" + e[3] +
                        "\", \"datetime\": \"" + e[0].strftime(f) + "\", \"groupid\": \"" + e[4] + "\", \"groupname\": \""
                        + e[5] + "\", \"dept\": \"" + e[6] + "\", \"courseN\": \"" + e[7] + "\"}, ")
            
        return results[:-2] + "]"
    return "no groups"

#Logout handler
@app.route("/logging_out")
def logging_out():
    if 'userid' in session:
        del session['userid']
    return redirect(url_for('cas.logout'))

if __name__ == "__main__":
    app.run(debug=True)
