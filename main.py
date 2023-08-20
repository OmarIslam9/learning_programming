import os
import random
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import logout_user, current_user, UserMixin, login_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import datetime

from werkzeug.utils import secure_filename

app=Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # Check if user is in paid_user table
    user = users.query.get(int(user_id))
    if user:
        return user
    # If not, check if user is in free_user table

    # If user is not in either table, return None
    return None

with app.app_context():
    class users(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100))
        age = db.Column(db.String(100))
        email = db.Column(db.String(100))
        password = db.Column(db.String(100))
        learned = db.Column(db.String(1000))
        photo_filename = db.Column(db.String(1000))
        date_added = db.Column(db.Date, default=datetime.date.today)

        def save_profile_photo(self, photo_file):
            """
            Saves the user's profile photo to the uploads folder
            and updates the user's photo filename in the database.
            """
            # Get the uploads folder path
            uploads_folder = os.path.join(os.getcwd(), 'static', 'uploads')

            # Create the uploads folder if it doesn't exist
            if not os.path.exists(uploads_folder):
                os.makedirs(uploads_folder)

            # Save the photo file to the uploads folder with a unique filename
            photo_filename = f"{self.id}_{photo_file.filename}"
            photo_path = os.path.join(uploads_folder, photo_filename)
            photo_file.save(photo_path)

            # Update the user's photo filename in the database
            self.photo_filename = photo_filename
            db.session.commit()
    db.create_all()


class MyModelView(ModelView):
    def is_accessible(self):
            return True
admin = Admin(app)
admin.add_view(MyModelView(users, db.session))





@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Assuming 'users' is the class representing your user table
        user = users.query.filter_by(email=email).first()

        if not user:
            flash("This email does not exist, try again")
        elif not check_password_hash(user.password, password):
            flash("Incorrect password, try again")
        else:
            login_user(user)
            return redirect("/profile")  # Redirect to the profile page after successful login

    return render_template("login.html", logged_in_user=current_user)


@app.route("/profile")
def profile():
    if current_user.is_authenticated:
        # Fetch the user details from the logged-in user object or database
        user_details = {
            'name': current_user.name,
            'email': current_user.email,
            'age': current_user.age,
            'image': current_user.photo_filename
            # Add any other required details
        }
        return render_template("logged.html", logged_in_user=current_user, user_details=user_details)
    else:
        return redirect("/login")  # Redirect to the login page if the user is not authenticated


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if users.query.filter_by(email=request.form.get('email')).first():
            flash("You have already signed up with this email. Please log in instead.")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )

        new_user = users(
            name=request.form.get('name'),
            age=request.form.get('age'),
            email=request.form.get('email'),
            password=hash_and_salted_password,
            date_added=datetime.date.today(),
            learned=request.form.get('learned')
        )

        db.session.add(new_user)
        db.session.commit()

        if 'profile_photo' in request.files:
            photo_file = request.files['profile_photo']
            new_user.save_profile_photo(photo_file)

        return redirect("/login")

    # Handle GET request
    return render_template("register.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
def start():
    return render_template("start.html", logged_in_user=current_user)

@app.route('/quiz1')
def quiz1():
    questions = [
        {
            'question': 'Question 1: What is the output of the following code snippet?\n\nx = 5\ny = 2\nresult = x % y\nprint(result)',
            'choices': ['A) 1', 'B) 2', 'C) 3', 'D) 0'],
        },
        {
            'question': 'Question 2: Which of the following is NOT a programming language?',
            'choices': ['A) Python', 'B) HTML', 'C) Java', 'D) CSS'],
        },
        {
            'question': 'Question 3: What does the acronym "OOP" stand for in programming?',
            'choices': ['A) Object-Oriented Programming', 'B) Object-Oriented Protocol', 'C) Object-Oriented Processor', 'D) Object-Oriented Practice'],
        },
        {
            'question': 'Question 4: What is the purpose of a loop in programming?',
            'choices': ['A) To store data temporarily', 'B) To perform repetitive tasks', 'C) To display error messages', 'D) To execute conditionally'],
        },
    ]
    return render_template('quiz.html', questions=questions, logged_in_user=current_user)

# @app.route('/quiz2')
# def quiz2():
#     questions = [
#         {
#             'question': 'Question 1: What is the correct syntax to declare a variable in JavaScript?',
#             'choices': ['A) var x;', 'B) variable x;', 'C) x = 5;', 'D) int x;'],
#         },
#         {
#             'question': 'Question 2: Which of the following is a Python framework for web development?',
#             'choices': ['A) Django', 'B) React', 'C) Ruby on Rails', 'D) Laravel'],
#         },
#         {
#             'question': 'Question 3: What does CSS stand for in web development?',
#             'choices': ['A) Cascading Style Sheets', 'B) Computer Style Sheets', 'C) Creative Style Sheets', 'D) Custom Style Sheets'],
#         },
#         {
#             'question': 'Question 4: What is the purpose of the "git clone" command in Git?',
#             'choices': ['A) To create a new repository', 'B) To commit changes to the repository', 'C) To clone a remote repository', 'D) To merge branches in the repository'],
#         },
#     ]
#     return render_template('quiz.html', questions=questions, logged_in_user=current_user)
#
#
# @app.route('/quiz3')
# def quiz3():
#     questions = [
#         {
#             'question': 'Question 1: What is the output of the following code snippet in C++?\n\n#include <iostream>\nusing namespace std;\n\nint main() {\n  int x = 5;\n  cout << x << endl;\n  return 0;\n}',
#             'choices': ['A) 5', 'B) 0', 'C) Garbage value', 'D) Compilation error'],
#         },
#         {
#             'question': 'Question 2: Which programming language is used for developing Android applications?',
#             'choices': ['A) Java', 'B) Python', 'C) C#', 'D) Swift'],
#         },
#         {
#             'question': 'Question 3: What does SQL stand for in database management?',
#             'choices': ['A) Structured Query Language', 'B) Sequential Query Language', 'C) Semantic Query Language', 'D) System Query Language'],
#         },
#         {
#             'question': 'Question 4: What is the purpose of the "sudo" command in Linux?',
#             'choices': ['A) To delete files', 'B) To create new directories', 'C) To switch to the root user', 'D) To install software packages'],
#         },
#     ]
#     return render_template('quiz.html', questions=questions, logged_in_user=current_user)

@app.route('/quiz_result', methods=['POST'])
def quiz_result():
    score = 0

    # Get the user's answers from the submitted form
    user_answers = [request.form.get(f'answer{i}') for i in range(1, 5)]  # Assuming 4 questions
    print(user_answers)

    # Calculate the score for Quiz 1 based on the correct answers
    correct_answers_quiz1 = ['D', 'B', 'A', 'B']  # Assuming the correct answers for Quiz 1
    score_quiz1 = sum(answer == correct for answer, correct in zip(user_answers, correct_answers_quiz1))
    score += score_quiz1

    # Similarly, calculate the score for Quiz 2 and Quiz 3
    # correct_answers_quiz2 = [...]  # Insert the correct answers for Quiz 2
    # score_quiz2 = sum(answer == correct for answer, correct in zip(user_answers,

    # Return a response indicating the user's score
    return f"Your score is: {score} out of 4."  # Modify the message as per your requirements


# @app.route('/submit_test', methods=['POST'])
# def submit_test():
#     # Get the selected answers from the form submission
#     answer1 = request.form.get('answer1')
#     answer2 = request.form.get('answer2')
#     answer3 = request.form.get('answer3')
#     answer4 = request.form.get('answer4')
#
#     # Compare the selected answers with the correct answers
#     correct_answers = {
#         'question1': 'C',
#         'question2': 'A',
#         'question3': 'A',
#         'question4': 'A'
#     }
#
#     score = 0
#
#     if answer1 == correct_answers['question1']:
#         score += 1
#
#     if answer2 == correct_answers['question2']:
#         score += 1
#
#     if answer3 == correct_answers['question3']:
#         score += 1
#
#     if answer4 == correct_answers['question4']:
#         score += 1
#
#     return render_template('result.html', score=score, logged_in_user=current_user)




















if __name__==("__main__"):
    app.run(debug=True)