from flask import session, render_template, request, redirect, url_for, Flask, flash
from helpers import myDb, login_required, authorize
from users import users
from students import students, programTypes
from transcripts import transcript, studentSuspended, calculateGpa
from chatroom import chatroom, view, send_message
from registration import registration
from applications import applications


app = Flask(__name__) 
app.secret_key = "secret_item"
app.config['SESSION_PERMANENT'] = False
app.register_blueprint(users, url_prefix='/users')
app.register_blueprint(students, url_prefix='/students')
app.register_blueprint(transcript, url_prefix='/transcript')
app.register_blueprint(chatroom, url_prefix='/chatroom')

app.register_blueprint(registration, url_prefix='/registration')
app.register_blueprint(applications, url_prefix='/applications')


@app.route("/")
@login_required
def home():
    cursor = myDb.cursor(dictionary=True)
    # session.clear()
    userId = session['userId']
   
    #Get the requested user. 
    cursor.execute("SELECT `first_name`, `last_name`, `type`, `id` FROM user WHERE id = %s", (userId,))
    user = cursor.fetchone()

    cursor.execute("SELECT is_reviewer, is_admissions_chair FROM faculty_info WHERE faculty_info.user_id=%s", (userId,))
    factype = cursor.fetchone()
    #Show the student home view if user if of type student 
    if user is not None and user["type"] in ["student"]:
        cursor.execute("SELECT COUNT(`course_id`), `user_id` FROM `student_courses_planned` WHERE `user_id` = %s", (userId,))
        form1 = cursor.fetchone()['COUNT(`course_id`)'] > 0
        return render_template("studenthome.html", student=user, form1 = form1)

    #Show the alum home view if user is of type alum 
    if user is not None and user["type"] in ["alum"]:
        cursor.execute("SELECT `program`, `grad_year`, `user_id` FROM `alumni_info` WHERE `user_id` = %s", (userId,))
        alum_info = cursor.fetchone()
        return render_template("alumhome.html", alum=user, alum_info=alum_info, programTypes=programTypes)
    
    if user is not None and user["type"] in ["applicant"]:
        return redirect(url_for('applications.applicant'))
    #Show the user view if user is of type sysadmin, gs or faculty 
    if user is not None and user["type"] in ["sysadmin"] or ["faculty"] or ['gs'] :
        return redirect(url_for('users.index', factype=factype))

@app.route("/index")
def index():
    if 'userId' not in session:
        return render_template("index.html")
    return redirect(url_for('home'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':    
        cursor = myDb.cursor(dictionary=True)
        cursor.execute("SELECT `id`, `type`, `username`, `password` FROM user WHERE username=%s and password=%s", (request.form['username'],request.form['password']))

        user = cursor.fetchone()
        if user == None:
            flash("User/password is incorrect. Please try again.", "warning")
            return render_template('login.html')

        session['userId'] = user['id']
        session['userType'] = user['type']
        session['username'] = user['username']

        if 'next' in session:
            return redirect(session.pop('next', None))
        
        return redirect(url_for("home"))

    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/home/personal_info", methods=['POST', 'GET'])
@login_required
def personal_info():
    # Create a cursor to execute queries
    cursor = myDb.cursor(dictionary=True)
    
    # If userId is not specified, use the currently logged in user's id
    userId = session['userId']

    #Fetch the user 
    cursor.execute("SELECT `first_name`, `type`, `last_name`, `id`, `email`, `street_address`, `city`, `state`, `zip`, `id` FROM user WHERE id = %s", (userId,))
    user = cursor.fetchone()

    currentEmail = user["email"]

    #Setting student and advisor to none, so if the user is not a student, we don't get an error. 
    student = None
    advisor = None
    
    if user["type"] in ['student']:
        cursor.execute("SELECT `program`, `advisor_id` FROM student_info WHERE user_id = %s", (userId,))
        student = cursor.fetchone()
        advisor_id = student["advisor_id"]
        cursor.execute("SELECT `first_name`, `last_name` FROM user WHERE id = %s", (advisor_id,))
        advisor = cursor.fetchone()
    
    #If the user wants to update their email, first check if they will change it to 
    # a new email or if the email is already in the database.: 
    if request.method == 'POST':
        if "email" in request.form:
            x = request.form["email"]
            if x != currentEmail:
                cursor.execute("SELECT `email` FROM user WHERE email = %s", (x,))
                if cursor.fetchone() is None:
                    cursor.execute("UPDATE user SET email = %s WHERE id = %s", (x, userId))
                    myDb.commit()
                    flash("Email successfully updated!", "success")
                    return redirect(url_for('personal_info'))
                else:
                    flash("Email already in use!", "danger")
                    return redirect(url_for('personal_info'))
            else:
                flash("Please enter a new email address.", "danger")
                return redirect(url_for('personal_info'))
        else:
        #Request the address information
            street = request.form["streetaddr"]
            city = request.form["city"]
            state = request.form["state"]
            zipCode = request.form["zip"]
        
        #Update the address information in the DB 
            cursor.execute("UPDATE user SET `street_address` = %s, `city`=%s, `state`=%s, `zip`=%s WHERE `id` = %s", (street, city, state, zipCode, userId))
            myDb.commit()
        
        #Inform the user that the information has been updated  
            flash("Address successfully updated!", "success")
            return redirect(url_for('personal_info'))


    return render_template("personal_info.html", user=user, student=student, advisor=advisor, programTypes=programTypes)

@app.route("/view_form1")
@login_required
@authorize(["student"])
def view_form1():

    cursor = myDb.cursor(dictionary=True)
    cursor.execute("SELECT `form_approved` FROM student_info WHERE user_id = %s", (session["userId"],))
    form1 = cursor.fetchone()
    if form1["form_approved"] == 1:
        return redirect(url_for('students.form_review', studentId=session["userId"]))

    cursor.execute("SELECT `id`, `department`, `cnumber`, `title` FROM course")
    courses = cursor.fetchall()
    
    cursor.execute("SELECT `course_id` FROM `student_courses_planned` WHERE `user_id` = %s", (session["userId"],))
    form1 = cursor.fetchall()

    return render_template("form1.html", courses=courses, form1=form1)


@app.route("/validate_form1", methods=['POST'])
@login_required
@authorize(["student"])
def validate_form1():

    userId = session['userId'] 
    cursor = myDb.cursor(dictionary=True, buffered=True)
    cursor.execute("DELETE FROM `student_courses_planned` WHERE user_id=%s", (userId,)) # remove all courses from the table
    ##need to loop through all of the class
    cursor.execute("SELECT `course_id` FROM `student_courses_planned` WHERE user_id=%s", (userId,))
    cursor.fetchall()

    #checking that the student has already submitted the form1 before
    if cursor.rowcount != 0:
        flash("You have alrady submitted your Form1. You cannot make another submisssion at this time.", "danger")
        return redirect(url_for('home'))

    #for loop to go through each of the courses
    for i in range(1,13):
        if 'class'+str(i) not in request.form:
            continue
        cursor.execute("SELECT `id` FROM course WHERE id=%s", (request.form["class"+str(i)],))
        curClass = cursor.fetchone()['id']
        #going to use this variable to check if its already in the students table
        cursor.execute("SELECT `user_id`, `course_id` FROM student_courses_planned WHERE user_id=%s AND course_id=%s", (userId, curClass))
        studentsClass = cursor.fetchone()
        if studentsClass == None:
            cursor.execute("INSERT INTO `student_courses_planned` (`course_id`, `user_id`) VALUES (%s, %s)", (curClass, userId))
        else:
            #going to clear the table and flash an error that says they put duplicate classes
            cursor.execute("DELETE FROM `student_courses_planned` WHERE user_id=%s", (userId,))
            myDb.commit()
            flash("You entered the same class more than once. Please try again.", "danger")
            return redirect(url_for('view_form1'))
        
    #need to select all classes from student courses planned loop through those
    cursor.execute("SELECT `course_id` FROM `student_courses_planned` WHERE user_id=%s",(userId,))
    studentsPlannedCourses = cursor.fetchall()
    for planned in studentsPlannedCourses:
        cursor.execute("SELECT `prereq_id` FROM `course_prereq` where course_id=%s", (planned['course_id'],))
        preReqs = cursor.fetchall()
        #if there is no prereq for the current course continue to the next class
        if len(preReqs) == 0:
            continue
        else:
            for preReq in preReqs:
                #if there is a prereq, select from the courses planned and check if the prereq is in the students form
                cursor.execute("SELECT `course_id` FROM `student_courses_planned` WHERE course_id=%s",(preReq['prereq_id'],))
                plannedPreReq = cursor.fetchall()
                if len(plannedPreReq) == 0:
                    cursor.execute("DELETE FROM `student_courses_planned` WHERE user_id=%s", (userId,))
                    myDb.commit()
                    flash("You have not chosen a required prerequisite for one of your class selections. Please try again.", "danger")
                    return redirect(url_for('view_form1'))
                else: 
                    continue

    #checking that the student is taking the 3 required classed for masters
    cursor.execute("SELECT `id` FROM `course` WHERE required_masters=1")
    masterCourses = cursor.fetchall()
    for master in masterCourses:
        cursor.execute("SELECT `course_id` FROM `student_courses_planned` WHERE course_id=%s", (master['id'],))
        classes = cursor.fetchall()
        if cursor.rowcount == 0:
            cursor.execute("DELETE FROM `student_courses_planned` WHERE user_id=%s", (userId,))
            myDb.commit()
            flash("You are missing one of your required classes for your degree. Please try again.", "danger")
            return redirect(url_for('view_form1'))
        else:
            continue

    cursor.execute("SELECT COUNT(department) FROM student_courses_planned INNER JOIN course ON student_courses_planned.course_id = course.id WHERE department!= 'CSCI' AND user_id=%s",(userId,))
    nonCs = cursor.fetchone()
    if int(nonCs["COUNT(department)"]) > 2:
        cursor.execute("DELETE FROM `student_courses_planned` WHERE user_id=%s", (userId,))
        myDb.commit()
        flash("You have too many non-computer science courses planned. Please try again.", "danger")
        return redirect(url_for('view_form1'))
    
    #take the sum and check the sum and if it is greater delete everything 
    cursor.execute("SELECT SUM(credits) FROM student_courses_planned JOIN course ON student_courses_planned.course_id = course.id WHERE user_id=%s",(userId,))
    creditHours = cursor.fetchone()
    if int(creditHours["SUM(credits)"]) < 30:
        cursor.execute("DELETE FROM `student_courses_planned` WHERE user_id=%s", (userId,))
        myDb.commit()
        flash("You do not have enough credits planned for your degree. Please try again.", "danger")
        return redirect(url_for('view_form1'))
    
    #if we have reached here it means we have fulfilled all conditions 
    myDb.commit()
    flash("You have successfuly submitted your Form1 application", "success")
    return redirect(url_for('home'))

@app.route("/graduation_apply", methods=["POST"])
@login_required
@authorize(["student"])
def graduation_apply():

    userId = session['userId'] 
    cursor = myDb.cursor(dictionary=True, buffered=True)

    cursor.execute("SELECT `grad_status` FROM `student_info` WHERE user_id=%s",(userId,))
    gradStat = cursor.fetchone()['grad_status']
    if gradStat == 'cleared':
        flash("You cannot apply for graduation again.", "danger")
        return redirect(url_for('home'))
    
    #checking if the student submitted form1
    cursor.execute("SELECT `course_id` FROM `student_courses_planned` WHERE user_id=%s", (userId,))
    cursor.fetchall()
    if cursor.rowcount==0:
        flash("You have not submitted your Form1. You cannot apply for graduation.", "danger")
        return redirect(url_for('home'))

    #get their planned courses get the classes they took and compare these, if one is missing/ none, return you have not fulfilled your form1 requirements.
    cursor.execute("SELECT `course_id` FROM `student_courses_planned` WHERE user_id=%s", (userId,))
    coursestaken = cursor.fetchall()
    for takenCourses in coursestaken:
        cursor.execute("SELECT course_id FROM  student_courses WHERE course_id=%s AND user_id=%s", (takenCourses['course_id'], userId))
        planned = cursor.fetchone()
        if planned == None:
            flash("You have not taken all of your planned courses. You cannot apply for graduation.", "danger")
            return redirect(url_for('home'))

    cursor.execute("SELECT `program`, `form_approved`, `thesis_passed` FROM `student_info` WHERE user_id=%s", (userId,))
    studentInfo = cursor.fetchone()
    # checking if the form was approved
    if studentInfo['form_approved'] == 0:
        flash("Your Form1 has not been approved. You cannot apply for graduation.", "danger")
        return redirect(url_for('home'))

    standing = studentSuspended(userId)
    if standing == True:
        flash("You are in academic suspension. You cannot apply for graduation", "danger")
        return redirect(url_for('home'))

    #get gpa for student
    gpa = calculateGpa(userId)

    # ensure a program is selected
    if not request.form['program']:
        flash("You must select a program.", "danger")
        return redirect(url_for('home'))
    
    # update student_info with new program
    cursor.execute("UPDATE `student_info` SET `program`=%s WHERE user_id=%s", (request.form['program'], userId))

    if request.form['program'] == 'phd':
        #get their thesis_passed
        if studentInfo['thesis_passed'] == 0:
            flash("Your thesis has not passed. You cannot apply for graduation.", "danger")
            return redirect(url_for('home'))

        # checking minimum credit hours (36 for phd)
        cursor.execute("SELECT `value` FROM `degree_requirements` WHERE requirement='min_credit_hours' AND program='phd' ")
        minCreditsPhd = float(cursor.fetchone()['value'])
        cursor.execute("SELECT SUM(credits) FROM student_courses_planned JOIN course ON student_courses_planned.course_id = course.id WHERE user_id=%s",(userId,))
        totalCreditHoursPhd = cursor.fetchone()
        if float(totalCreditHoursPhd['SUM(credits)']) < minCreditsPhd:
            flash("You have not taken enough credits. You cannot apply for graduation.", "danger")
            return redirect(url_for('home'))

        #checking minimum CSCI hours (30)
        cursor.execute("SELECT `value` FROM `degree_requirements` WHERE requirement = 'min_cs_credit_hours' AND program = 'phd'")
        minCsCreditsPhd = float(cursor.fetchone()['value'])
        cursor.execute("SELECT SUM(credits) FROM student_courses_planned JOIN course ON student_courses_planned.course_id = course.id WHERE user_id=%s AND department='CSCI' ",(userId,))
        totalCsCreditHoursPhd = cursor.fetchone()['SUM(credits)']
        if totalCsCreditHoursPhd < minCsCreditsPhd:
            flash("You have not taken enough Computer Science courses to fullfil degree requirements. You cannot apply for graduation.", "danger")
            return redirect(url_for('home'))

        # no more than 2 grades below B
        cursor.execute("SELECT `value` FROM `degree_requirements` WHERE requirement='most_below_b_grades' AND program='phd' ")
        maxNumBPhd = float(cursor.fetchone()['value'])
        cursor.execute("SELECT COUNT(grade) FROM `student_courses` WHERE user_id=%s AND `grade` NOT IN ('A', 'A-', 'B+', 'B', 'IP')", (userId,))
        numberB = cursor.fetchone()
        if numberB['COUNT(grade)'] > maxNumBPhd:
            flash("You have too many grades below B. You cannot apply for graduation.", "danger")
            return redirect(url_for('home'))
        
        # a min GPA of 3.5
        cursor.execute("SELECT `value` FROM `degree_requirements` WHERE requirement='min_gpa' AND program='phd' ")
        minGpaPhd = float(cursor.fetchone()['value'])
        if gpa < minGpaPhd:
            flash("Your grade point average is not high enough. You cannot apply to graduate", "danger")
            return redirect(url_for('home'))

        cursor.execute("UPDATE `student_info` SET grad_status='cleared' WHERE user_id=%s ", (userId,))
        myDb.commit()
        flash("You have succesfully applied for graduation. You are now waiting for administration aproval", "success")
        return redirect(url_for('home'))

    if request.form['program'] == 'masters':
        #checking that the student is taking the 3 required classed for masters
        cursor.execute("SELECT `id` FROM `course` WHERE required_masters=1")
        masterCourses = cursor.fetchall()
        for master in masterCourses:
            cursor.execute("SELECT `course_id` FROM `student_courses` WHERE course_id=%s", (master['id'],))
            if cursor.rowcount == 0:
                flash("You are missing one of the required classes for your degree. You cannot apply for graduation.", "danger")
                return redirect(url_for('home'))

        #need to check at least 30 credit hours
        cursor.execute("SELECT `value` FROM `degree_requirements` WHERE requirement='min_credit_hours' AND program='masters' ")
        minCreditsMasters = float(cursor.fetchone()['value'])
        cursor.execute("SELECT SUM(credits) FROM student_courses_planned JOIN course ON student_courses_planned.course_id = course.id WHERE user_id=%s",(userId,))
        creditHours = cursor.fetchone()
        if float(creditHours['SUM(credits)']) < minCreditsMasters:
            flash("You have not taken enough credits. You cannot apply for graduation.", "danger")
            return redirect(url_for('home'))

        # not more than one grade below b
        cursor.execute("SELECT `value` FROM `degree_requirements` WHERE requirement='most_below_b_grades' AND program='masters' ")
        maxNumBMasters = float(cursor.fetchone()['value'])
        cursor.execute("SELECT COUNT(grade) FROM `student_courses` WHERE user_id=%s AND `grade` NOT IN ('A', 'A-', 'B+', 'B', 'IP')", (userId,))
        numberB = cursor.fetchone()
        if float(numberB['COUNT(grade)']) > maxNumBMasters:
            flash("You have too many grades below B. You cannot apply for graduation.", "danger")
            return redirect(url_for('home'))

         # taken at MOST 2 courses outside CS department as part of the 30 credits
        cursor.execute("SELECT `value` FROM `degree_requirements` WHERE requirement='most_non_cs_courses' AND program='masters' ")
        maxCsCreditsMasters = float(cursor.fetchone()['value'])
        cursor.execute("SELECT COUNT(department) FROM student_courses INNER JOIN course ON student_courses.course_id = course.id WHERE department!= 'CSCI' AND user_id=%s",(userId,))
        nonCs = cursor.fetchone()
        if int(nonCs["COUNT(department)"]) > maxCsCreditsMasters:
            flash("You have taken too many non-computer science courses. You cannot apply for graduation.", "danger")

        #need to check gpais above 3.0 for masters student 
        cursor.execute("SELECT `value` FROM `degree_requirements` WHERE requirement='min_gpa' AND program='masters' ")
        minGpaMasters = float(cursor.fetchone()['value'])
        if gpa < minGpaMasters:
            flash("Your grade point average is not high enough. You cannot apply to graduate", "danger")
            return redirect(url_for('home'))
        
        cursor.execute("UPDATE `student_info` SET grad_status='cleared' WHERE user_id=%s ", (userId,))
        myDb.commit()
        flash("You have succesfully applied for graduation. You are now waiting for administration aproval", "success")
        return redirect(url_for('home'))

    flash("You cannot apply for graduation", "warning")
    return redirect(url_for('home'))

@app.errorhandler(401)
def forbidden(e):
    return render_template('401.html')

