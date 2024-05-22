from flask import session, render_template, request, redirect, url_for, flash, Blueprint
from helpers import authorize, myDb, login_required

chatroom = Blueprint('chatroom', __name__, template_folder='templates')

@chatroom.route('/chatRoom')
@login_required
@authorize(['alum'])
def view():
    cursor = myDb.cursor(dictionary=True)
    cursor.execute("SELECT message, identity FROM alumni_messages ORDER BY message_time ASC")
    messages = cursor.fetchall()
    return render_template("chatroom.html", messages=messages)


@chatroom.route('/send', methods=['GET', 'POST'])
@login_required
@authorize(['alum'])
def send_message():
    cursor = myDb.cursor(dictionary=True)
    username = session['username']
    userId = session['userId']

    if request.method=='POST':
        cursor.execute("INSERT INTO `alumni_messages` (identity,message,user_id) VALUES (%s,%s, %s)", (username, request.form["message"], userId ))
        myDb.commit()

    return redirect(url_for('.view'))
    