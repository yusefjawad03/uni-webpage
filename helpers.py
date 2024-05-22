from functools import wraps
from flask import session, abort, redirect, url_for, request, Flask
import mysql.connector

app = Flask('app')
app.secret_key = "secret_item"
cnx = mysql.connector.connect()

myDb = mysql.connector.connect(
    # not quite sure about the host, but this is what I have at the top of the sql file
    host='phase2-6.cpqmwccqu44e.us-east-1.rds.amazonaws.com',
    user='admin',
    password='6DBPhase2',
    database='university'
)

def authorize(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'userType' not in session or session['userType'] not in roles:
                abort(401)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'userId' not in session:
            # User is not logged in, so save the current route they're trying to access in the session
            session['next'] = request.url
            return redirect(url_for('index'))  # Redirect to the login page
        else:
            # User is logged in, so allow access to the requested route
            return f(*args, **kwargs)
    return decorated_function
