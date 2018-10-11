@webapp.route('/home/upload', methods=['GET'])
# Display an empty HTML form that allows users to define new student.
def upload_create('/home/upload'):
    return render_template("photos/upload.html", title="New Student")

@webapp.route('/home/upload', methods=['POST'])
# upload a new  image and save it in the database.

def images_create_save():
   id =
   %% name = request.form.get('name', "")
   %%location_add = request.form.get('email', "")

    error = False

    if name == "" or location_add == "" o
        error = True
        error_msg = "Error: All fields are required!"

    if not error and not re.match('\d{4}-\d{2}-\d{2}', dob):
        error = True
        error_msg = "Error: Date of birth most be in format YYYY-MM-DD!"

    if error:
        return render_template("students/new.html", title="New Student", error_msg=error_msg,
                               name=name, email=email, dob=dob, program=program)

    cnx = get_db()
    cursor = cnx.cursor()

    query = ''' INSERT INTO students (name,email,date_of_birth,program_of_study)
                       VALUES (%s,%s,date %s,%s)
    '''

    cursor.execute(query, (name, email, dob, program))
    cnx.commit()

    return redirect(url_for('students_list'))


