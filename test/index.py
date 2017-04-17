#!/usr/bin/python

# Print necessary headers.
print("Content-Type: text/html")
print()

# Connect to the database.
import pymysql
conn = pymysql.connect(
    db='groupm8',
    user='root',
    passwd='333groupm8',
    host='localhost')
c = conn.cursor()

# Insert some example data.

# Print the contents of the database.
c.execute("SELECT * FROM Users")
print(c.fetchall())
