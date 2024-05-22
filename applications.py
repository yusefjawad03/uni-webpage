from flask import Flask, render_template, redirect, session, request, url_for, Flask, flash, Blueprint
from datetime import datetime
from helpers import myDb, login_required, authorize
from users import users

applications = Blueprint('applications', __name__, template_folder='templates')


@applications.route("/application/application_form", methods=["GET", "POST"])
@login_required
@authorize(["applicant"])
def application_form():
    user_id=session['userId']
    if request.method == "POST":
            cur = myDb.cursor()

            ssn = request.form.get("SSN")
            cur.execute("SELECT SSN FROM applications WHERE SSN=%s", (ssn,))
            ssn_exists = cur.fetchone()
            if ssn_exists:
                flash("SSN already exists")
                return redirect(url_for("applications.application_form"))
            # Select the email, first_name, last_name, and street_address from the user table
            cur.execute("SELECT email, first_name, last_name, street_address, city, state, zip FROM user WHERE id=%s", (user_id,))
            user_info = cur.fetchone()

            first_name = user_info[1]
            last_name = user_info[2]
            email = user_info[0]
            address = user_info[3]
            city = user_info[4]
            state = user_info[5]
            zip = user_info[6]
            degree_sought = request.form.get("DegreeSought")
            admission_date = request.form.get("AdmissionDate")
            prior_degrees = request.form.get("PriorDegrees")
            experience = request.form.get("Experience")
            recommendation_letters_1 = request.form.get('recommendation_letters_1')
            recommendation_letters_2 = request.form.get('recommendation_letters_2')
            recommendation_letters_3 = request.form.get('recommendation_letters_3')
            rec_letter = ' '.join(filter(None, [recommendation_letters_1, recommendation_letters_2, recommendation_letters_3]))
            verbal_score = request.form.get("VerbalScore")
            quantitative_score = request.form.get("QuantitativeScore")
            total_score = request.form.get("TotalScore")
            graduation_year = request.form.get("YearofGraduation")
            gpa = request.form.get("GPA")
            university = request.form.get("University")
            transcript = request.form.get("TranscriptSentStatus")

            # Save the application information to the database
            cur.execute("""
                UPDATE applications 
                SET 
                    SSN = CASE WHEN %s IS NOT NULL THEN %s ELSE SSN END, 
                    DegreeSought = CASE WHEN %s IS NOT NULL THEN %s ELSE DegreeSought END, 
                    AdmissionDate = CASE WHEN %s IS NOT NULL THEN %s ELSE AdmissionDate END,
                    PriorDegrees = CASE WHEN %s IS NOT NULL THEN %s ELSE PriorDegrees END, 
                    rec_letter = CASE WHEN %s IS NOT NULL THEN %s ELSE rec_letter END, 
                    VerbalScore = CASE WHEN %s IS NOT NULL THEN %s ELSE VerbalScore END, 
                    QuantitativeScore = CASE WHEN %s IS NOT NULL THEN %s ELSE QuantitativeScore END, 
                    TotalScore = CASE WHEN %s IS NOT NULL THEN %s ELSE TotalScore END, 
                    Experience = CASE WHEN %s IS NOT NULL THEN %s ELSE Experience END, 
                    YearofGraduation = CASE WHEN %s IS NOT NULL THEN %s ELSE YearofGraduation END, 
                    GPA = CASE WHEN %s IS NOT NULL THEN %s ELSE GPA END, 
                    University = CASE WHEN %s IS NOT NULL THEN %s ELSE University END, 
                    TranscriptSentStatus = CASE WHEN %s IS NOT NULL THEN %s ELSE TranscriptSentStatus END, 
                    Status = 'complete'
                WHERE UID = %s
            """, (ssn, ssn, degree_sought, degree_sought, admission_date, admission_date, prior_degrees, prior_degrees, rec_letter, rec_letter, verbal_score, verbal_score, quantitative_score, quantitative_score, total_score, total_score, experience, experience, graduation_year, graduation_year, gpa, gpa, university, university, transcript, transcript, user_id))

            myDb.commit()

            cur.execute("INSERT INTO RecommendationLetters (ID, LetterWriterEmail, LetterRequestEmailSentStatus) VALUES (%s, %s, %s)", (user_id, rec_letter, True))
            myDb.commit()

            cur.close()

            return redirect(url_for("applications.status"))
    else:
        cur = myDb.cursor()
        cur.execute("SELECT email, first_name, last_name, street_address, city, state, zip FROM user WHERE id=%s", (user_id,))
        user_info = cur.fetchone()
            
        first_name = user_info[1]
        last_name = user_info[2]
        address = user_info[3]
        email = user_info[0]
        city = user_info[4]
        state = user_info[5]
        zip = user_info[6]
        cur.close()
        
        cur = myDb.cursor()
        cur.execute("SELECT SSN, DegreeSought, AdmissionDate, PriorDegrees, rec_letter, VerbalScore, QuantitativeScore, TotalScore, Experience, YearofGraduation, GPA, University, TranscriptSentStatus, Status FROM applications WHERE UID=%s", (user_id,))
        info_user = cur.fetchone()
        cur.close()

        if info_user is not None:
            ssN = info_user[0]
            dgsought = info_user[1]
            adate = info_user[2]
            priordeg = info_user[3]
            reclet = info_user[4]
            verbscore = info_user[5]
            quantscore = info_user[6]
            totalscore = info_user[7]
            exper = info_user[8]
            year = info_user[9]
            gp = info_user[10]
            unipast = info_user[11]
            tscript = info_user[12]
            status = info_user[13]
        else:
            ssN = None
            dgsought = None
            adate = None
            priordeg = None
            reclet = None
            verbscore = None
            quantscore = None
            totalscore = None
            exper = None
            year = None
            gp = None
            unipast = None
            tscript = None
            status = None

        return render_template("application_form.html", quantscore=quantscore, totalscore=totalscore, exper=exper, reclet=reclet, verbscore=verbscore, adate=adate , priordeg=priordeg, ssN=ssN, dgsought=dgsought, first_name=first_name, last_name=last_name, address=address, email=email, city=city, state=state, zip=zip, gp=gp, unipast=unipast, year=year, tscript=tscript, status=status)
  

@applications.route('/recommendation', methods=['GET', 'POST'])
@login_required
def recommendation():
    user_id = session['userId']
    email = session['email']  # retrieve email from session

    cursor = myDb.cursor()
    cursor.execute("SELECT LetterWriterEmail FROM RecommendationLetters WHERE ID = %s AND LetterWriterEmail LIKE %s", (user_id, "%" + email + "%"))
    rows = cursor.fetchall()
    letter_writer_emails = []
    for row in rows:
        emails = row[0].split()
        for e in emails:
            if email in e:
                letter_writer_emails.append(e)
                break
    cursor.close()
    if request.method == 'POST':
        letter_writer_name = request.form['LetterWriterName']
        letter_writer_title = request.form['LetterWriterTitle']
        letter_writer_affiliation = request.form['LetterWriterAffiliation']
        recommendation_rating = int(request.form['RecommendationRating'])
        recommendation_comments = request.form['RecommendationComments']

        cursor = myDb.cursor()

        for letter_writer_email in letter_writer_emails:
            cursor.execute("UPDATE RecommendationLetters SET LetterReceivedStatus = %s, LetterWriterName = %s, LetterWriterTitle = %s, LetterWriterAffiliation = %s, RecommendationRating = %s, RecommendationComments = %s WHERE LetterWriterEmail = %s AND ID = %s", (True, letter_writer_name, letter_writer_title, letter_writer_affiliation, recommendation_rating, recommendation_comments, letter_writer_email, user_id))

        myDb.commit()
        cursor.close()

        flash('Recommendation letter complete and under review')
        return redirect(url_for('applications.applicant'))

    return render_template('recommendation.html', letter_writer_email=letter_writer_emails, email=email)


@applications.route('/recommendation_check', methods=['GET', 'POST'])
@login_required
def recommendation_check():
    if request.method == 'POST':
        email = request.form['email']
        cursor=myDb.cursor()
        cursor.execute("SELECT LetterWriterEmail FROM RecommendationLetters WHERE LetterWriterEmail LIKE %s", ("%" + email + "%",))
        result = cursor.fetchone()
        cursor.close()
        if result:
            session['email'] = email
            return redirect(url_for('applications.recommendation'))
        else:
            flash('No recommendation letters have been requested for this email.')
    return render_template('recommendation_check.html')


@applications.route('/applicant')
@login_required
@authorize(["applicant"])
def applicant():
        # do something with type
        decision = session.get('decision')
        return render_template('applicant.html', decision=decision)



@applications.route("/update_applicant_info", methods=["GET", "POST"])
def update_applicant_info():
    if request.method == "POST":
        # Update applicant information in the database
        return render_template("update_applicant_info.html")


@applications.route('/review_applications', methods=['GET', 'POST'])
@login_required
@authorize(["faculty", "gs", "sysadmin"])
def review_applications():
    user_id = session['userId']
    type = session.get('userType')
    decision = request.form.get('action')

    if request.method == 'POST':
        transcript_received = request.form.get('transcript_received')
        if transcript_received == 'received':
            transcript_status = True
        else:
            transcript_status = False

        app_id = request.form.get('app_id')
        cursor = myDb.cursor()
        cursor.execute("UPDATE applications SET TranscriptReceivedStatus = %s, Status=%s WHERE app_id = %s", (transcript_status, decision ,app_id))
        1
        myDb.commit()
        cursor.close()

    cursor = myDb.cursor()
    cursor.execute("SELECT app_id, UID, user.first_name, user.last_name, user.email, applications.Payment, applications.DegreeSought FROM applications JOIN user ON applications.UID=user.id")
    applications = cursor.fetchall()

    cursor.execute("SELECT is_reviewer, is_admissions_chair FROM faculty_info WHERE faculty_info.user_id=%s", (user_id,))
    factype = cursor.fetchone()

    cursor.close()
    return render_template('review_applications.html', applications=applications, type=type, factype=factype)


@applications.route('/confirm_student/<int:app_id>', methods=['POST'])
@login_required
def confirm_student(app_id):
    cursor = myDb.cursor()
    cursor.execute("UPDATE user SET type='student' WHERE id=(SELECT UID FROM applications WHERE app_id=%s)", (app_id,))
    
    # retrieve the necessary data from the applications table
    cursor.execute("SELECT UID, AdmissionDate, DegreeSought FROM applications WHERE app_id=%s", (app_id,))
    result = cursor.fetchone()
    uid, admit_date_str, degree = result

    if 'Summer' in admit_date_str:
        admit_date = datetime.strptime(admit_date_str, 'Summer %Y')
    elif 'Fall' in admit_date_str:
        admit_date = datetime.strptime(admit_date_str, 'Fall %Y')
    elif 'Spring' in admit_date_str:
        admit_date = datetime.strptime(admit_date_str, 'Spring %Y')
    else: 
        flash("Admission Date not specified")
    
    # extract the year from the datetime object and convert it to an integer
    admit_year = int(admit_date.strftime('%Y'))
    
    # query to retrieve RecommendedAdvisorID from RecommendationLetters table
    cursor.execute("SELECT RecommendedAdvisorID FROM RecommendationLetters JOIN applications ON RecommendationLetters.ID=applications.UID WHERE applications.app_id = %s", (app_id,))
    result = cursor.fetchone()
    if result:
        advisor_id = result[0]
    else:
        # if no RecommendedAdvisorID found, set advisor_id to null
        advisor_id = None
    
    # insert the data into the student_info table
    cursor.execute("INSERT INTO student_info (user_id, admit_year, program, advisor_id) VALUES (%s, %s, %s, %s)", (uid, admit_year, degree, advisor_id))
    
    myDb.commit()
    cursor.close()
    flash('Student confirmed')
    return redirect(url_for('applications.review_applications'))

@applications.route('/all_applicants')
@login_required
@authorize(["gs", "sysadmin"])
def all_applicants():
    applicant_id = request.args.get("applicant_id")
    cur = myDb.cursor()
    cur.execute("SELECT * FROM applications JOIN user ON applications.UID=user.id WHERE app_id = %s", (applicant_id,))
    application_data = cur.fetchone()
    cur.close()

    return render_template('all_applicants.html', application_data=application_data)

@applications.route('/stats', methods=["GET", "POST"])
@login_required
@authorize(["sysadmin"])
def stats():
    cur = myDb.cursor()
    cur.execute("SELECT COUNT(*) FROM applications")
    total_applicants = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM applications WHERE Status = 'admitted'")
    total_admitted = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM applications WHERE Status = 'rejected'")
    total_rejected = cur.fetchone()[0]

    cur.execute("SELECT AVG(TotalScore) FROM applications WHERE DegreeSought = 'masters'")
    masters_average_gre = cur.fetchone()[0]

    cur.execute("SELECT AVG(TotalScore) FROM applications WHERE DegreeSought = 'phd'")
    phd_average_gre = cur.fetchone()[0]

    cur.close()

    return render_template('stats.html', total_applicants=total_applicants, total_admitted=total_admitted, total_rejected=total_rejected, masters_average_gre=masters_average_gre, phd_average_gre=phd_average_gre)



@applications.route('/review_form', methods=["GET", "POST"])
@login_required
@authorize(["faculty", "gs", "sysadmin"])
def review_form():
    if request.method == "POST":
        applicant_id = request.args.get("applicant_id")
        recommendation = request.form.get("recommendation")
        comments = request.form.get("comments")
        advisor = request.form.get("advisor")
        
        reviewer_id = session.get("userId")
        # Check if reviewer_id is None
        if reviewer_id is None:
            flash("Access Denied")

        # Store the review form data into the ReviewForms table
        cur = myDb.cursor()
        cur.execute("INSERT INTO ReviewForms (ReviewerID, ReviewerComments, RecommendationRating, RecommendedAdvisorID) VALUES (%s, %s, %s, %s)",
                    (reviewer_id, comments, recommendation, advisor))
        myDb.commit()
        cur.close()

        flash('Review Form Submitted Succesfully')
        return redirect(url_for("applications.review_applications"))
    else:
        applicant_id = request.args.get("applicant_id")

        cur = myDb.cursor()
        cur.execute("SELECT user.id FROM user JOIN faculty_info ON user.id = faculty_info.user_id WHERE user.type = 'faculty' AND faculty_info.is_advisor = 1")
        advisors = [row[0] for row in cur.fetchall()]
        cur.close()

        cur2 = myDb.cursor()
        cur2.execute("SELECT * FROM RecommendationLetters JOIN applications ON RecommendationLetters.ID=applications.UID WHERE applications.app_id = %s", (applicant_id,))
        recommendation_data = cur2.fetchone()
        cur2.close()

        cur3 = myDb.cursor()
        cur3.execute("SELECT * FROM applications WHERE app_id = %s", (applicant_id,))
        application_data = cur3.fetchone()
        cur3.close()
        
        return render_template("review_form.html", applicant_id=applicant_id, application_data=application_data, advisors=advisors, recommendation_data=recommendation_data)


@applications.route('/all_reviews', methods=['GET'])
@login_required
@authorize(["gs", "sysadmin"])
def all_reviews():
    # Get the reviewer ID from the session
    # reviewer_id = session.get('userId')

    # Fetch review forms for the logged-in reviewer
    cur = myDb.cursor()
    cur.execute("SELECT * FROM ReviewForms")
    review_forms = cur.fetchall()
    cur.close()

    return render_template('all_reviews.html', review_forms=review_forms)


@applications.route('/status', methods=['GET', 'POST'])
@login_required
def status():
    user_id = session['userId']
    cur = myDb.cursor()
    cur.execute("SELECT Status FROM applications WHERE UID = %s", (user_id,))
    status = cur.fetchone()
    cur.close()

    if not status or not status[0]:
        cur = myDb.cursor()
        cur.execute('UPDATE applications SET Status=%s WHERE UID=%s', ("incomplete", user_id))
        myDb.commit()
        cur.close()
        status = ("incomplete",)

    if 'accepted' not in session:
            session['accepted'] = False  
    if request.method == 'POST' and status[0] in ["admit_aid", "admit"]:
        session['accepted'] = True


    return render_template("status.html", status=status, accepted=session['accepted'], user_id=user_id)


@applications.route('/paypal')
def paypal():
    return render_template('paypal.html')

@applications.route('/pay-admission-fee', methods=['POST'])
def pay_admission_fee():
    user_id = session['userId']
    cursor = myDb.cursor()
    cursor.execute("UPDATE applications SET Payment=%s WHERE UID=%s", (1, user_id))
    myDb.commit()
    cursor.close()
    flash("Your Deposit has been sent and will be reviewed")
    return redirect(url_for('applications.status'))