from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bugs.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "your_secret_key"
db = SQLAlchemy(app)


# Models
class Bug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="Open")
    comments = db.relationship("Comment", backref="bug", cascade="all, delete")


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    bug_id = db.Column(db.Integer, db.ForeignKey("bug.id"), nullable=False)


# Routes
@app.route("/")
def home():
    bugs = Bug.query.all()
    return render_template("home.html", bugs=bugs)


@app.route("/add", methods=["POST"])
def add_bug():
    title = request.form["title"]
    description = request.form["description"]
    new_bug = Bug(title=title, description=description)
    db.session.add(new_bug)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/update/<int:id>", methods=["POST"])
def update_bug(id):
    bug = Bug.query.get_or_404(id)
    bug.status = request.form["status"]
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete/<int:id>")
def delete_bug(id):
    bug = Bug.query.get_or_404(id)
    db.session.delete(bug)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/comment/<int:bug_id>", methods=["POST"])
def comment(bug_id):
    content = request.form.get("content")
    new_comment = Comment(content=content, bug_id=bug_id)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    open_bugs = Bug.query.filter_by(status="Open").count()
    in_progress = Bug.query.filter_by(status="In Progress").count()
    resolved = Bug.query.filter_by(status="Resolved").count()
    return render_template(
        "dashboard.html", open=open_bugs, progress=in_progress, resolved=resolved
    )


if __name__ == "__main__":
    app.run(debug=True)
