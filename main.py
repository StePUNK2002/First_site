from flask import Flask
from schemas import Settings
from schemas import db
from api import index, registration, login, add_post, exit, like, edit_post, editing_post, delete_post

def nl2br(value):
    return value.replace('\n', '<br>')

def datetimeformat(value, format='%d-%m-%Y'):
    return value.strftime(format)

settings = Settings()
app = Flask(__name__, template_folder='templates')
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{settings.username}:{settings.password}@{settings.db_host}:{settings.port}/{settings.db_name}"
app.jinja_env.filters['nl2br'] = nl2br
app.jinja_env.filters['datetimeformat'] = datetimeformat
db.init_app(app)  # Инициализация объекта db



app.route('/', methods=['GET'])(index)


app.route('/registration', methods=['GET', 'POST'])(registration)


app.route('/login', methods=['GET', 'POST'])(login)


app.route('/add_post', methods=['GET', 'POST'])(add_post)

app.route('/exit', methods=['GET'])(exit)
app.route('/like/<int:post_id_like>', methods=['GET', 'POST'])(like)


app.route('/edit_post/<int:post_id_edit>/<string:post_title>/<string:post_text>', methods=['GET', 'POST'])(edit_post)
app.route('/editing_post', methods=['GET', 'POST'])(editing_post)
app.route('/delete_post/<int:post_id_delete>', methods=['POST','GET'])(delete_post)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
