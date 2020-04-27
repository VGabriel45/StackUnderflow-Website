from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, logout_user, login_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

response_like = 0
question_like = 0


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    question = db.relationship('Question', backref='user')


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    likes = db.relationship('Likes', backref='question')
    responses = db.relationship('Response', backref='question')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    response = db.Column(db.Text(), nullable=True)
    author = db.Column(db.String(100), nullable=False)
    likes = db.relationship('Likes', backref='response')
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    number_of_likes = db.Column(db.Integer, nullable=True)
    response_id = db.Column(db.Integer, db.ForeignKey('response.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))


@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        author = request.form['author']
        new_question = Question(
            title=title, description=description, author=author)
        db.session.add(new_question)
        db.session.commit()
        print('Added')
        return redirect('/')
    else:
        all_questions = Question.query.all()
        all_responses = Response.query.all()
        all_users = User.query.all()
        return render_template('index.html', all_questions=all_questions, all_responses=all_responses, all_users=all_users)


@app.route('/ask-question', methods=['GET', 'POST'])
def ask():
    return render_template('form.html')


@app.route('/respond-question/<id>', methods=['GET', 'POST'])
def respond_to_question(id):
    question = Question.query.get_or_404(id)
    if request.method == 'POST':
        response = request.form['response']
        author = request.form['author']
        new_response = Response(
            response=response, author=author, question=question)
        db.session.add(new_response)
        db.session.commit()
        return redirect(f'/respond-question/{id}')
    else:
        return render_template('respond.html', question=question)


@app.route('/like-question/<id>')
def like_question(id):
    global question_like
    question = Question.query.get_or_404(id)
    question_like += 1
    Likes(number_of_likes=question_like, question=question)
    db.session.commit()
    return redirect(request.referrer)


@app.route('/like-response/<id>')
def like_response(id):
    global response_like
    response = Response.query.get_or_404(id)
    response_like += 1
    Likes(number_of_likes=response_like, response=response)
    db.session.commit()
    return redirect(request.referrer)


@app.route('/delete-response/<id>')
def delete_response(id):
    response = Response.query.get_or_404(id)
    db.session.delete(response)
    db.session.commit()
    return redirect(request.referrer)


@app.route('/delete-question/<id>')
def delete_question(id):
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    return redirect(request.referrer)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect('/register')
        new_user = User(username=username, email=email,
                        password=generate_password_hash(password, method='sha256'))

        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    else:
        return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect('/login')
        return redirect('/')
    else:
        all_users = User.query.all()
        return render_template('login.html', all_users=all_users)


@app.route('/logout', methods=["GET"])
def logout():
    return 'You have been logged out!'


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    debug = True
    app.run()
