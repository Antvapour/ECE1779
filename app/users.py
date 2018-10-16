from flask import render_template, session, redirect, url_for, request, g, send_from_directory
from app import webapp

import mysql.connector

from app.config import db_config

import os

from wand.image import Image

webapp.secret_key = '\x80\xa9s*\x12\xc7x\xa9d\x1f(\x03\xbeHJ:\x9f\xf0!\xb1a\xaa\x0f\xee'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@webapp.route('/signup', methods=['GET'])
# Display an HTML form that allows users to sign up.
def signup():
    return render_template("users/signup.html",title="New User")


@webapp.route('/signup', methods=['POST'])
# Create a new account and save it in the database.
def signup_save():
    username = request.form.get('username',"")
    password1 = request.form.get('password1',"")
    password2 = request.form.get('password2',"")

    error = False

    if username == "" or password1== "" or password2== "" :
        error=True
        error_msg="Error: All fields are required!"

    elif password1 != password2 :
        error=True
        error_msg="Error: The re-typed password does not match your first entry!"

    else :
        cnx = get_db()
        cursor = cnx.cursor()

        query = '''SELECT * FROM users
                          WHERE username = %s'''
        cursor.execute(query,(username,))
        row = cursor.fetchone()

        if row is not None :
            error=True
            error_msg="Error: User name already exists!"

    if error:
        return render_template("users/signup.html",title="New User",error_msg=error_msg, username=username)

    cnx = get_db()
    cursor = cnx.cursor()

    query = ''' INSERT INTO users (username,password)
                       VALUES (%s, %s)'''

    cursor.execute(query,(username,password1))
    cnx.commit()

    session['authenticated'] = True

    query = '''SELECT id FROM users
                      WHERE username = %s'''
    cursor.execute(query,(username,))
    row = cursor.fetchone()
    session['username'] = row[0]

    path = os.path.join(APP_ROOT, 'images', str(row[0]))
    os.makedirs(path)

    return redirect(url_for('user_home'))

@webapp.route('/login',methods=['GET'])
# Display an HTML form that allows users to log in.
def login():
    return render_template("users/login.html",title="Log in")

@webapp.route('/login_submit',methods=['POST'])
###################################################
def login_submit():
    username = request.form.get('username',"")
    password = request.form.get('password',"")

    error = False

    if username == "" or password== "" :
        error=True
        error_msg="Error: All fields are required!"

    else :
        cnx = get_db()
        cursor = cnx.cursor()

        query = '''SELECT * FROM users
                          WHERE username = %s'''
        cursor.execute(query,(username,))
        row = cursor.fetchone()

        if row is None :
            error=True
            error_msg="Error: User Does not exist!"

        elif row[2] != password :
            error=True
            error_msg="Error: password does not match!"

    if error :
        return render_template("users/login.html",title="Log in",error_msg=error_msg, username=username)

    session['authenticated'] = True
    session['username'] = row[0]

    return redirect(url_for('user_home'))


@webapp.route('/home', methods=['GET','POST'])
###################################################
def user_home():
    if 'authenticated' not in session:
        return redirect(url_for('login'))

    users_id = session.get('username')

    cnx = get_db()
    cursor = cnx.cursor()

    query = '''SELECT users_id, filename FROM images
                    WHERE users_id = %s'''
    cursor.execute(query,(users_id,))

    return render_template("images/home.html",title="User Home", cursor=cursor)


@webapp.route('/show/<filename>', methods=['GET','POST'])
# display thumbnails of a specific account
def send_image(filename):
    users_id = session.get('username')
    path_basic = os.path.join(APP_ROOT, 'images', str(users_id), filename)


# create thumbnails of all images

    filename_thumb = filename + '_thumbnail.png'
    path_thumb_full = os.path.join(APP_ROOT, 'images', str(users_id), filename_thumb)
    path = os.path.join(str(users_id), filename_thumb)

    with Image(filename=path_basic) as img:

        with img.clone() as image:
            size = image.width if image.width < image.height else image.height
            image.crop(width=size, height=size, gravity='center')
            image.resize(128, 128)
            image.format = "png"
            image.save(filename=path_thumb_full)

            return send_from_directory("images", path)


@webapp.route('/logout',methods=['GET','POST'])
# Clear the session when users want to log out.
def logout():
    session.clear()
    return redirect(url_for('main'))