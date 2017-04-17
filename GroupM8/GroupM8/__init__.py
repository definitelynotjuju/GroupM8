from flask import Flask, render_template, request
app = Flask(__name__)
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
if __name__ == "__main__":
    app.run(debug=True)
