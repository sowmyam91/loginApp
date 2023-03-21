########################################################################################
######################          Import packages      ###################################
########################################################################################


from flask import Blueprint, render_template, flash, request
from flask_login import login_required, current_user
from __init__ import create_app, db
from auth import require_api_token
########################################################################################
# our main blueprint
main = Blueprint('main', __name__)


@main.route('/')  # home page that return 'index'
def index():
    return render_template('index.html')


# @main.route('/profile', defaults={'name': 'login'})
@main.route('/profile')  # profile page that return 'profile'
@login_required
def profile():
    return render_template('profile.html')


app = create_app()  # we initialize our flask pyapp using the __init__.py function
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # create the SQLite database
    app.run(debug=True)  # run the flask app on debug mode
