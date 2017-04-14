#!/usr/bin/python

# Turn on debug mode.
import cgitb
cgitb.enable()

# Print necessary headers.
print("Content-Type: DATABASE TEST")
print()

#Connect to the database
import sys
import pymysql
conn = pymysql.connect(
    db='groupm8',
    user='root',
    passwd='333groupm8',
    host='localhost')
c = conn.cursor()

def create_user(userid, firstName, lastName, password):
    cmd = "INSERT IGNORE INTO Users (UserID, FirstName, LastName, Password) Values ('" + userid + "', '" + firstName + "', '" + lastName + "', '" + password + "')"
    c.execute(cmd)
    conn.commit()

def add_course(userid, dept, courseN):
    cmd = "INSERT IGNORE INTO Courses (UserID, Dept, CourseN, Availability,ID) Values ('" + userid + "', '" + dept + "', '" + courseN + "', 'T', '" + (userid + dept + courseN) + "')"
    c.execute(cmd)
    conn.commit()

def rem_course(userid, dept, courseN):
    cmd = "DELETE FROM Courses WHERE UserID = '" + userid + "' AND Dept = '" + dept + "' AND CourseN = '" + courseN + "' AND NOT EXISTS (SELECT * FROM Members WHERE UserID = '" + userid + "' AND Dept = '" + dept + "' AND CourseN = '" + courseN + "')"
    c.execute(cmd)
    conn.commit()

def create_group(userid, name, dept, courseN, description):
    cmd = "INSERT INTO Groups (Name,Dept,CourseN,Description,Availability) VALUES ('" + name + "', '" + dept + "', '" + courseN + "', '" + description +"', 'T')"
    c.execute(cmd)
    cmd = "SELECT MAX(ID) FROM Groups"
    c.execute(cmd)
    ID = str(c.fetchone()[0])
    cmd = "INSERT IGNORE INTO Members (GroupID,UserID,Dept,CourseN,ID) VALUES ('" + ID + "', '" + userid + "', '" + dept + "', '" + courseN + "', '" + (ID + userid) + "')"
    c.execute(cmd)
    conn.commit()

def join_group(userid, groupid):
    cmd = "SELECT * FROM Groups WHERE ID = '" + groupid + "'"
    if c.execute(cmd) == 0:
        print("Group " + groupid + " does not exist.")
    else:
        cmd = "SELECT Dept FROM Groups WHERE ID = '" + groupid + "'"
        c.execute(cmd)
        dept = str(c.fetchone()[0])
        cmd = "SELECT CourseN FROM Groups WHERE ID = '" + groupid + "'"
        c.execute(cmd)
        courseN = str(c.fetchone()[0])
        cmd = "INSERT IGNORE INTO Members (GroupID,UserID,Dept,CourseN,ID) VALUES ('" + groupid + "', '" + userid + "', '" + dept + "', '" + courseN + "', '" + (ID + userid) + "')"
        c.execute(cmd)
        conn.commit()

def leave_group(userid, groupid):
    cmd = "SELECT * FROM Groups WHERE ID = '" + groupid + "'"
    if c.execute(cmd) == 0:
        print("Group " + groupid + " does not exist.")
    else:
        cmd = "DELETE FROM Members WHERE GroupID = '" + groupid + "' AND UserID = '" + userid + "'"
        c.execute(cmd)
        conn.commit()

def search_group(dept, courseN):
    cmd = "SELECT ID, Name, Description FROM Groups WHERE Dept = '" + dept + "' AND CourseN = '" + courseN + "'"
    if c.execute(cmd) == 0:
        print("No groups found for this course.")
    else:
        result_set = c.fetchall()
        for row in result_set:
            print ("ID: %s\n Name: %s\n Description: %s" % (row[0], row[1], row[2]))
        conn.commit()

def search_user(groupid, dept, courseN):
    cmd = "SELECT Users.UserID, Users.FirstName, Users.LastName FROM Users, Courses WHERE Courses.Dept = '" + dept + "' AND Courses.CourseN = '" + courseN + "' AND Users.UserID = Courses.UserID"
    if c.execute(cmd) == 0:
        print("No users found for given course.")
    else:
        result_set = c.fetchall()
        for row in result_set:
            cmd = "SELECT * FROM Members WHERE GroupID = '" + groupid + "' AND UserID = '" + row[0] + "'"
            if c.execute(cmd) == 0:
                print ("%s %s" % (row[1], row[2]))
        conn.commit()

def add_event(groupid, date, time, description):
    cmd = "INSERT INTO Events (GroupID,Date,Time,Description) Values ('" + userid + "', '" + date + "', '" + time + "', '" + description + "')"
    c.execute(cmd)
    conn.commit()

def remove_event(eventid):
    cmd = "DELETE FROM Events WHERE EventId = '" + eventid + "'"
    c.execute(cmd)
    conn.commit()

def group_desc(groupid, description):
    cmd = "UPDATE Groups SET Description = '" + description + "' WHERE GroupID = '" + groupid + "'"
    c.execute(cmd)
    conn.commit()

def event_desc(groupid, description):
    cmd = "UPDATE Events SET Description = '" + description + "' WHERE GroupID = '" + groupid + "'"
    c.execute(cmd)
    conn.commit()

def change_group_availability(groupid):
    cmd = "SELECT Availability FROM Groups WHERE GroupId = '" + groupid + "'"
    if c.execute(cmd) == 0:
        print("Group " + groupid + " does not exist.")
    else:
        availability = str(c.fetchone()[0])
        if availability == "T":
            cmd = "UPDATE GROUPS SET Availability = 'F' WHERE GroupID = '" + groupid + "'"
            c.execute(cmd)
        else:
            cmd = "UPDATE GROUPS SET Availability = 'T' WHERE GroupID = '" + groupid + "'"
        conn.commit()

cmdL = sys.argv
function = cmdL[1]
if function == "create_user":
    create_user(cmdL[2], cmdL[3], cmdL[4], cmdL[5])
if function == "add_course":
    add_course(cmdL[2], cmdL[3], cmdL[4])
if function == "rem_course":
    rem_course(cmdL[2], cmdL[3], cmdL[4])
if function == "create_group":
    create_group(cmdL[2], cmdL[3], cmdL[4], cmdL[5], cmdL[6])
if function == "join_group":
    join_group(cmdL[2], cmdL[3])
if function == "leave_group":
    leave_group(cmdL[2], cmdL[3])
if function == "search_group":
    search_group(cmdL[2], cmdL[3])
if function == "search_user":
    search_user(cmdL[2], cmdL[3], cmdL[4])
