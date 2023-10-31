# Copyright (c) Alex Ellis 2017. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from flask import Flask, request, render_template, redirect, url_for
from function import handler
from waitress import serve
import os
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:Lug#123@db.lugvitc.org:5432/lugdb'
db = SQLAlchemy(app)
# distutils.util.strtobool() can throw an exception

class FFCS_members(db.Model):
    reg_no = db.Column(db.String(9), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    club_dept = db.Column(db.String(25), nullable=False)
    phone_no = db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, default=0)
    contributions = db.Column(db.Integer, default=0)
    expertize_in = db.Column(db.Text, default="")
    contribution_details = db.Column(db.Text, default=" ", nullable=True)
    photo = db.Column(db.Boolean, default=False, nullable=True)


def is_true(val):
    return len(val) > 0 and val.lower() == "true" or val == "1"

@app.before_request
def fix_transfer_encoding():
    """
    Sets the "wsgi.input_terminated" environment flag, thus enabling
    Werkzeug to pass chunked requests as streams.  The gunicorn server
    should set this, but it's not yet been implemented.
    """

    transfer_encoding = request.headers.get("Transfer-Encoding", None)
    if transfer_encoding == u"chunked":
        request.environ["wsgi.input_terminated"] = True

@app.route("/",methods=['POST','GET'])
def home():
    if request.method=='POST':
        details = request.form
        dict = {}
        dict['reg_no']=details["regno"]
        dict['name'] = details["name"]
        dict['club_dept']='FFCS'
        dict['phone_no'] = details["phoneno"]
        dict['email'] = details["email"]
        dict['score'] = 0
        dict['contributions'] = 0
        dict['expertize_in'] = details["exp"]
        dict['contribution_details'] = ''
        
        db.session.add(FFCS_members(**dict))
        db.session.commit()
        return "Success"
    
    test = FFCS_members.query.all()
    for i in test:
        print(i)
    return render_template("form.html")

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
