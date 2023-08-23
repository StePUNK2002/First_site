from schemas import Author, Post, Image, Like, Comment, db
from sqlalchemy import desc
from sqlalchemy import delete

def create_author(first_name, last_name, middle_name, login, password, avatar, aboutme):
    new_author = Author(first_name=first_name, last_name=last_name, middle_name=middle_name, login=login,
                        password=password, avatar=avatar, aboutme=aboutme)

    # Добавление автора в базу данных
    db.session.add(new_author)
    db.session.commit()
    return new_author

def get_authors_logins():
    logins = Author.query.with_entities(Author.login).all()  # Query all the logins from the Author table
    login_list = [login[0] for login in logins]
    return login_list

def get_author_by_login(login):
     return Author.query.filter_by(login=login).first()

def create_post(user_id,time_post, title, text):
    new_post = Post(author_id=user_id, post_date=time_post, title=title, text=text,
                    likes=0)
    db.session.add(new_post)
    db.session.commit()
    return new_post

def get_posts():
    posts = (
        db.session.query(Post)
            .order_by(desc(Post.id))
            .all()
    )
    return posts
def get_posts_with_likes_and_images():
    posts = (
        db.session.query(Post, Image, Author)
            .join(Image, Post.id == Image.post_id, isouter=True)
            .join(Author, Post.author_id == Author.id)
            .all()
    )
    return posts

def get_post_by_id(post_id):
    return Post.query.filter_by(id=post_id).first()

def update_post(post, title=None, text=None, likes=None):
    if title is not None:
        post.title = title
    if text is not None:
        post.text = text
    if likes is not None:
        post.likes = likes
    db.session.commit()


def delete_post(post_id):
    delete_statement = delete(Post).where(Post.id == post_id)
    db.session.execute(delete_statement)
    db.session.commit()

def create_image(path, post_id):
    new_image = Image(path=path, post_id=post_id)
    db.session.add(new_image)
    db.session.commit()
    return new_image

def get_image_by_post_id(post_id):
    return Image.query.filter_by(post_id=post_id).first()

def update_image(image, path):
    image.path = path
    db.session.commit()


def delete_image(post_id):
    image_for_delete = delete(Image).where(Image.post_id == post_id)
    db.session.execute(image_for_delete)
    db.session.commit()
def create_like(user_id, post_id_like):
    like = Like(author_id=user_id, post_id=post_id_like)
    db.session.add(like)
    db.session.commit()
    return like

def get_likes_by_id(post_id_like):
     return Like.query.with_entities(Like.author_id).filter(Like.post_id == post_id_like).all()

def delete_like(user_id, post_id_like):
    delete_like = delete(Like).where(Like.author_id == user_id, Like.post_id == post_id_like)
    db.session.execute(delete_like)
    db.session.commit()
def delete_like_by_post_id(post_id):
    likes_for_delet = delete(Like).where(Like.post_id == post_id)
    db.session.execute(likes_for_delet)
    db.session.commit()

def create_comment(author, text, post):
    comment = Comment(author=author, text=text, post=post)
    db.session.add(comment)
    db.session.commit()
    return comment

def get_comments():
    return Comment.query.all()

def get_comment_by_id(comment_id):
    return Comment.query.get(comment_id)

def update_comment(comment, text):
    comment.text = text
    db.session.commit()

def delete_comment(comment):
    db.session.delete(comment)
    db.session.commit()
