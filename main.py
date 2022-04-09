
#import logging
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from MySQLdb import DatabaseError
import re
import Utillity as ut
import pandas as pd
app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'


#logging application consol
#logger = logging.getLogger('werkzeug') # grabs underlying WSGI logger
#handler = logging.FileHandler('app.log') # creates handler for the log file
#logger.addHandler(handler) # adds handler to the werkzeug WSGI logger

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'python_project'

# Intialize MySQL
mysql = MySQL(app)

#landing page
@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
            # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            return redirect(url_for('home'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/claim', methods=['GET', 'POST'])
def claim():
    # Output message if something goes wrong...
    msg = ''
    n=0
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form:
        # Create variables for easy access
        name = request.form['name']
        car_modal = request.form['car_modal']
        email = request.form['email']
        status="In Progress"
        img1= ut.upload_file(request.files['img1'])
        img2= ut.upload_file(request.files['img2'])
        img3= ut.upload_file(request.files['img3'])
        
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Account doesnt exists and the form data is valid, now insert new account into accounts table
        cursor.execute('INSERT INTO claim VALUES (NULL,%s,%s, %s, %s,%s,%s,%s,%s)', (session['username'],name,car_modal, email,img1,img2,img3,status))
        mysql.connection.commit()
        return redirect(url_for('claim'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('Select * from claim where username=%s',(session['username'],))
        claim_data = cursor.fetchall()
        if claim_data:
            claim_data=pd.DataFrame(list(claim_data))
            #print(claim_data)
            n=int(len(claim_data))
            return render_template('claim.html',claim_data=claim_data,n=n)
        else:
            msg="No Claim Request Aviliable"
        
    # Show registration form with message (if any)
    return render_template('claim.html', msg=msg,n=n)

@app.route('/Get_Report', methods=['GET', 'POST'])
def Get_Report():
    Claim_Report="Analysis is in Progress"
    claim_number = request.form['claim_id']
    return render_template('Get_Report.html', Claim_Report=Claim_Report,claim_number=claim_number)

@app.errorhandler(404)
def page_not_found(error):
    error_msg='Error 404: This page does not exist !!'
    #logger.exception(error_msg)
    return render_template('error.html',error_msg=error_msg)

@app.errorhandler(DatabaseError)
def special_exception_handler(error):
    error_msg='Error 500: Database connection failed !!'
    #logger.exception(error_msg)
    return render_template('error.html',error_msg=error_msg)

@app.errorhandler(Exception)          
def Error(e):
    error_msg="An Error occured: " + str(e)
    #logger.exception(error_msg)
    return render_template('error.html',error_msg=error_msg)

if __name__ == "__main__":
    app.run()