import re
from flask import request, render_template, url_for, redirect
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import delete
from sqlalchemy import desc
from schemas import Author, Post, Image, Like, db
import uuid
import crud

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


    if post_id_vedro != -1:
        edit_post = True
        print("yes")
        post_id_vedro = -1
        return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                               avatar_path=path, nickname=nickname, add_post=add_post, post_title=post_title_vedro,post_text=post_text_vedro, edit_post=edit_post)
    edit_post = False
    return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                           avatar_path=path, nickname=nickname, add_post=add_post, posts=crud.get_posts(), edit_post=edit_post)
def registration():
    show_banner = False
    global edit_post
    edit_post = False
    global is_be
    global is_login
    global is_registration
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

        if login in crud.get_authors_logins():
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
        crud.create_author(first_name=first_name, last_name=last_name, middle_name=middle_name, login=login,
                            password=password, avatar=avatar, aboutme=aboutme)
        succes = True
    else:
        is_registration = True
        is_login = False
    return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be, succes=succes)


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
        user = crud.get_author_by_login(login)
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
                global image_avatar
                image_avatar = path
                return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                                       avatar_path=path, nickname=user.login, posts=crud.get_posts())
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

        return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                               avatar_path=f'../{path}', posts=crud.get_posts_with_likes_and_images())
    else:

        return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be)
def add_post():
    global edit_post
    edit_post = False
    global is_be
    global is_login
    global is_registration
    global add_post
    is_registration = False
    is_login = False
    add_post = True
    if request.method == "POST":
        user_id = crud.get_author_by_login(login=nickname).id
        title = request.form['post-heading']
        text = request.form['post-content']
        time_post = datetime.now().date()
        print(time_post)
        new_post = crud.create_post(user_id=user_id,time_post=time_post, title=title, text=text)
        image_for_post = request.files['image']
        if image_for_post:

            filename = secure_filename(image_for_post.filename)
            file_extension = os.path.splitext(filename)[1]
            random_filename = str(uuid.uuid4()) + file_extension
            random_filename = secure_filename(random_filename)
            image_folder = 'static/images'
            image_for_post.save(os.path.join(image_folder, random_filename))
            post_image = random_filename
            crud.create_image(path=post_image, post_id=new_post.id)
        added = True
        add_post = True
        return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                               avatar_path=path, nickname=nickname, add_post=add_post, added=added)

    return render_template('index.html', is_login=is_login, is_registration=is_registration, is_be=is_be,
                           avatar_path=path, nickname=nickname, add_post=add_post)
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
    ids = crud.get_likes_by_id(post_id_like=post_id_like)
    id_list = [id[0] for id in ids]
    print(id_list)
    if user_id in id_list:
        print("Лайк есть")
        edit_like_post = crud.get_post_by_id(post_id=post_id_like)
        crud.update_post(post=edit_like_post, likes=edit_like_post.likes - 1)
        crud.delete_like(user_id=user_id, post_id_like=post_id_like)
    else:
        print("Лайка нет")
        crud.create_like(user_id=user_id, post_id_like=post_id_like)
        edit_like_post = crud.get_post_by_id(post_id=post_id_like)
        crud.update_post(post=edit_like_post, likes=edit_like_post.likes +1)
    return redirect(url_for('index'))
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
def editing_post():
    title = request.form['post-heading']
    text = request.form['post-content']
    image_for_post = request.files['image']
    global post_id_vedro
    if image_for_post:
        if image_for_post:
            past_image = crud.get_image_by_post_id(post_id=post_id_vedro_2)
            if past_image == None:
                filename = secure_filename(image_for_post.filename)
                file_extension = os.path.splitext(filename)[1]
                random_filename = str(uuid.uuid4()) + file_extension
                random_filename = secure_filename(random_filename)
                image_folder = 'static/images'
                image_for_post.save(os.path.join(image_folder, random_filename))
                post_image = random_filename
                crud.create_image(path=post_image, post_id=post_id_vedro_2)
            else:
                path_image_for_delete = crud.get_image_by_post_id(post_id=post_id_vedro_2).path
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
                crud.update_image(image=past_image, path=post_image)
    post = crud.get_post_by_id(post_id=post_id_vedro_2)
    crud.update_post(post=post, title=title, text=text)
    print(post)
    return redirect(url_for('index'))
def delete_post(post_id_delete):
    try:
        path_image_for_delete = crud.get_image_by_post_id(post_id=post_id_delete).path
        full_path = os.path.join(folder_image_post, path_image_for_delete)
        if os.path.exists(full_path):
            # Удаляем изображение
            os.remove(full_path)
    except:
        pass
    #лайки, изображение, пост
    crud.delete_like_by_post_id(post_id=post_id_delete)
    crud.delete_image(post_id=post_id_delete)
    crud.delete_post(post_id=post_id_delete)
    return redirect(url_for('index'))