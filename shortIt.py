from flask import Flask, redirect, url_for, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
import re
import datetime
import os
import secrets


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "shortenit.db")
app.secret_key = os.environ.get("SECRET_KEY", "dev-fallback-key")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Links(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    originalUrl = db.Column("originalUrl", db.String(2048))
    shortend = db.Column("shortend", db.String(100), unique=True)
    clicks = db.Column("clicks", db.Integer, default=0)
    createdAt = db.Column("CreatedAt", db.DateTime)

    def __init__(self, originalUrl, shortend, clicks, createdAt):
        self.originalUrl = originalUrl
        self.shortend = shortend
        self.clicks = clicks
        self.createdAt = createdAt

@app.route("/", methods=["GET", "POST"])
def Main():
    if request.method == "POST":
        url = request.form["url"]
        if " " in url:
            flash("Invalid URL: URLs cannot contain spaces.")
        else:
            if re.match(r"^https?://.+", url):
                while True:
                    shorten = secrets.token_urlsafe(6)
                    if not Links.query.filter_by(shortend=shorten).first():
                        break
                link = Links(originalUrl=url, shortend=shorten, clicks=0, createdAt=datetime.datetime.now(datetime.UTC))
                db.session.add(link)
                db.session.commit()
                flash(f"Your shortened URL is: {request.host_url}{shorten}")
            else:
                flash("Invalid URL: Must start with http:// or https:// and contain no spaces.")
    return render_template("index.html")

@app.route("/<shortend>")
def lookup(shortend):
    found = Links.query.filter_by(shortend=shortend).first()
    if found:
        found.clicks += 1
        db.session.commit()
        return redirect(found.originalUrl)
    else:
        return "Link Not Found", 404

@app.route("/View")
def View():
    return render_template("view.html", values=Links.query.all())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()