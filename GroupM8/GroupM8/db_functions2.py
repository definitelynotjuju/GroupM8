
def create_user(userid, firstName, lastName, password):
    cmd = "INSERT IGNORE INTO Users (UserID, FirstName, LastName, Password) Values ('" + userid + "', '" + firstName + "', '" + lastName + "', '" + password + "')"
    self.c.execute(cmd)
    self.conn.commit()
