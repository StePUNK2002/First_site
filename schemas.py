from flask_sqlalchemy import SQLAlchemy
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

db = SQLAlchemy()

class Settings(BaseSettings):
    secret_key: str = os.getenv('SECRET_KEY')
    username: str = os.getenv('USERNAME')
    password: str = os.getenv('PASSWORD')
    db_name: str = os.getenv('DB_NAME')
    db_host: str = os.getenv('DB_HOST')
    port: int = os.getenv('PORT')



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
