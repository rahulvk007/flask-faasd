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


class Event:
    def __init__(self):
        self.body = request.get_data()
        self.headers = request.headers
        self.method = request.method
        self.query = request.args
        self.path = request.path

class Context:
    def __init__(self):
        self.hostname = os.getenv('HOSTNAME', 'localhost')

def format_status_code(resp):
    if 'statusCode' in resp:
        return resp['statusCode']
    
    return 200

def format_body(resp):
    if 'body' not in resp:
        return ""
    elif type(resp['body']) == dict:
        return jsonify(resp['body'])
    else:
        return str(resp['body'])

def format_headers(resp):
    if 'headers' not in resp:
        return []
    elif type(resp['headers']) == dict:
        headers = []
        for key in resp['headers'].keys():
            header_tuple = (key, resp['headers'][key])
            headers.append(header_tuple)
        return headers
    
    return resp['headers']

def format_response(resp):
    if resp == None:
        return ('', 200)

    statusCode = format_status_code(resp)
    body = format_body(resp)
    headers = format_headers(resp)

    return (body, statusCode, headers)

@app.route('/', defaults={'path': ''}, methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
def call_handler(path):
    event = Event()
    context = Context()
    response_data = handler.handle(event, context)
    
    resp = format_response(response_data)
    return resp

@app.route("/form",methods=['POST','GET'])
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
    
    return render_template("form.html")

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
