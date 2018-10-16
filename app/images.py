from flask import render_template, session, redirect, url_for, request, g,send_from_directory
from app import webapp

import mysql.connector

from app.config import db_config

import os

from wand.image import Image


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
        path = os.path.join(APP_ROOT, 'images/', str(users_id), filename)
        print(path)
        upload.save(path)
        query = ''' INSERT INTO images (users_id,filename)
                           VALUES (%s,%s)'''
        cursor.execute(query, (users_id,filename))
        cnx.commit()

        path_basic = os.path.join(APP_ROOT, 'images', str(users_id), filename)

        # create rotated transformations and save
        filename_rotated = filename + '_rotated.png'
        path_rotated_full = os.path.join(APP_ROOT, 'images', str(users_id), filename_rotated)

        with Image(filename=path_basic) as img:
            with img.clone() as rotated:
                rotated.rotate(135)
                rotated.format = "png"
                rotated.save(filename=path_rotated_full)

        # create flopped transformations and save
        filename_flopped = filename + '_flopped.png'
        path_flopped_full = os.path.join(APP_ROOT, 'images', str(users_id), filename_flopped)

        with Image(filename=path_basic) as img:
            with img.clone() as flopped:
                flopped.flop()
                flopped.format = "png"
                flopped.save(filename=path_flopped_full)

        # created gray-scale transformations and save

        filename_gray = filename + '_gray.png'
        path_gray_full = os.path.join(APP_ROOT, 'images', str(users_id), filename_gray)

        with Image(filename=path_basic) as img:
            with img.clone() as gray:
                gray.type = 'grayscale'
                gray.format = "png"
                gray.save(filename=path_gray_full)

        return redirect(url_for('user_home'))


@webapp.route('/images/trans/<filename>', methods=['GET'])
# show the transformations of a specific image.
def images_trans(filename):
    filename1 = filename
    return render_template("images/trans.html",title="Transformations Home", filename=filename1)


@webapp.route('/trans/<filename>', methods=['GET','POST'])
# display thumbnails of a specific account
def send_image_trans(filename):
    users_id = session.get('username')
    filename = os.path.join(str(users_id), filename)
    return send_from_directory("images", filename)


