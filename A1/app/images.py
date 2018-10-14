from flask import render_template, session, redirect, url_for, request, g
from app import webapp

import mysql.connector

from app.config import db_config

import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

webapp.secret_key = '\x80\xa9s*\x12\xc7x\xa9d\x1f(\x03\xbeHJ:\x9f\xf0!\xb1a\xaa\x0f\xee'

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

@webapp.route('/images/upload', methods=['POST'])
# upload a new image and save it in the database.
def images_upload():
    if 'authenticated' not in session:
        return redirect(url_for('login'))

    users_id = session.get('username')

    cnx = get_db()
    cursor = cnx.cursor()

    for upload in request.files.getlist("file"):
        filename = upload.filename
        path = os.path.join(APP_ROOT, 'images', str(users_id), filename)
        upload.save(path)
        query = ''' INSERT INTO images (users_id,filename)
                           VALUES (%s,%s)'''
        cursor.execute(query, (users_id,filename))

    cnx.commit()

    return redirect(url_for('user_home'))
