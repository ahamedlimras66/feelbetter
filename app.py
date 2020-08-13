import json, os, time
from flask import Flask, render_template, Response, redirect, url_for, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from models.schema import *
from flask_mail import Mail,Message

from flask_login import LoginManager, login_user, login_required, logout_user, current_user



app = Flask(__name__)
app.secret_key = 'my-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'limraslimahamed@gmail.com'
app.config['MAIL_PASSWORD'] = 'Ahamedlimras99.'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.before_first_request
def create_table():
    db.create_all()
    if AdminUser.query.filter_by(username='root').first() is None:
        adminID = AdminUser(username='root',password=generate_password_hash('root', method='sha256'))
        db.session.add(adminID)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
	return AdminUser.query.get(int(user_id))

class MyAdminIndexView(AdminIndexView):
	def is_accessible(self):
		if current_user.is_authenticated:
			return True
	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('login', next=request.url))

class MyModelView(ModelView):
	def is_accessible(self):
		if current_user.is_authenticated:
			return True
	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('login', next=request.url))

class UserAdmin(ModelView):
    def on_model_change(self, form, model, is_created):
        model.password = generate_password_hash(model.password,method='sha256')


admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(UserAdmin(AdminUser, db.session))
admin.add_view(MyModelView(Chat, db.session))
admin.add_view(MyModelView(Guide, db.session))

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/login_check', methods=['POST', 'GET'])
def loginCheck():
    userName = request.form['username']
    password = request.form['password']

    user = AdminUser.query.filter_by(username=userName).first()
    
    if user and check_password_hash(user.password, password):
        login_user(user, remember=False)
        return redirect('admin')
    error = "Incorrect username or password"
    return render_template('login.html',error=error)

@app.route("/")
def home():
    return render_template('home.html')



@app.route("/game")
def game():
    return render_template('game.html')

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/save_chat/<jsdata>")
def save_chat(jsdata):
    data = json.loads(jsdata)

    chat = Chat(name=data['name'], age=data['age'], gender=data['gender'], problem=data['problem'], contact=data['contact'])
    db.session.add(chat)
    db.session.commit()

    for guide in Guide.query.all():
        msg = Message("hello "+ guide.name, sender="arrowmail", recipients=[guide.email])
        msg.html = render_template("guide.html",
                                    name=chat.name,
                                    age=chat.age,
                                    gender=chat.gender,
                                    problem=chat.problem,
                                    contact=chat.contact)
        mail.send(msg)
        time.sleep(2)
    return Response(status=200)



@app.route("/ball")
def ball():
    return render_template('ball.html')

@app.route("/memory")
def memory():
    return render_template('memory.html')

@app.route("/blocking")
def blocking():
    return render_template('blocking.html')

@app.route("/space")
def space():
    return render_template('space.html')

@app.route("/2048")
def game2048():
    return render_template('2048.html')


if __name__ == "__main__":
    from db import db
    db.init_app(app)
    app.run(debug=True)