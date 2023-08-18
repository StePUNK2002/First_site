import re
from flask import Flask, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import delete
import uuid

def nl2br(value):
    return value.replace('\n', '<br>')

def datetimeformat(value, format='%d-%m-%Y'):
    return value.strftime(format)
# TODO Сделать кастом для изображений постов с удалением файлов(необязателно).
# TODO Сделать лайки.
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'thisissecret'
username = "newuser"
password = "password"
dbname = "test"
#Название контейнера в докере
db_host = "db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{username}:{password}@{db_host}:5432/{dbname}"
app.jinja_env.filters['nl2br'] = nl2br
app.jinja_env.filters['datetimeformat'] = datetimeformat
db = SQLAlchemy(app)
#TODO Заменить на сессии
#session.get('post_id_vedro')
is_login = False
is_registration = False
is_be = False
add_post = False
edit_post = False
folder = os.path.join('static', 'avatars')
folder_image_post = os.path.join('static', 'images')
path = os.path.join(folder, "default_user.jpg")
nickname = ''
user_id = -1


post_title_vedro = ''
post_text_vedro = ''
post_id_vedro = -1
post_id_vedro_2 = -1

def check_login_password(login):
    pattern = r'^[a-zA-Z][a-zA-Z0-9]{5,}$'
    match = re.match(pattern, login)
    if match:
        return True
    return False


# Создаем сущности.
class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    last_name = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100), nullable=True)
    login = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(40))
    avatar = db.Column(db.String, nullable=True)
    aboutme = db.Column(db.String(500))


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    author = db.relationship('Author', backref='posts')
    post_date = db.Column(db.DateTime)
    title = db.Column(db.String(120))
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


@app.route('/', methods=['GET'])
def index():
    global is_be
    global is_login
    global is_registration
    global add_post
    global edit_post
    global post_id_vedro
    edit_post = False
    is_login = False
    is_registration = False
    add_post = False
    from sqlalchemy import desc

    posts = (
        db.session.query(Post)
            .order_by(desc(Post.id))
            .all()
    )

    if post_id_vedro != -1:
        edit_post = True
        print("yes")
        post_id_vedro = -1
        return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                               avatar_path=path, nickname=nickname, add_post=add_post, post_title=post_title_vedro,post_text=post_text_vedro, edit_post=edit_post)
    edit_post = False
    return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                           avatar_path=path, nickname=nickname, add_post=add_post, posts=posts, edit_post=edit_post)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    show_banner = False
    duplicate_login = False
    global edit_post
    edit_post = False
    global is_be
    global is_login
    global is_registration
    in_bd = False
    succes = False
    if request.method == 'POST':
        # Обработка загруженного изображения
        image = request.files['image']
        avatar = "default_user.jpg"
        if image:
            filename = secure_filename(image.filename)
            file_extension = os.path.splitext(filename)[1]
            random_filename = str(uuid.uuid4()) + file_extension
            random_filename = secure_filename(random_filename)
            avatar_folder = 'static/avatars'  # Относительный путь к папке "avatar"
            image.save(os.path.join(avatar_folder, random_filename))
            avatar = random_filename
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
            in_bd = True
            return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                                   succes=succes, in_bd=in_bd)
        if check_login_password(login) == False or check_login_password(password) == False:
            show_banner = True
            return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                                   show_banner=show_banner)

        # Проверка совпадения пароля и повторения пароля
        if password != confirm_password:
            error = 'Пароли не совпадают 😔!'
            return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                                   show_banner=show_banner, error=error)
        # Создание новой сущности Author
        new_author = Author(first_name=first_name, last_name=last_name, middle_name=middle_name, login=login,
                            password=password, avatar=avatar, aboutme=aboutme)

        # Добавление автора в базу данных
        db.session.add(new_author)
        db.session.commit()
        succes = True
    else:
        is_registration = True
        is_login = False
    return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be, succes=succes)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global is_be
    global is_login
    global is_registration
    global nickname
    global edit_post
    edit_post = False
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
                global user_id
                is_registration = False
                is_login = False
                is_be = True
                global path
                print(user.avatar)
                path = os.path.join(folder, user.avatar)
                nickname = user.login
                user_id = user.id
                posts = Post().query.all()
                global image_avatar
                image_avatar = path
                return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                                       avatar_path=path, nickname=user.login, posts=posts)
            else:
                print("Пароль не подходит")
                return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                                       not_people=True)

        else:
            # User does not exist
            print("Нет такого....")
            return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                                   not_people=True)

    else:
        is_login = True
        is_registration = False
    if is_be:
        #query = db.session.query(Post, Image).join(Image, Post.id == Image.post_id, isouter=True)

        # Выполняем запрос и получаем результат
        #posts = query.all()
        #print(posts)
        posts = (
            db.session.query(Post, Image, Author)
                .join(Image, Post.id == Image.post_id, isouter=True)
                .join(Author, Post.author_id == Author.id)
                .all()
        )

        return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                               avatar_path=f'../{path}', posts=posts)
    else:

        return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be)


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    global edit_post
    edit_post = False
    global is_be
    global is_login
    global is_registration
    global add_post
    is_registration = False
    is_login = False
    added = False
    add_post = True
    if request.method == "POST":
        user_id = Author.query.filter_by(login=nickname).first().id
        title = request.form['post-heading']
        text = request.form['post-content']
        time_post = datetime.now().date()
        new_post = Post(author_id=user_id, post_date=time_post, title=title, text=text,
                        likes=0)
        db.session.add(new_post)
        db.session.commit()
        image_for_post = request.files['image']
        if image_for_post:

            filename = secure_filename(image_for_post.filename)
            file_extension = os.path.splitext(filename)[1]
            random_filename = str(uuid.uuid4()) + file_extension
            random_filename = secure_filename(random_filename)
            image_folder = 'static/images'
            image_for_post.save(os.path.join(image_folder, random_filename))
            post_image = random_filename
            new_image = Image(path=post_image, post_id=new_post.id)
            db.session.add(new_image)
            db.session.commit()
        added = True
        add_post = True
        return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                               avatar_path=path, nickname=nickname, add_post=add_post, added=added)

    return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                           avatar_path=path, nickname=nickname, add_post=add_post)


@app.route('/exit', methods=['GET'])
def exit():
    global edit_post
    edit_post = False
    global is_be
    global is_login
    global is_registration
    global add_post
    is_be = False
    is_login = False
    is_registration = False
    add_post = False
    return render_template('index.html', is_login=is_login, is_registration=is_registration, add_post=add_post)
@app.route('/like/<int:post_id_like>', methods=['GET', 'POST'])
def like(post_id_like):
    global edit_post
    edit_post = False
    global is_be
    global is_login
    global is_registration
    global add_post
    is_login = False
    is_registration = False
    add_post = False
    ids = Like.query.with_entities(Like.author_id).filter(Like.post_id == post_id_like).all()  # Query all the logins from the Author table
    id_list = [id[0] for id in ids]
    print(id_list)
    if user_id in id_list:
        print("Лайк есть")
        edit_like_post = Post.query.filter_by(id=post_id_like).first()
        edit_like_post.likes = edit_like_post.likes - 1
        delete_like = delete(Like).where(Like.author_id == user_id, Like.post_id == post_id_like)
        db.session.execute(delete_like)
        db.session.commit()
    else:
        print("Лайка нету")
        create_like = Like(author_id=user_id, post_id=post_id_like)
        edit_like_post = Post.query.filter_by(id=post_id_like).first()
        edit_like_post.likes = edit_like_post.likes + 1
        db.session.add(create_like)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit_post/<int:post_id_edit>/<string:post_title>/<string:post_text>', methods=['GET', 'POST'])
def edit_post(post_id_edit, post_title, post_text):
    global edit_post
    edit_post = True
    global post_title_vedro
    global post_text_vedro
    global post_id_vedro
    global post_id_vedro_2
    post_title_vedro = post_title
    post_text_vedro = post_text
    post_id_vedro = post_id_edit
    post_id_vedro_2 = post_id_vedro
    return redirect(url_for('index'))
@app.route('/editing_post', methods=['GET', 'POST'])
def editing_post():
    title = request.form['post-heading']
    text = request.form['post-content']
    image_for_post = request.files['image']
    global post_id_vedro
    if image_for_post:
        if image_for_post:
            past_image = Image.query.filter_by(post_id=post_id_vedro_2).first()
            if past_image == None:
                filename = secure_filename(image_for_post.filename)
                file_extension = os.path.splitext(filename)[1]
                random_filename = str(uuid.uuid4()) + file_extension
                random_filename = secure_filename(random_filename)
                image_folder = 'static/images'
                image_for_post.save(os.path.join(image_folder, random_filename))
                post_image = random_filename
                new_image = Image(path=post_image, post_id=post_id_vedro_2)
                db.session.add(new_image)
                db.session.commit()
            else:
                path_image_for_delete = Image().query.filter_by(post_id=post_id_vedro_2).first().path
                full_path = os.path.join(folder_image_post, path_image_for_delete)
                if os.path.exists(full_path):
                    # Удаляем изображение
                    os.remove(full_path)
                filename = secure_filename(image_for_post.filename)
                file_extension = os.path.splitext(filename)[1]
                random_filename = str(uuid.uuid4()) + file_extension
                random_filename = secure_filename(random_filename)
                image_folder = 'static/images'
                image_for_post.save(os.path.join(image_folder, random_filename))
                post_image = random_filename
                past_image.path = post_image
                db.session.commit()
    post = Post.query.filter_by(id=post_id_vedro_2).first()
    post.title = title
    post.text = text
    db.session.commit()
    print(post)
    return redirect(url_for('index'))
@app.route('/delete_post/<int:post_id_delete>', methods=['POST','GET'])
def delete_post(post_id_delete):
    likes_for_delet = delete(Like).where(Like.post_id == post_id_delete)
    delete_statement = delete(Post).where(Post.id == post_id_delete)
    image_for_delete = delete(Image).where(Image.post_id == post_id_delete)
    try:
        path_image_for_delete = Image().query.filter_by(post_id=post_id_delete).first().path
        full_path = os.path.join(folder_image_post, path_image_for_delete)
        if os.path.exists(full_path):
            # Удаляем изображение
            os.remove(full_path)
        db.session.execute(image_for_delete)
    except:
        pass
    db.session.execute(likes_for_delet)
    db.session.execute(delete_statement)
    db.session.commit()
    return redirect(url_for('index'))


def Server():
    with app.app_context():
        db.create_all()
    #app.run(debug=True)
    app.run(debug=False)


if __name__ == '__main__':
    Server()
