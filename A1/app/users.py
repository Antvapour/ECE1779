from flask import render_template, redirect, url_for, request, g
from app import webapp





@webapp.route('/signup',methods=['GET'])
# Display an empty HTML form that allows users to define new student.
def signup():
    return render_template("users/signup.html",title="New User")

@webapp.route('/signup',methods=['POST'])
# Create a new student and save them in the database.
def courses_create_save():
    username = request.form.get('username',"")
    password1 = request.form.get('password1',"")
    password2 = request.form.get('password2',"")

    error = False

    if username == "" or password1== "" or password2== "" :
        error=True
        error_msg="Error: All fields are required!"

    else if password1 != password2 :
        error=True
        error_msg="Error: The re-typed password does not match your first attempt!"


    if error:
        return render_template("users/signup.html",title="New User",error_msg=error_msg, username=username)

    return redirect(url_for('user_main'))
