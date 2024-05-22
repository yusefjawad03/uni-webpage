from flask import render_template, request, redirect, url_for, flash, Blueprint, session, abort
from helpers import authorize, myDb, login_required
from datetime import datetime
import pytz

registration = Blueprint('registration', __name__, template_folder='templates')

programTypes = {
    "masters": "Masters",
    "phd": "PhD"
}

@registration.route('/assign_grades', methods=['GET', 'POST'])
@login_required
@authorize(["faculty", "gs", "sysadmin"])
def assign_grades():

    cursor = myDb.cursor(dictionary=True, buffered=True)

    prof_id = session["userId"]
    accType = session["userType"]
    message = None

    if request.method == 'POST':
        grade = request.form.get('grade')
        student_id = request.form.get('student_id')
        course_id = request.form.get('course_id')
        # update student_courses for student, course_id with value from drop-down form
        cursor.execute("UPDATE student_courses SET grade = %s WHERE user_id = %s AND course_id = %s", (grade, student_id, course_id))
        myDb.commit()

        # send message
        message = "Grade submitted successfully."

    # fetch students in courses
    # if type 2, only get students in courses taught by prof
    if accType == 'faculty':
        cursor.execute("SELECT p_student.*, course.* FROM user p_student JOIN student_info on p_student.id=student_info.user_id JOIN student_courses ON student_info.user_id = student_courses.user_id JOIN course ON student_courses.course_id = course.ID JOIN user p_professor ON course.professor = p_professor.id WHERE p_professor.id = %s AND p_professor.type = 'faculty'", (prof_id,))
        students = cursor.fetchall()
    # if type 3, get all courses for all students
    elif accType == 'gs' or accType == 'sysadmin':
        cursor.execute("SELECT * FROM user JOIN student_info ON user.id=student_info.user_id JOIN student_courses ON student_info.user_id = student_courses.user_id JOIN course ON student_courses.course_id = course.ID")
        students = cursor.fetchall()
    else:
        return redirect('/error')

    return render_template("assign_grades.html", students=students, accType=accType, message=message)

@registration.route('/assign_professor', methods=['GET', 'POST'])
@login_required
@authorize(["sysadmin"])
def assign_professor():


    cursor = myDb.cursor(dictionary=True, buffered=True)

    cursor.execute("SELECT * FROM course")
    courses = cursor.fetchall()

    cursor.execute("SELECT * FROM user WHERE type = 'faculty'")
    professors = cursor.fetchall()

    if request.method == 'POST':
        cid = request.form['course_id']
        pid = request.form['professor_id']
        cursor.execute("SELECT time, day FROM course WHERE id = %s", (cid,))
        course = cursor.fetchone()
        time = course["time"]
        day = course["day"]
        if(time==1):
            cursor.execute("SELECT * FROM course WHERE professor = %s AND course.time != %s  AND course.day = %s ",
                (pid, 3, day))
        elif(time==3):
            cursor.execute("SELECT * FROM course WHERE professor = %s AND course.time != %s  AND course.day = %s ",
                    (pid, 1, day))
        else:
            cursor.execute("SELECT * FROM course WHERE professor = %s AND day = %s",
                       (pid, day))
        conflict_course = cursor.fetchone()

        if conflict_course:
            return "Error: Professor already teaching at this time"

        cursor.execute("UPDATE course SET professor = %s WHERE id = %s", (pid, cid))
        myDb.commit()
        cursor.execute("SELECT * FROM course")
        courses = cursor.fetchall()
        return render_template("assign_professor.html", courses=courses, professors=professors)

    return render_template("assign_professor.html", courses=courses, professors=professors)


@registration.route('/registration')
@login_required
@authorize(["student"])
def registration2():
    cursor = myDb.cursor(dictionary=True)
    
    # set person, cursor
    user_id = session["userId"]
    cursor = myDb.cursor(dictionary=True, buffered=True)

    # fetch all courses

    search = request.args.get('search')

    # Set person, cursor
    cursor = myDb.cursor(dictionary=True, buffered=True)

    # Fetch all courses
    if(search):
        if search.isdigit():
            cursor.execute("SELECT * FROM course WHERE cnumber = %s", (search,))
        else:
            cursor.execute("SELECT * FROM course WHERE title LIKE %s", ('%' + search + '%',))
    else:
        cursor.execute("SELECT * FROM course")
    courses = cursor.fetchall()
    i=0
    courseDicts=[]
    for course in courses:
      cursor.execute("SELECT prereq_id FROM course_prereq WHERE course_id = %s",(course["ID"], ))
      prereq=cursor.fetchall()
      if course:
        course_dict = {
            'ID': course['ID'],
            'department': course['department'],
            'cnumber': course['cnumber'],
            'title': course['title'],
            'credits' :course['credits'],
            'day' :course['day'],
            'year' :course['year'],
            'require_masters' :course['required_masters'],
            'semester' :course['semester'],
            'time' :course['time'],
            'section' :course['section'],
            'location' :course['location'],
            'capacity' : course['capacity'],
            'professor' : course['professor'],
            'prereq':prereq
        }
        courseDicts.append(course_dict)
    # select all faculty
    cursor.execute("SELECT * FROM user WHERE type='faculty'")
    professors = cursor.fetchall()
    print(professors)
    # fetch current courses
    cursor.execute("SELECT * FROM course JOIN student_courses ON course.ID = student_courses.course_id WHERE student_courses.user_id = %s AND student_courses.grade = 'IP'", (session['userId'],))
    current_courses = cursor.fetchall()

    return render_template("registration.html", courses=courseDicts, professors=professors, current_courses=current_courses)

# add course: student
@registration.route('/add_course', methods = ['GET', 'POST'])
@login_required
@authorize(["student"])
def add_course():
  approved=0
  planned=0
  # set cursor and person
  cursor = myDb.cursor(dictionary=True, buffered=True)
  if request.method == 'POST' and "CID" in request.form:
    # get class prereqs
    CID = request.form.get('CID')
    cursor.execute("Select title from course where ID=%s",(CID,))
    title=cursor.fetchone()
    # print(title)
    canTake=1
    cursor.execute("Select * from course_prereq cp join course c on cp.course_id=c.ID WHERE cp.course_id=%s",(CID, ))
    prereqs=cursor.fetchall()

    for prereq in prereqs:
        # print(prereq["prereq_id"])
        cursor.execute("select * from course where ID=%s",(prereq["prereq_id"], ))
        course=cursor.fetchone()
        # print(session["userId"])
        cursor.execute("Select * from student_courses sc join course c on sc.course_id=c.ID where c.title=%s and sc.user_id=%s",(course["title"],session["userId"] ))
        taken=cursor.fetchall()
        # print(taken)
        cursor.execute("Select * from course where ID=%s",(prereq["prereq_id"], ))
        course=cursor.fetchone()
        if(not taken):
            flash("You have not fulfilled the prerequisite "+course["department"]+ " " + str(course["cnumber"])+"!")
            canTake=0
        
    if(canTake==1):
        cursor.execute("SELECT time,day FROM course WHERE ID = %s",(CID,))
        course=cursor.fetchone()
        day=course["day"]
        time=course["time"]

        # query for conflicting courses
        if(time==1):
            cursor.execute("SELECT * FROM student_courses sc JOIN course c ON sc.course_id = c.ID WHERE sc.user_id = %s AND c.time != %s  AND c.day = %s AND (sc.grade is NULL OR sc.grade =%s)",
                    (session["userId"], 3, day, "IP"))
        elif(time==3):
            cursor.execute("SELECT * FROM student_courses sc JOIN course c ON sc.course_id = c.ID WHERE sc.user_id = %s AND c.time != %s  AND c.day = %s AND (sc.grade is NULL OR sc.grade =%s)",
                    (session["userId"], 1, day, "IP"))
        else:
            cursor.execute("SELECT * FROM student_courses sc JOIN course c ON sc.course_id = c.ID WHERE sc.user_id = %s AND c.day = %s AND (sc.grade is NULL OR sc.grade =%s)",
                    (session["userId"], day, "IP"))
        conflict_courses = cursor.fetchall()
        if(conflict_courses):
            flash("There are conflicting courses in your schedule")
        if not conflict_courses:
            # print("no conflicting courses")
            cursor.execute("SELECT * FROM student_courses_planned where course_id=%s and user_id=%s",
            (CID,session["userId"] ))
            planned=cursor.fetchone()

            cursor.execute("SELECT * FROM student_courses sc join course c ON sc.course_id =c.ID where c.title=%s and user_id=%s",
            (title["title"],session["userId"]))
            takes=cursor.fetchone()
            cursor.execute("SELECT * FROM student_info where user_id=%s and form_approved = 1",
            (session["userId"], ))
            approved=cursor.fetchone()
            # print("takes")

            if(not takes):
                cursor.execute("INSERT INTO student_courses(user_id, course_id) VALUES (%s, %s)",
                    (session["userId"],CID))
            if(takes):
                flash("You have already taken this course")
            myDb.commit()

  return redirect(url_for('registration.registration2'))

# drop a course: student
@registration.route('/drop_course', methods = ['GET', 'POST'])
@login_required
@authorize(["student"])
def drop_course():

    cursor = myDb.cursor(dictionary=True, buffered=True)
    CID = request.form.get('CID')
    if request.method == 'POST' and "CID" in request.form:
        # check if truly taking class
        cursor.execute("SELECT * FROM student_courses WHERE user_id = %s AND course_id = %s",
                      (session["userId"],CID))
        takes=cursor.fetchone()

        if(takes):
            cursor.execute("DELETE FROM student_courses WHERE user_id = %s AND course_id = %s",
                      (session["userId"], CID))
            myDb.commit()

    return redirect(url_for('registration.registration2'))

@registration.route('/course_list', methods = ['GET', 'POST'])
@login_required
def course_list():

    cursor = myDb.cursor(dictionary=True, buffered=True)
    cursor.execute("SELECT * from course ")
    courses_info=cursor.fetchall()


    return render_template("course_list.html", courses=courses_info)
@registration.route('/course_page', methods = ['GET', 'POST'])
@login_required
def course_page():

    CID=request.args.get('CID')    
    cursor = myDb.cursor(dictionary=True, buffered=True)
    cursor.execute("SELECT * from course where ID=%s", (CID,))
    course=cursor.fetchone()
    cursor.execute("SELECT * from course_prereq cp join course ON cp.prereq_id=course.ID where course.title =%s", (course["title"],))
    prereqs=cursor.fetchall()
    # Select course information
    cursor.execute("SELECT * FROM course WHERE ID = %s",
                   (CID,))
    course = cursor.fetchone()

    # Select professor name
    cursor.execute("SELECT first_name, last_name FROM course JOIN user ON course.professor = user.id WHERE course.professor = %s",
                   (course["professor"],))
    professor = cursor.fetchone()

    return render_template("course_page.html", professor=professor, course=course, prereqs=prereqs)
@registration.route('/classmates', methods = ['GET', 'POST'])
@login_required
def viewClassmates():

    cursor = myDb.cursor(dictionary=True, buffered=True)
    CID=request.form.get("course_id") or request.args.get("CID")
    cursor.execute("SELECT * from course where ID=%s",(CID, ))
    course=cursor.fetchone()
    cursor.execute("SELECT user.* from user join student_courses ON user.id=student_courses.user_id where student_courses.course_id =%s and user.id!=%s and (student_courses.grade is NULL or student_courses.grade=%s)", (CID,session["userId"], "IP"))
    classmates=cursor.fetchall()
    cursor.execute("SELECT user.first_name, user.last_name FROM course JOIN user ON course.professor = user.id WHERE course.professor = %s",
                   (course["professor"],))
    professor=cursor.fetchone()
    return render_template("classmates.html", professor=professor, course=course,students=classmates)
@registration.route('/viewStudents', methods = ['GET', 'POST'])
@login_required
def viewStudents():

    cursor = myDb.cursor(dictionary=True, buffered=True)
    CID=request.form.get("course_id") or request.args.get("CID")
    cursor.execute("SELECT * from course where ID=%s",(CID, ))
    course=cursor.fetchone()
    cursor.execute("SELECT user.* from user join student_courses ON user.id=student_courses.user_id where student_courses.course_id =%s and user.id!=%s", (CID,session["userId"]))
    students=cursor.fetchall()
    cursor.execute("SELECT user.first_name, user.last_name FROM course JOIN user ON course.professor = user.id WHERE course.professor = %s",
                   (course["professor"],))
    professor=cursor.fetchone()
    return render_template("viewStudents.html", professor=professor, course=course,students=students)   
@registration.route('/classes')
@login_required
def viewClasses():

    cursor = myDb.cursor(dictionary=True, buffered=True)

    cursor.execute("SELECT course.* from course join student_courses on course.ID =student_courses.course_id where user_id=%s and (student_courses.grade=NULL or student_courses.grade=%s)",(session["userId"],"IP"))
    courses=cursor.fetchall()

    return render_template("classes.html",  courses=courses )


@registration.route('/send_message', methods = ['GET', 'POST'])
@login_required
def send_message():


    cursor = myDb.cursor(dictionary=True, buffered=True)
    recipient=request.form.get("recipient")
    CID=request.form.get("CID")
    # print(type(recipient))
    message=request.form.get("message")
    timezone = pytz.timezone('America/New_York')
    current_time = datetime.now(timezone)

    cursor.execute("INSERT INTO privateMessages (sender_id, recipient_id, message,date,CID) VALUES (%s, %s, %s,%s,%s)",(session["userId"],recipient,message,current_time,CID) )
    myDb.commit()

    return redirect(url_for('registration.viewClassmates', CID=CID))
@registration.route('/draft_message', methods = ['GET', 'POST'])
@login_required
def draft_message():
    recipient=request.args.get("recipient")
    course=request.args.get("course")
    return render_template("message.html",  recipient=recipient, course=course )
@registration.route('/view_messages', methods = ['GET', 'POST'])
@login_required
def view_messages():

    cursor = myDb.cursor(dictionary=True, buffered=True)
    cursor.execute("SELECT * from user join privateMessages on privateMessages.sender_id=user.id where privateMessages.recipient_id=%s",(session["userId"], ))
    messages=cursor.fetchall()
    return render_template("inbox.html",messages=messages)
@registration.route('/rate_course', methods=['POST'])
def rate_course():
    user_id = session["userId"]
    course_id = request.form['CID']
    rating = request.form['rating']
    comment = request.form['comment']
    cursor = myDb.cursor(dictionary=True, buffered=True)
    cursor.execute("INSERT INTO ratings(user_id, course_id, rating, comment) VALUES(%s, %s, %s, %s)", (user_id, course_id, rating, comment))
    myDb.commit()


    return redirect(url_for('registration.my_courses'))

@registration.route('/rate_professor', methods=['POST'])
def rate_professor():
    user_id = session["userId"]
    professor_id = request.form.get('PID')
    rating = request.form['rating']
    comment = request.form['comment']

    cursor = myDb.cursor(dictionary=True, buffered=True)
    cursor.execute("INSERT INTO ratings(user_id, professor_id, rating, comment) VALUES(%s, %s, %s, %s)", (user_id, professor_id, rating, comment))
    myDb.commit()


    return redirect(url_for('registration.my_professors'))


@registration.route('/course_ratings')
def course_ratings():
    cursor = myDb.cursor(dictionary=True, buffered=True)
    course_id = request.args.get("CID")
    cursor.execute("SELECT title from course where ID=%s", (course_id,))
    course=cursor.fetchone()
    cursor.execute("SELECT ratings.*, user.* FROM ratings JOIN user ON ratings.user_id = user.id join course ON ratings.course_id = course.ID WHERE course.title = %s", (course["title"],))
    ratings = cursor.fetchall()
    if ratings:
        average_rating = sum(rating['rating'] for rating in ratings) / len(ratings)
    else:
        average_rating=0


    return render_template('courseRatings.html', ratings=ratings, average_rating=average_rating,CID=course_id)


@registration.route('/professor_ratings')
def professor_ratings():
    cursor = myDb.cursor(dictionary=True, buffered=True)
    professor_id = request.args.get("PID")
    cursor.execute("SELECT ratings.*, user.first_name FROM ratings JOIN user ON ratings.user_id = user.id WHERE ratings.professor_id = %s", (professor_id,))
    ratings = cursor.fetchall()
    if ratings:
        average_rating = sum(rating['rating'] for rating in ratings) / len(ratings)
    else:
        average_rating=0
    return render_template('professorRatings.html', ratings=ratings, average_rating=average_rating,PID=professor_id)

@registration.route('/professor_list')
def professor_list():
    cursor = myDb.cursor(dictionary=True, buffered=True)
    cursor.execute("SELECT * FROM user WHERE type = 'faculty'")
    professors = cursor.fetchall()

    return render_template('professor_list.html', professors=professors)
@registration.route('/my_professors')
def my_professors():
    cursor = myDb.cursor(dictionary=True, buffered=True)
    
    cursor.execute("SELECT DISTINCT u.* FROM user u JOIN course c ON u.id = c.professor JOIN student_courses sc ON c.ID = sc.course_id WHERE sc.user_id = %s AND (sc.grade!='IP' AND sc.grade IS NOT NULL)", (session["userId"],))

    professors = cursor.fetchall()
    return render_template('my_professors.html', professors=professors)
@registration.route('/my_courses')
def my_courses():
    cursor = myDb.cursor(dictionary=True, buffered=True)
    
    cursor.execute("SELECT c.* FROM course c JOIN student_courses sc ON c.ID = sc.course_id WHERE sc.user_id = %s AND sc.grade IS NOT NULL AND sc.grade != 'IP'",(session["userId"], ))

    courses = cursor.fetchall()
    return render_template('my_courses.html', courses=courses)
@registration.route('/profCourses')
def profCourses():
    cursor = myDb.cursor(dictionary=True, buffered=True)
    
    cursor.execute("SELECT c.* FROM course c where professor=%s",(session["userId"], ))
    courses = cursor.fetchall()
    return render_template('profCourses.html', courses=courses)
