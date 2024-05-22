from flask import session, render_template, request, redirect, url_for, flash, Blueprint
from helpers import authorize, myDb, login_required

users = Blueprint('users', __name__, template_folder='templates')

def validate_user(user):
    if user['firstName'] == "" or user['lastName'] == "" or user['userType'] == "" or user['universityId'] == "" or user['stAddr'] == "" or user['city'] == "" or user['state'] == "" or user['zipCode'] == "" or user['email'] == "" or (user['userType'] == "student" and user['advisorId'] == ""):
        # If any of the required fields are empty, return False
        return False
    if user['userType'] not in userTypes:
        # If the user type is not valid, return False
        return False
    if len(user['firstName']) > 50 or len(user['lastName']) > 50:
        # If the first or last name is too long, return False
        return False
    if len(user['universityId']) != 8 or not user['universityId'].isnumeric():
        # If the university ID is not 8 digits, return False
        return False

    if len(user['stAddr']) > 50 or len(user['city']) > 50:
        #If the street address or city is too long 
        return False
    
    if len(user['state']) != 2:
        #If the state is too short or too long
        return False
    
    if len(user['zipCode']) != 5 or not user['zipCode'].isnumeric():
        return False 

    if user['userType'] == "student":
        # If the user is a student, ensure the advisor exists
        cursor = myDb.cursor(dictionary=True)
        cursor.execute("SELECT `id` FROM `user` WHERE `id` = %s AND `type` = 'faculty'", (user['advisorId'],))
        if cursor.fetchone() is None:
            return False

    return True

userTypes = {
    "alum": "Alumni",
    "faculty": "Faculty",
    "gs": "Grad Secretary",
    "student": "Graduate Student",
    "sysadmin": "Systems Administrator",
    "applicant": "Applicant"
}

@users.route("/")
@login_required
def index():
    factype_str = request.args.get('factype')
    factype = eval(factype_str) if factype_str else None
    global userTypes
    cursor = myDb.cursor(dictionary=True)

    userId = session['userId']

    cursor.execute("SELECT `id`, `first_name`, `last_name`, `type` FROM `user` WHERE id=%s", (userId,))
    user = cursor.fetchone()
    return render_template("user_home.html", user=user, factype=factype)


#chnage this route name and
@users.route("/view")
@authorize(["sysadmin"])
@login_required
def view_users():
    global userTypes
    cursor = myDb.cursor(dictionary=True)

    cursor.execute("SELECT `id`, `first_name`, `last_name`, `type` FROM `user`")
    users = cursor.fetchall()
    myDb.commit()

    return render_template("user_index.html", users=users, userTypes=userTypes)

@users.route("/<int:userId>/edit", methods=["GET", "POST"])
@authorize(["sysadmin"])
@login_required
def edit(userId):
    global userTypes
    cursor = myDb.cursor(dictionary=True)

    # Ensure the user exists

    cursor.execute("SELECT `id`, `first_name`, `last_name`, `type` FROM `user` WHERE `id` = %s", (userId,))

    user = cursor.fetchone()
    if user is None:
        flash("The requested user does not exist.")
        return redirect(url_for('.index'))

    if request.method == "POST":
        # Get the form data
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        userType = request.form["userType"]
        advisorId = request.form["advisorId"] if "advisorId" in request.form else ""
        stAddr = request.form["stAddr"]
        city = request.form["city"]
        state = request.form["state"]
        zipCode = request.form["zipCode"]
        email = request.form["email"]

        # Validate the form data
        validated = validate_user(request.form)

        if validated:
            # Update the user in the database
            cursor.execute("UPDATE `user` SET `first_name` = %s, `last_name` = %s, `type` = %s, `street_address` = %s, `city` = %s, `state` = %s, `zip` = %s, `email` = %s WHERE `id` = %s", (firstName, lastName, userType, stAddr, city, state, zipCode, email, userId))
            if userType == "student":
                # If the user is a student, update their student info
                cursor.execute("UPDATE `student_info` SET `advisor_id` = %s WHERE `user_id` = %s", (advisorId, userId))
                if cursor.rowcount == 0:
                    # If the student info was not updated, insert it
                    cursor.execute("INSERT INTO `student_info` (`user_id`, `advisor_id`) VALUES (%s, %s)", (userId, advisorId))
            else:
                # If the user is not a student, delete their student info
                cursor.execute("DELETE FROM `student_info` WHERE `user_id` = %s", (userId,))
                cursor.execute("DELETE FROM `student_courses` WHERE `user_id` = %s", (userId,))
                cursor.execute("DELETE FROM `student_courses_planned` WHERE `user_id` = %s", (userId,))

            myDb.commit()
            # Redirect to the user index page
            return redirect(url_for('.index'))
    
    # If the user is a student, get their student info
    if user['type'] == "student":
        cursor.execute("SELECT `advisor_id` FROM `student_info` WHERE `user_id` = %s", (userId,))
        studentInfo = cursor.fetchone()
        user['advisor_id'] = studentInfo['advisor_id']

    # Get the list of faculty advisors
    cursor.execute("SELECT `id`, `first_name`, `last_name` FROM `user` WHERE `type` = 'faculty' AND `id` != %s ORDER BY `first_name`, `last_name`", (userId,))
    advisors = cursor.fetchall()

    

    return render_template("user_edit.html", userTypes=userTypes, user=user, advisors=advisors)

@users.route("/add", methods=["GET", "POST"])
@authorize(["sysadmin"])
@login_required
def add():
    global userTypes
    cursor = myDb.cursor(dictionary=True)

    if request.method == "POST":
        # Get the form data
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        userType = request.form["userType"]
        universityId = request.form["universityId"]
        advisorId = request.form["advisorId"] if "advisorId" in request.form else ""
        stAddr = request.form["stAddr"]
        city = request.form["city"]
        state = request.form["state"]
        zipCode = request.form["zipCode"]
        email = request.form["email"]
        # Validate the form data
        validated = validate_user(request.form)

        if validated:
            # Insert the user into the database
            cursor.execute("INSERT INTO `user` (`first_name`, `last_name`, `type`, `id`, `street_address`, `city`, `state`, `zip`, `email`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (firstName, lastName, userType, universityId, stAddr, city, state, zipCode, email))
            if userType == "student":
                userId = cursor.lastrowid
                cursor.execute("INSERT INTO `student_info` (`user_id`, `advisor_id`) VALUES (%s, %s)", (userId, advisorId))
            myDb.commit()
            # Redirect to the user index page
            return redirect(url_for('.index'))

    # Get the list of faculty advisors
    cursor.execute("SELECT `id`, `first_name`, `last_name` FROM `user` WHERE `type` = 'faculty' ORDER BY `first_name`, `last_name`")
    advisors = cursor.fetchall()

    return render_template("user_add.html", userTypes=userTypes, advisors=advisors)

@users.route("/<int:userId>/remove")
@authorize(["sysadmin"])
@login_required
def remove(userId):
    cursor = myDb.cursor(dictionary=True)

    # Ensure the user exists
    cursor.execute("SELECT `id`, `type` FROM `user` WHERE `id` = %s", (userId,))
    user = cursor.fetchone()
    if user is None:
        flash("The requested user does not exist.")
        return redirect(url_for('.index'))

    # Remove the user from the database
    cursor.execute("DELETE FROM `user` WHERE `id` = %s", (userId,))
    if user['type'] == "student":
        cursor.execute("DELETE FROM `student_info` WHERE `user_id` = %s", (userId,))
    myDb.commit()
    flash("User successfully removed.")
    return redirect(url_for('.index'))
