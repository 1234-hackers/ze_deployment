import base64
from email import message
from dns.message import Message
from flask import Flask, render_template, url_for, request, redirect,flash,session
from flask.scaffold import F
from flask_pymongo import PyMongo
from flask_wtf.form import FlaskForm
from pymongo import MongoClient
import passlib
from passlib.context import CryptContext
from passlib.hash import bcrypt_sha256,argon2,ldap_salted_md5,md5_crypt
import time
from datetime import  datetime as dt
import smtplib
from email.message import EmailMessage
import socket,os
from functools import wraps
from gridfs import*
from bson import ObjectId
#from flask_hcaptcha import hCaptcha
from flask_wtf.csrf import CSRFProtect,CSRFError
from wtforms.csrf.session import SessionCSRF 
from datetime import timedelta
import email_validator 
import random
#from flask_mail import Mail,Message
from bson.binary import Binary
from werkzeug.utils import secure_filename
import asyncio
import markupsafe
from markupsafe import escape , Markup

from postmarker.core import PostmarkClient
ip = socket. gethostbyname(socket. gethostname())


from fpdf import FPDF
ipst = str(ip)
application = Flask(__name__)

#captcha
application.config['HCAPTCHA_ENABLED'] =  False
application.config ["HCAPTCHA_SITE_KEY"]  =  "cd654ebc-97ad-44fb-8ddc-963287c6d77b"
application.config ['HCAPTCHA_SECRET_KEY'] = "0xb1E280895395797DCF11D0B1807aa9678A4B391d" 

#hcaptcha = hCaptcha(application)

upload_folder = 'static/images'
application.config['UPLOAD_FOLDER'] = upload_folder
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])



#csrf protection
SECRET_KEY = "dsfdsjgdjgdfgdfioaskiskladsdpoadsdskkjzcxn dfsgjdkjgdg"
csrf = CSRFProtect(application)

application.config['MONGO_DBNAME'] = 'users'
application.config['MONGO_URI'] = 'mongodb://localhost:27017/dons'
mongo = PyMongo(application)
client = MongoClient('localhost', 27017)
application.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

Hash_passcode = CryptContext(schemes=["sha256_crypt", "des_crypt" ],sha256_crypt__min_rounds=17072)

mongo = PyMongo(application)
users = mongo.db.users
doanations = mongo.db.donations
verif = mongo.db.verify_email
dbx = mongo.db.p_classes

def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if "login_user" in session:
            return f(*args,**kwargs,)
        else:
            time.sleep(2)
            return redirect(url_for('login'))
    return wrap


@application.route('/',methods = ["POST","GET"])
def home():

    return render_template("landing.html")

@application.route('/donate/',methods=["POST","GET"])
def donate():
    # session.pop('meth',None)
    # if request.method =="POST":
    #     data_class = request.form['sb']
    #     if data_class == "ether":


    #         return redirect(url_for('copy_address'))
        
    #     if  dc == "stripe":
         
    #         return redirect(url_for('copy_address'))
        
    #     if  dc3 == "paypal":
       
    #         return redirect(url_for('copy_address'))


    return render_template('donate.html')

@application.route('/stripe/' , methods=["POST" , "GET"])
def stripe():

    return render_template('de_stripe.html')

@application.route('/paypal/' , methods=["POST" , "GET"])
def paypal():

    return render_template('de_paypal.html')

@application.route('/skrill/' , methods=["POST" , "GET"])
def skrill():

    return render_template('de_skrill.html')

#crypto
@application.route('/ether/' , methods=["POST" , "GET"])
def ether():

    return render_template('de_ether.html')

@application.route('/monero/' , methods=["POST" , "GET"])
def monero():

    return render_template('de_monero.html')

@application.route('/usdt/' , methods=["POST" , "GET"])
def usdt():

    return render_template('de_usdt.html')



@application.route('/copy_address/' , methods=["POST" , "GET"])
def copy_address():
    data_class = session.get('meth')
    found = dbx.find({"tunn" : data_class})

    return render_template('copy_add.html', x = data_class)

@application.route('/contact/' , methods=["POST" , "GET"])
def contact():
    the_db = mongo.db.inquiries
    if request.method == "POST":

        em = request.form['email']

        desc = request.form['desc']

        inq = request.form['inq']

        the_db.insert_one({"email" : em , "inquiry" : inq , "description" : desc , "cond" : 1})

        return render_template('inq_sent.html')


    return render_template('contact.html')

@application.route('/confirm_pdf/' , methods = ['POST','GET'])
def confirm_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial" , size = 15)

    pdf.cell(200,10,txt = "Thank you for your donation" , ln = 1 ,align = 'C')

    pdf.cell(200,10,txt = "This jjsfiosfsjb   jisfiwjefiosdfisio  oj ijgsifjsiojfods    iofsiofj" , ln = 2 ,align = 'c')

    naez = "james@gmail.com"
    naez2 = naez.replace("." , "")
    pdf.output(  naez2 + ".pdf")
    name2 =  naez2 + ".pdf"




    return render_template('pdfdata.html' , name2=naez2)

@application.route('/goods/' , methods=['POST' , 'GET'])
def goods():



    return render_template('goods.html')
@application.route('/reset_pass/', methods = ['POST','GET'])
def  reset_pass():
    reset_db = mongo.db.pass_reset
    code = random.randint(145346 , 976578)
    code = str(code)
    if request.method == "POST":
        email = request.form['email']
        existing = users.find_one({'email':email} )
        if existing:

            '''
            postmark = PostmarkClient(server_token='POSTMARK-SERVER-API-TOKEN-HERE')

# Send an email
postmark.emails.send(
  From='sender@example.com',
  To='recipient@example.com',
  Subject='Postmark test',
  HtmlBody='HTML body goes here'
)
            Send message here with the code
            '''
            now = dt.now()
            r_now =  now.strftime("Date  %Y:%m:%d: Time %H:%M:%S")
            session['rset'] = email
            if not reset_db.find_one({"email" : email}):
                reset_db.insert_one({"email" : email , "code" : code , "time_in" : r_now})
            return redirect(url_for('enter_code'))      
        else:
            return redirect(url_for('register'))
    return render_template('reset_pass.html')



@application.route('/enter_code/' , methods = ['POST','GET'])
def enter_code():
    email = session['rset']
    if "x" =="x":
        if request.method == "POST":
            reset_db = mongo.db.pass_reset
            code = request.form['code']
            legit = reset_db.find_one({"email" : email})
            if legit:
                legit_code = legit["code"]
                now = dt.now()
                now = now.strftime("Date  %Y:%m:%d: Time %H:%M:%S")
                req_time = legit['time_in']
                def timez():
                    now = dt.now()
                    now3 = now.strftime("Date  %Y:%m:%d: Time %H:%M:%S")
                    cr = str(now3)[23:28]
                    first_min = cr[3:5]
                    first_hour = cr[0:2]

                    cr2 = str(req_time)[23:28]
                    second_min = cr2[3:5]
                    second_hour = cr2[0:2]

                    dif = int(second_min) - int(first_min)
                    hours = int(first_hour) - int(second_hour)
                    if dif < 0:
                        dif = dif + 60
                    return dif
                    
                diff =timez()
                if code == legit_code:
                    reset_db.find_one_and_delete({'email' : email})
                    return redirect(url_for('update_password'))  
                else:
                    return redirect(url_for('reset_pass' ))
    return render_template('enter_code.html')
     
      

@application.route('/update_password/' , methods = ['POST','GET'])
def update_password():
    email = session['rset']
    if request.method == "POST":
        users = mongo.db.users
        target_account = session['rset'] 
        pass1 = request.form['pas1']
        pass2 = request.form['pas2']
        if pass1 == pass2:
            passcode = Hash_passcode.hash(pass2)
            the_user = users.find_one({"email" : email})
            users.find_one_and_update({"email" :target_account} , { '$set' : {"password" : passcode} })
            session['login_user'] = target_account
            return redirect(url_for('home'))
        else:
            check_pass = " Please Check The Password And Try Again"
            return render_template('new_pass.html', mess = check_pass)
            
    return render_template('new_pass.html')


                  
@application.route('/login/' , methods = ['POST','GET'])
def login():
    if request.method == "POST":# and  hcaptcha.verify():
        email = request.form['email']
        existing_user  = users.find_one({'email':email} )
        if existing_user:
                passcode = request.form['passcode']
                v = str(existing_user['verified'])

                existing_pass = existing_user['password']
                if Hash_passcode.verify(passcode,existing_pass):
                    username = existing_user['username']
                    if username in session:
                        fa = existing_user['tags']
                        if v == 0 :
                            return redirect(url_for('complete_regist'))
                        if len(fa) < 5 and v ==1 :
                             return redirect(url_for('choose_tags'))
                        if len(fa) > 5 and v == 0 :
                             return redirect(url_for('complete_regist'))
                        else:
                            return redirect(url_for('feed'))
                    else:    
                        session.parmanent = True
                        session['login_user'] = email
                        fa = existing_user['tags']
                        if len(fa) < 5:
                            return redirect(url_for('choose_tags'))
                        else:    
                            return redirect(url_for('feed'))
    return render_template('login.html')



@application.route('/register/',methods = ['POST','GET'])
def register():
    if request.method == "POST":
        email = request.form['email']
        passc = request.form['passc']
        passc2 = request.form['passc2']
        hashed = Hash_passcode.hash(passc2)
          
        registered = users.find_one({"email":email})
        if registered:
            mess = "You are already registered,please Log in"
            return redirect(url_for('login'))
        if passc == passc2  and not registered:
            mess = "Registerd Successfully" 
            users.insert_one({"email":email , "password":hashed , "verified" :0})
            if users.find_one({"email":email}):
                code = random.randint(145346 , 976578)
                code = str(code)
                session['login_user'] = email
                if not verif.find_one({"email" : email}):
                    verif.insert_one({"email" : email , "code" : code })
                    #send the code Here
                    return redirect(url_for('complete_regist'))
                        
    return render_template('register.html')

@application.route('/complete_regist' , methods = ['POST' , 'GET'])
def complete_regist():
    verif = mongo.db.verify_email
    user_email = session['login_user']
    in_db = verif.find_one({"email" : user_email})
    if request.method == "POST":
        de_code = request.form['code']
        if in_db:
            code = str(in_db['code'])
            if code == de_code:
                users.find_one_and_update({"email" : user_email} ,{ '$set' :  {"verified": 1}} )
                verif.find_one_and_delete({'email' : user_email})
                return redirect(url_for('home'))
            else:
                print("Wrong Code")
                time.sleep(2)
                return redirect(url_for('complete_regist'))
        else:
            return redirect(url_for('register'))
            
    return render_template('verif_reg.html' , m = user_email)
    


if __name__ == "__main__":
    application.secret_key = "Fucddggdgdfdgdrer5677u"
    application.run(debug = True , port = 5004)

    
