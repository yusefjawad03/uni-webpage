from flask import render_template, request, redirect, url_for, flash, Blueprint, session
from helpers import authorize, myDb, login_required

transcript = Blueprint('transcript', __name__, template_folder='templates')

gradeConversion = {
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "F": 0.0
}

def calculateGpa(studentId, semester = None):
    cursor = myDb.cursor(dictionary=True)
    if semester is None:
        cursor.execute("SELECT `grade`, `credits` FROM `student_courses` INNER JOIN `course` ON `student_courses`.`course_id` = `course`.`id` WHERE `user_id` = %s", (studentId,))
    else:
        cursor.execute("SELECT `grade`, `credits` FROM `student_courses` INNER JOIN `course` ON `student_courses`.`course_id` = `course`.`id` WHERE `user_id` = %s AND `student_courses`.`semester` = %s AND `student_courses`.`year` = %s", (studentId, semester["semester"], semester["year"]))
    courses = cursor.fetchall()
    if len(courses) == 0:
        return None
    myDb.commit()

    totalCredits = 0
    totalGradePoints = 0
    for course in courses:
        if course["grade"] not in gradeConversion:
            continue
        totalCredits += course["credits"]
        totalGradePoints += course["credits"] * gradeConversion[course["grade"]]
    if totalCredits == 0:
        # handle the case where totalCredits is zero
        return 0
    return round(totalGradePoints / totalCredits, 2)

def studentSuspended(studentId):
    cursor = myDb.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(`grade`) AS `count` FROM `student_courses` WHERE `user_id` = %s AND `grade` NOT IN ('A', 'A-', 'B+', 'B', 'IP')", (studentId,))
    result = cursor.fetchone()
    myDb.commit()
    return result["count"] >= 3

@transcript.route("/")
@transcript.route("/<int:userId>")
@login_required
def view(userId=None):    
    # Create a cursor to execute queries
    cursor = myDb.cursor(dictionary=True)
    
    # If userId is not specified, use the currently logged in user's id
    if userId is None:
        userId = session['userId']

    # Get requested user
    cursor.execute("SELECT `type` FROM user WHERE id = %s", (userId,))
    user = cursor.fetchone()

    # Check if the user requested is a student/alum
    if not user or user["type"] not in ("student", "alum"):
        # If the user is not a student/alum, redirect to the home page
        flash("Requested user is not a student and does not have a transcript.", "danger")
        return redirect(url_for('home'))
    
    # If the logged in user is a faculty advisor, ensure they are allowed to view the requested student's transcript
    if session['userType'] == "faculty":
        cursor.execute("SELECT is_advisor FROM faculty_info WHERE user_id=%s", (session['userId'],))
        isAdvisor = cursor.fetchone()['is_advisor']
        if isAdvisor == 0:
            return redirect(url_for('401'))
        cursor.execute("SELECT `advisor_id` FROM `student_info` WHERE `user_id` = %s AND `advisor_id` = %s", (userId, session['userId']))
        if cursor.fetchone() is None:
            flash("You are not allowed to view the requested student's transcript.", "danger")
            return redirect(url_for('home'))
    # If the logged in user is a student, ensure they are allowed to only view their own transcript
    elif session['userType'] in ("student", "alum"):
        if session['userId'] != userId:
            flash("You are not allowed to view the requested student's transcript.", "danger")
            return redirect(url_for('.view'))

    # Get the semesters the user has taken courses in
    cursor.execute("SELECT DISTINCT `semester`, `year` FROM `student_courses` WHERE `user_id` = %s ORDER BY `year` DESC, `semester` DESC", (userId,))
    semesters = cursor.fetchall()

    # Get the courses the user has taken in each semester
    for semester in semesters:
        cursor.execute("SELECT `department`, `cnumber`, `title`, `credits`, `grade` FROM `student_courses` INNER JOIN `course` ON `student_courses`.`course_id` = `course`.`id` WHERE `user_id` = %s AND `student_courses`.`semester` = %s AND `student_courses`.`year` = %s", (userId, semester["semester"], semester["year"]))
        semester["courses"] = cursor.fetchall()
        semester["gpa"] = calculateGpa(userId, semester)

    myDb.commit()

    # Calculate the student's overall GPA
    overallGpa = calculateGpa(userId)
    
    return render_template("transcript.html", semesters=semesters, overallGpa=overallGpa, suspended=studentSuspended(userId))