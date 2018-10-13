
from flask import render_template, redirect, url_for, request, g, session, send_from_directory
from app import webapp
import os
import mysql.connector

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

from app.config import db_config


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

################
@webapp.route('/images', methods=['GET'])
# Display an HTML list of all sections.
def images_list():
    cnx = get_db()

    cursor = cnx.cursor()

    query = '''SELECT i.id,i.imagename, i.stored_location, i.trans1, i.trans2, i.trans3
               FROM users u, photos i 
               WHERE u.id = i.users_id'''

    cursor.execute(query)

    return render_template("photos/list.html", title="Images List", cursor=cursor)

#######

@webapp.route('/images/<int:id>', methods=['GET'])
# Display transformations of a specific image.
def images_view(id):
    cnx = get_db()

    cursor = cnx.cursor()

    query = '''SELECT trans1, trans2, trans3 FROM images
                            WHERE id = %s'''

    cursor.execute(query, (id,))

    row = cursor.fetchone()

    trans1 = row[0]
    trans2 = row[1]
    trans3 = row[2]

    return render_template("images/view.html", title="Section Details",
                           trans1=trans1,tran2=trans2,trans3=trans3)


@webapp.route('/images/upload', methods=['GET'])
# Display an empty HTML form that allows users to define new student.
def images_upload():

    return render_template("photos/new.html", title="New Images", id=session.get('username'))


@webapp.route('/images/upload', methods=['POST'])
# upload a new image and save it in the database.
def images_upload_save():

    users_id = session.get('username')
    imagename = request.form.get('imagename', "")

    target = os.path.join(APP_ROOT, 'images/')
    #target1 = os.path.join(APP_ROOT, 'trans1/')
    #target2 = os.path.join(APP_ROOT, 'trans2/')
    #target3 = os.path.join(APP_ROOT, 'trans3/')

    for upload in request.files.getlist("file"):
        filename = upload.filename
        print(filename)
        stored_location = "".join([target, filename])
        upload.save(stored_location)

    trans1 = request.form.get('trans1', "")
    trans2 = request.form.get('trans2', "")
    trans3 = request.form.get('trans3', "")


    cnx = get_db()
    cursor = cnx.cursor()

    query = ''' INSERT INTO photos (users_id,imagename,stored_location,trans1,trans2,trans3)
                       VALUES (%s,%s)'''

    cursor.execute(query, (users_id,imagename, stored_location,trans1,trans2,trans3))

    cnx.commit()

    return redirect(url_for('images_list'))


@webapp.route('/show/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)


@webapp.route('/images/delete/<int:id>', methods=['POST'])
# Deletes the specified student from the database.
def sections_delete(id):
    cnx = get_db()
    cursor = cnx.cursor()

    query = "DELETE FROM photos WHERE id = %s"

    cursor.execute(query, (id,))
    cnx.commit()

    return redirect(url_for('images_list'))

