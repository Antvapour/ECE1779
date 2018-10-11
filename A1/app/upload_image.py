import os
from flask import request, render_template, send_from_directory
from app import webapp


APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@webapp.route("/upload")
def index():
    return render_template("photos/upload.html")


@webapp.route("/show", methods=["POST"])
def upload():

    target = os.path.join(APP_ROOT, 'images/')
  #  print(target)
  # print(APP_ROOT)


    for upload in request.files.getlist("file"):

        filename = upload.filename
        print(filename)
        destination = "".join([target, filename])
        upload.save(destination)

    return render_template("/photos/complete.html",image_name=filename, file_address=destination)


@webapp.route('/show/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

@webapp.route('/gallery')
def getgallery():
    image_names = os.listdir('./app/images')
    print(image_names)
    return render_template("/photos/gallery.html", image_names=image_names)


