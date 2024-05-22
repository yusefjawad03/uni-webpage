from flask import render_template, request, redirect, url_for, flash, Blueprint, session, abort
from helpers import authorize, myDb, login_required

students = Blueprint('students', __name__, template_folder='templates')

programTypes = {
    "masters": "Masters",
    "phd": "PhD"
}

@students.route("/")
@login_required
@authorize(["faculty", "gs", "sysadmin"])
def index():
    cursor = myDb.cursor(dictionary=True, buffered=True)
    advisors = None

    if session['userType'] == "faculty":
        cursor.execute("SELECT `user_id`, `program`, `grad_status`, `thesis_passed`, `form_approved`, `first_name`, `last_name` FROM `student_info` INNER JOIN `user` ON `student_info`.`user_id` = `user`.`id` WHERE `advisor_id` = %s", (session["userId"],))
        students = cursor.fetchall()
    else:
        # Get the list of faculty advisors
        cursor.execute("SELECT `id`, `first_name`, `last_name` FROM `user` WHERE `type` = 'faculty' ORDER BY `first_name`, `last_name`")
        advisors = cursor.fetchall()
        cursor.execute("SELECT `student_info`.`user_id`, `student_info`.`program`, `student_info`.`grad_status`, `student_info`.`grad_semester`, `student_info`.`grad_year`, `student_info`.`advisor_id`, `student_info`.`form_approved`, `student_info`.`thesis_passed`, `student`.`first_name`, `student`.`last_name`, `advisor`.`first_name` AS `advisor_first_name`, `advisor`.`last_name` AS `advisor_last_name` FROM `student_info` INNER JOIN `user` AS `student` ON `student_info`.`user_id` = `student`.`id` LEFT JOIN `user` AS `advisor` ON `student_info`.`advisor_id` = `advisor`.`id`")
        students = cursor.fetchall()
   

    myDb.commit()

    return render_template("students_index.html", students=students, programTypes=programTypes, advisors=advisors)

@students.route("/alumni")
@login_required
@authorize(["gs", "sysadmin"])
def alumni():
    cursor = myDb.cursor(dictionary=True)

    cursor.execute("SELECT `alumni_info`.`program`, `user`.`email`, `alumni_info`.`grad_year`, `user`.`first_name`, `user`.`last_name`, `user`.`id` AS user_id FROM `alumni_info` INNER JOIN `user` ON `alumni_info`.`user_id` = `user`.`id`")
    
    students = cursor.fetchall()

    myDb.commit()

    return render_template("students_alumni.html", students=students, programTypes=programTypes)

@students.route("/<int:studentId>/pass-thesis")
@login_required
@authorize(["faculty", "sysadmin"])
def passThesis(studentId):
    cursor = myDb.cursor(dictionary=True)

    # ensure advisor is assigned to student
    cursor.execute("SELECT `advisor_id` FROM `student_info` WHERE `user_id` = %s", (studentId,))
    advisorId = cursor.fetchone()['advisor_id']
    if session['userType'] == "advisor" and advisorId != session['userId']:
        flash("You are not assigned to this student.", "danger")
        return redirect(url_for('.index'))

    # ensure student is PhD
    cursor.execute("SELECT `program` FROM `student_info` WHERE `user_id` = %s", (studentId,))
    program = cursor.fetchone()['program']
    if program != "phd":
        flash("Only PhD students can pass their thesis.", "danger")
        return redirect(url_for('.index'))

    # update thesis status
    cursor.execute("UPDATE `student_info` SET `thesis_passed` = 1 WHERE `user_id` = %s", (studentId,))
    myDb.commit()

    return redirect(url_for('.index'))

@students.route("/<int:studentId>/form/review")
@login_required
@authorize(["faculty", "gs", "student", "sysadmin"])
def form_review(studentId):
    cursor = myDb.cursor(dictionary=True)

    if session["userType"] == "student" and session["userId"] != studentId:
        # student can only view their own form
        abort(401)

    # ensure advisor is assigned to student
    if session["userType"] == "faculty":
        cursor.execute("SELECT `advisor_id` FROM `student_info` WHERE `user_id` = %s", (studentId,))
        advisorId = cursor.fetchone()['advisor_id']
        cursor.execute("SELECT is_advisor FROM faculty_info WHERE user_id=%s", (session['userId'],))
        isAdvisor = cursor.fetchone()['is_advisor']
        if isAdvisor == 0:
            return redirect(url_for('401'))
        if advisorId != session['userId']:
            flash("You are not assigned to this student.", "danger")
            return redirect(url_for('.index'))


    # ensure student has courses on form1
    cursor.execute("SELECT COUNT(`course_id`) FROM `student_courses_planned` WHERE `user_id` = %s", (studentId,))
    form1 = cursor.fetchone()['COUNT(`course_id`)']
    if form1 == 0 and session["userType"] != "student":
        flash("Student has not submitted a form1.", "danger")
        return redirect(url_for('.index'))
    elif form1 == 0 and session["userType"] == "student":
        return redirect(url_for('view_form1'))

    # get courses on form1
    cursor.execute("SELECT `department`, `cnumber`, `title` FROM `student_courses_planned` INNER JOIN `course` ON `course`.`id` = `student_courses_planned`.`course_id` WHERE `user_id` = %s", (studentId,))
    courses = cursor.fetchall()

    # get student info
    cursor.execute("SELECT `id`, `first_name`, `last_name`, `id`, `program`, `form_approved` FROM `student_info` INNER JOIN `user` ON `student_info`.`user_id` = `user`.`id` WHERE `user_id` = %s", (studentId,))
    student = cursor.fetchone()

    return render_template("students_review_form.html", courses=courses, student=student, programTypes=programTypes)

@students.route("/<int:studentId>/form/approve")
@login_required
@authorize(["faculty", "sysadmin"])
def form_approve(studentId):
    cursor = myDb.cursor(dictionary=True)

    # ensure advisor is assigned to student
    cursor.execute("SELECT `advisor_id` FROM `student_info` WHERE `user_id` = %s", (studentId,))
    advisorId = cursor.fetchone()['advisor_id']
    cursor.execute("SELECT is_advisor FROM faculty_info WHERE user_id=%s", (session['userId'],))
    isAdvisor = cursor.fetchone()['is_advisor']
    if isAdvisor == 0:
        flash("You do not advise any students", "danger")
        return redirect(url_for('401'))
    if session['userType'] == "advisor" and advisorId != session['userId']:
        flash("You are not assigned to this student.", "danger")
        return redirect(url_for('.index'))

    # ensure student has courses on form1
    cursor.execute("SELECT COUNT(`course_id`) FROM `student_courses_planned` WHERE `user_id` = %s", (studentId,))
    if cursor.fetchone()['COUNT(`course_id`)'] == 0:
        flash("Student has not submitted a form1.", "danger")
        return redirect(url_for('.index'))
    
    # update form1 status
    cursor.execute("UPDATE `student_info` SET `form_approved` = 1 WHERE `user_id` = %s", (studentId,))

    return redirect(url_for('.index'))

@students.route("/advisor", methods=["POST"])
@login_required
@authorize(["gs", "sysadmin"])
def advisor():
    cursor = myDb.cursor(dictionary=True)

    # ensure advisor is selected
    if not request.form["advisorId"]:
        flash("You must select an advisor.", "danger")
        return redirect(url_for('.index'))

    # update advisor
    cursor.execute("UPDATE `student_info` SET `advisor_id` = %s WHERE `user_id` = %s", (request.form["advisorId"], request.form["studentId"]))
    flash("Advisor updated.", "success")
    myDb.commit()

    return redirect(url_for('.index'))

@students.route("/<int:studentId>/approve/grad")
@login_required
@authorize(["gs", "sysadmin"])
def approve_grad(studentId):
    cursor = myDb.cursor(dictionary=True)

    # check if graduation has been approved 
    cursor.execute("SELECT `grad_status`, `program` FROM `student_info` WHERE `user_id` = %s", (studentId,))
    studentInfo = cursor.fetchone()
    gradStatus = studentInfo['grad_status']
    program = studentInfo['program']

    if gradStatus == 'cleared':
        # if the student has submitted the form and been approved to graduate:
        # 1. Change the student to be of type "alum"
        # 2. Remove the student info stored in the database
        # 3. Remove any planned courses linked to the studnet info. 
        # 4. add the alumni in to the almuni table

        cursor.execute("UPDATE `user` SET `type` = 'alum' WHERE `id` = %s", (studentId,))
        cursor.execute("DELETE FROM `student_info` WHERE `user_id` = %s", (studentId,))
        cursor.execute("DELETE FROM `student_courses_planned` WHERE `user_id` = %s", (studentId,))
        cursor.execute("INSERT INTO `alumni_info` (`user_id`, `program`) VALUES (%s, %s)",(studentId, program))
        
        myDb.commit()
        flash("Student graduated!", "success")
        return redirect(url_for('.index'))
    else:
        # graduation has not been approved, so don't clear the student 
        flash("Student has not been cleared to graduate!", "danger")
        return redirect(url_for('.index'))


@students.route("/gradDate", methods=["POST"])
@login_required
@authorize(["gs", "sysadmin"])
def gradDate():
    cursor = myDb.cursor(dictionary=True)

    # ensure year and semester are selected and valid
    if not request.form["year"] or not request.form["semester"] or int(request.form["year"]) < 2023 or request.form["semester"] not in ["fall", "spring", "summer"]:
        flash("You must provide a valid semester and year.", "danger")
        return redirect(url_for('.index'))

    # update advisor
    cursor.execute("UPDATE `student_info` SET `grad_year` = %s, `grad_semester` = %s WHERE `user_id` = %s", (request.form["year"], request.form["semester"], request.form["studentId"]))
    flash("Expected graduation date updated.", "success")
    myDb.commit()

    return redirect(url_for('.index'))


@students.route("/create_acc_page")
def create_acc_page():
    if 'userId' not in session:
        return render_template("create_account.html")
    else:
        flash("you cannot create an account!")
        return 

@students.route("/create_acc", methods=['GET', 'POST'])
def create_acc():

    cursor = myDb.cursor(dictionary=True) 
    if request.method == 'POST':
        cursor.execute("SELECT username FROM user WHERE username=%s", (request.form["userName"],))
        name = cursor.fetchone()
        if name == None:
            cursor.execute("SELECT MAX(id) as max_id FROM user")
            last_id = cursor.fetchone()['max_id']
            if last_id == 99999999:
                next_id = 1
            else:
                next_id = last_id + 1
            cursor.execute("INSERT INTO `user` (`id`, `type`, `email`, `username`, `password`, `first_name`,`last_name`, `street_address`, `city`, `state`, `zip` ) VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s)", (next_id, "applicant", request.form['email'], request.form['userName'], request.form['pass'], request.form['firstName'], request.form['lastName'], request.form['streetAdd'], request.form['city'], request.form['state'], request.form['zip'] ))
            cursor.execute("INSERT INTO `applications` (`UID`) VALUES (%s)", (next_id,))
            myDb.commit()
            flash("You have successfully created your account! Please sign in.", "success")
            return redirect(url_for('login'))
        
        flash("This username already exists. Please choose a different one.", "danger")
        return redirect(url_for('students.create_acc_page'))

@students.route("/current", methods=['GET', 'POST'])
@login_required
@authorize(["gs"])
def current_students():
    cursor = myDb.cursor(dictionary=True)
    userId = session["id"]
    if request.method == 'POST':
        #make sure i have everything that I need to select 
        cursor.execute("SELECT first_name, last_name, id, program, thesis_passed, advisor_id program FROM user JOIN ON student_info.user_id = user.id WHERE user_id = %s AND admit_year=%s OR degree=%s", (userId, request.form["ad_year"], request.form['degree']))
        cur_students = cursor.fetchall()
        
        return render_template("students_index.html", student = cur_students)
        #here we can just return student based on admit year or by degree

@students.route("/graduating", methods=['GET', 'POST'])
@login_required
@authorize(["gs"])
def view_graduating():
    cursor = myDb.cursor(dictionary=True) 
   
    cursor.execute("SELECT `student_info`.`user_id`, `student_info`.`program`, `student_info`.`grad_status`, `student_info`.`grad_semester`, `student_info`.`grad_year`, `student_info`.`advisor_id`, `student_info`.`form_approved`, `student_info`.`thesis_passed`, `student`.`first_name`, `student`.`last_name`, `advisor`.`first_name` AS `advisor_first_name`, `advisor`.`last_name` AS `advisor_last_name` FROM `student_info` INNER JOIN `user` AS `student` ON `student_info`.`user_id` = `student`.`id` LEFT JOIN `user` AS `advisor` ON `student_info`.`advisor_id` = `advisor`.`id` WHERE student_info.grad_status=1")
    graduating = cursor.fetchall()
    cursor.execute("SELECT `id`, `first_name`, `last_name` FROM `user` WHERE `type` = 'faculty' ORDER BY `first_name`, `last_name`")
    advisors = cursor.fetchall()

    return render_template("students_index.html", student = graduating, advisors=advisors)


@students.route("/view_alum", methods=['GET', 'POST'])
@login_required
@authorize(["gs"])
def view_alum():
    cursor = myDb.cursor(dictionary=True) 
    userId = session["id"]
    if request.method == 'POST':
        cursor.execute("SELECT user.first_name, user.last_name, user.email, alumni_info.program, alumni_info.grad_year FROM alumni_info JOIN ON user.id = alumni_info.user_id WHERE id=%s AND grad_year=%s", (userId,request.form['grad_year']))
        alumni = cursor.fetchall()

        #need to make alumni index
        return render_template("students_alumni.html",  student = alumni)


@students.route("/chat", methods=['GET', 'POST'])
@login_required
@authorize(["alum"])
def chatroom():
    cursor = myDb.cursor(dictionary=True) 
    userId = session["id"]

    cursor.execute("SELECT username FROM user WHERE id=%s", (userId,))
    user = cursor.fetchone()

    return render_template("chatroom.html", user=user)