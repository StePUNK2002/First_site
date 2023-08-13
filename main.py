import sys
import flask
import sqlalchemy
from flask import Flask,request,render_template,url_for,jsonify,redirect,flash
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


#Создаем сущности.
class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    last_name = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100), nullable=True)
    login = db.Column(db.String(20))
    password = db.Column(db.String(20))
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
    posts = Post.query.all()
    return render_template("index.html",posts=posts)

@app.route('/registration', methods=['GET','POST'])
def registration():
    if request.method == 'POST':
        # ...

        # Обработка загруженного изображения
        image = request.files['image']
        avatar = ""
        if image:
            filename = secure_filename(image.filename)
            avatar_folder = 'avatars'  # Относительный путь к папке "avatar"
            image.save(os.path.join(avatar_folder, filename))
            avatar = os.path.join(avatar_folder, filename)
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        middle_name = request.form['middleName']
        login = request.form['login']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        aboutme = request.form['about']

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

        flash('Автор успешно добавлен', 'success')
        return redirect(url_for('index'))
    return render_template('registration.html')


def Test():
    with app.app_context():
        db.create_all() # <--- create db object.
        posts = Author.query.all()
        print(posts)


def Server():
    with app.app_context():
        db.create_all() # <--- create db object.
    app.run(debug=True)

if __name__ == '__main__':
    Server()