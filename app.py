from flask import Flask
from flask import redirect, render_template, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
import hashlib
import os
import config


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://%s:%s@%s/%s" % (config.DB_USER,
                                                                 config.DB_PASSWORD,
                                                                 config.DB_HOST,
                                                                 config.DB_TABLE)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class URL(db.Model):
    short = db.Column(db.String(7), primary_key=True, unique=True)
    full = db.Column(db.String(254), unique=True)

    def __init__(self, short, full):
        self.short = short
        self.full = full


db.create_all()
db.session.commit()


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        full_url = request.form['full_url']
        md5 = hashlib.md5(full_url.encode()).hexdigest()[0:7]
        new_url = URL(md5, full_url)
        url = URL.query.filter_by(short=md5).first()
        if request.base_url not in full_url:
            flash(request.base_url + md5)
            if not url:
                db.session.add(new_url)
                db.session.commit()
        else:
            flash('That is already shorted link')
        return render_template('index.html')
    return render_template('index.html')


@app.route('/<new>', methods=['GET'])
def redirect_to_new(new):
    url = URL.query.filter_by(short=new).first()
    if url:
        return redirect(url.full)
    else:
        abort(404)


if __name__ == '__main__':
    app.run()
