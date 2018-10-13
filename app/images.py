
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

    query = '''SELECT i.id, i.stored_location
               FROM users u, photos i 
               WHERE u.id = i.users_id'''

    cursor.execute(query)

    return redirect(url_for('photos/home', cursor=cursor))



@webapp.route('/images/<int:id>', methods=['GET'])
# Display transformations of a specific image.
def images_view(ima_loc):

          with Image (filename= ima_loc ) as img:
               with img.clone() as image:
                    size = image.width if image.width < image.height else image.height
                    image.crop(width=size, height=size, gravity='center')
                    image.resize(256, 256)
                    image.format = 'jpeg'

          return render_template("photos/transformations.html", title="Transformations Home")


#@webapp.route('/images/<int:id>', methods=['GET'])
# Display transformations of a specific image.
#def images_transformations(id):




@webapp.route('/images/upload', methods=['GET'])
# Display an empty HTML form that allows users to define new student.
def images_upload():

    return render_template("photos/new.html", title="New Images", id=session.get('username'))


@webapp.route('/images/upload', methods=['POST'])
# upload a new image and save it in the database.
def images_upload_save():

    users_id = session.get('username')
    target = os.path.join(APP_ROOT, 'images/')


    for upload in request.files.getlist("file"):
        filename = upload.filename
        print(filename)
        stored_location = "".join([target, filename])
        upload.save(stored_location)

    cnx = get_db()
    cursor = cnx.cursor()

    query = ''' INSERT INTO photos (users_id,stored_location)
                       VALUES (%s,%s)'''

    cursor.execute(query, (users_id, stored_location))

    cnx.commit()

    return redirect(url_for('images_list'))


@webapp.route('/images/delete/<int:id>', methods=['POST'])
# Deletes the specified student from the database.
def sections_delete(id):
    cnx = get_db()
    cursor = cnx.cursor()

    query = "DELETE FROM photos WHERE id = %s"

    cursor.execute(query, (id,))
    cnx.commit()

    return redirect(url_for('images_list'))

