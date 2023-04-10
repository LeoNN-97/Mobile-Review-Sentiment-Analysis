from flask import Flask,session,request,redirect,flash,render_template,url_for
from flask_login import login_user,login_required, logout_user, current_user,LoginManager
from models import *

app = Flask(__name__,template_folder='templates')
app.config['SECRET_KEY']="mysecretkey"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))