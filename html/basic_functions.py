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
    cmd = "INSERT INTO Users (ID, FirstName, LastName, Password) VALUES ('" + userid + "', '" + firstName + "', '" + lastName + "', '" + password + "')"
    c.execute(cmd)
    gTName = "g" + userid
    cTName = "c" + userid
    rTName = "r" + userid
    cmd = "CREATE TABLE " + gTName + " (ID int NOT NULL UNIQUE)"
    c.execute(cmd)
    cmd = "CREATE TABLE " + cTName + " (Dept char(3), CourseN char(3))"
    c.execute(cmd)
    cmd = "CREATE TABLE " + rTName + " (Type char(1), F varchar(255), T varchar(255))"
    c.execute(cmd)
    cmd = "UPDATE Users Set Groups = '" + gTName + "', Courses = '" + cTName + "', Requests = '" + rTName + "' WHERE ID = '" + userid + "'"
    c.execute(cmd)
    conn.commit()
    
def create_group(userid, name, dept, courseN, description):
    cmd = "INSERT INTO Groups (Name,Dept,CourseN,Description,Availability) VALUES ('" + name + "', '" + dept + "', '" + courseN + "', '" + description +"', 'T')"
    c.execute(cmd)
    conn.commit()
    cmd = "SELECT MAX(ID) FROM Groups"
    c.execute(cmd)
    ID = str(c.fetchone()[0])
    mTName = "m" + ID
    eTName = "e" + ID
    rTName = "r" + ID
    cmd = "CREATE TABLE " + mTName + " (ID varchar(255) NOT NULL UNIQUE)"
    c.execute(cmd)
    cmd = "CREATE TABLE " + eTName + " (Day date, Time char(6), Description varchar(1000))"
    c.execute(cmd)
    cmd = "CREATE TABLE " + rTName + " (Type char(1), F varchar(255), T varchar(255))"
    c.execute(cmd)
    cmd = "UPDATE Groups Set Members = '" + mTName + "', Events = '" + eTName + "', Requests = '" + rTName + "' WHERE ID = " + ID
    c.execute(cmd)
    cmd = "INSERT INTO " + mTName + " (ID) VALUES ('" + userid + "')"
    c.execute(cmd)
    cmd = "INSERT INTO g" + userid + " (ID) VALUES (" + ID + ")"
    c.execute(cmd)
    conn.commit()

def join_group(userid, groupid):
    cmd = "SELECT Members FROM Groups WHERE ID = '" + groupid + "'"
    result = c.execute(cmd)
    if result == 0:
        print("Group " + groupid + " does not exist.")
    else:
        membersT = c.fetchone()[0]
        cmd = "SELECT Groups FROM Users WHERE ID = '" + userid + "'"
        if (c.execute(cmd) == 0):
            print("User " + userid + " does not exist.")
        else:
            groupsT = c.fetchone()[0]
            cmd = "SELECT ID FROM " + groupsT + " WHERE ID = '" + groupid + "'"
            if c.execute(cmd) != 0:
                print("User " + userid + " is already in group.")
            else:
                cmd = "SELECT ID FROM " + membersT + " WHERE ID = '" + userid + "'"
                if c.execute(cmd) != 0:
                    print("User " + userid + " is already in group.")
                else:
                    cmd = "INSERT INTO " + groupsT + " (ID) VALUES ('" + groupid + "')"
                    c.execute(cmd)
                    cmd = "INSERT INTO " + membersT + " (ID) VALUES ('" + userid + "')"
                    c.execute(cmd)
            conn.commit()

def leave_group(userid, groupid):
    cmd = "SELECT Members FROM Groups WHERE ID = '" + groupid + "'"
    if c.execute(cmd) == 0:
        print("Group " + groupid + " does not exist.")
    else:
        membersT = c.fetchone()[0]
        cmd = "SELECT Groups FROM Users WHERE ID = '" + userid + "'"
        if c.execute(cmd) == 0:
            print("User " + userid + " does not exist.")
        else:
            groupsT = c.fetchone()[0]
            cmd = "SELECT ID FROM " + membersT + " WHERE ID = '" + userid + "'"
            if c.execute(cmd) == 0:
                print("User " + userid + " is not in group " + groupid + ".")
            else:
                cmd = "DELETE FROM " + membersT + " WHERE ID = '" + userid + "'"
                c.execute(cmd)
                cmd = "SELECT ID FROM " + groupsT + " WHERE ID = '" + groupid + "'"
                if c.execute(cmd) != 0:
                    cmd = "DELETE FROM " + groupsT + " WHERE ID = '" + groupid + "'"
                    c.execute(cmd)
                cmd = "SELECT * FROM " + membersT
                if c.execute(cmd) == 0:
                    cmd = "DROP TABLES " + membersT + ",e" + groupid + ",r" + groupid
                    c.execute(cmd)
                    cmd = "DELETE FROM Groups WHERE ID = '" + groupid + "'"
                    c.execute(cmd)
                conn.commit()
                
cmdL = sys.argv
function = cmdL[1]
if function == "create_user":
    create_user(cmdL[2], cmdL[3], cmdL[4], cmdL[5])
if function == "create_group":
    create_group(cmdL[2], cmdL[3], cmdL[4], cmdL[5], cmdL[6])
if function == "join_group":
    join_group(cmdL[2], cmdL[3])
if function == "leave_group":
    leave_group(cmdL[2], cmdL[3])
