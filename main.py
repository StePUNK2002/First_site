import re
from flask import Flask,request,render_template,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
def nl2br(value):
    return value.replace('\n', '<br>')
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'thisissecret'
# our database uri
username = "newuser"
password = "password"
dbname = "test"
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{username}:{password}@localhost:5432/{dbname}"
app.jinja_env.filters['nl2br'] = nl2br
db = SQLAlchemy(app)
is_login = False
is_registration = False
is_be = False
folder = os.path.join('static', 'avatars')
path = os.path.join(folder, "default_user")
nickname = ''



def check_login_password(login):
    pattern =  r'^[a-zA-Z][a-zA-Z0-9]{5,}$'
    match = re.match(pattern, login)
    if match:
        return True
    return False

#Создаем сущности.
class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    last_name = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100), nullable=True)
    login = db.Column(db.String(20),unique=True)
    password = db.Column(db.String(40))
    avatar = db.Column(db.String, nullable=True)
    aboutme = db.Column(db.String(500))

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    author = db.relationship('Author', backref='posts')
    post_date = db.Column(db.DateTime)
    title = db.Column(db.String(20))
    text = db.Column(db.String(140))
    likes = db.Column(db.Integer)
class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    post = db.relationship('Post', backref='images')

class Like(db.Model):
    __tablename__ = 'likes_post'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author = db.relationship('Author', backref='likes_post')
    post = db.relationship('Post', backref='likes_post')

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    text = db.Column(db.String(140))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author = db.relationship('Author', backref='comments')
    post = db.relationship('Post', backref='comments')

@app.route('/',methods=['GET'])
def index():
    global is_be
    global is_login
    global is_registration
    global path
    return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                           avatar_path=path, nickname=nickname)
@app.route('/registration', methods=['GET','POST'])
def registration():
    show_banner = False
    duplicate_login = False
    global is_be
    global is_login
    global is_registration
    if request.method == 'POST':
        # Обработка загруженного изображения
        image = request.files['image']
        avatar = "default_user"
        if image:
            filename = secure_filename(image.filename)
            avatar_folder = 'static/avatars'  # Относительный путь к папке "avatar"
            image.save(os.path.join(avatar_folder, filename))
            avatar = secure_filename(image.filename)
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        middle_name = request.form['middleName']
        login = request.form['login']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        aboutme = request.form['about']

        logins = Author.query.with_entities(Author.login).all()  # Query all the logins from the Author table
        login_list = [login[0] for login in logins]  # Extract the logins and store them in a list
        if login in login_list:
            return render_template('registration.html', show_banner=show_banner)
        if check_login_password(login) == False or check_login_password(password) == False:
            show_banner = True
            return render_template('registration.html', show_banner=show_banner)

        # Проверка совпадения пароля и повторения пароля
        if password != confirm_password:
            error = 'Пароли не совпадают 😔!'
            return render_template('registration.html', error=error)
        # Создание новой сущности Author
        new_author = Author(first_name=first_name, last_name=last_name, middle_name=middle_name, login=login,
                            password=password, avatar=avatar,aboutme=aboutme)

        # Добавление автора в базу данных
        db.session.add(new_author)
        db.session.commit()
    else:
        is_registration = True
        is_login = False
    return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be)

@app.route('/login', methods=['GET','POST'])
def login():
    global is_be
    global is_login
    global is_registration
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        user = Author.query.filter_by(login=login).first()
        if user:
            if user.password == password:
                print("Все верно")
                global is_be
                global is_login
                global is_registration
                is_registration = False
                is_login = False
                is_be = True
                global path
                print(user.avatar)
                path = os.path.join(folder, user.avatar)
                global nickname
                nickname = user.login
                return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be, avatar_path=path, nickname=user.login)
            else:
                print("Пароль не подходит")
                return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be, show_banner=True)

        else:
            # User does not exist
            print("Нет такого....")
            return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be, show_banner=True)

    else:
        is_login = True
        is_registration = False
    if is_be:
        return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be, vatar_path=f'../{path}')
    else:
        return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be)
def Test():
    with app.app_context():
        db.create_all() # <--- create db object.
        posts = Author.query.all()
        print(posts)


def Server():
    with app.app_context():
        db.create_all() # <--- create db object.
    app.run(debug=True)
    #app.run(debug=False)

if __name__ == '__main__':
    Server()