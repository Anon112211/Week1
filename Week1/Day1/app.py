from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# SQLAlchemy setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload config
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

# Create upload folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- User Model ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    bday = db.Column(db.String(), nullable=False)
    address = db.Column(db.String(), nullable=False)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    image = db.Column(db.String(), nullable=True)

# --- Helper Function ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        bday = request.form['bday']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']
        image_file = request.files['image']

        image_filename = None
        if image_file and allowed_file(image_file.filename):
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

        # Create user object
        user = User(name=name, bday=bday, address=address, username=username, password=password, image=image_filename)

        try:
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for('login'))
        except:
            db.session.rollback()
            flash("Username already exists.", "danger")

    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            return redirect(url_for('profile'))
        else:
            flash("Invalid username or password.", "danger")

    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if user:
        return render_template('profile.html', name=user.name, bday=user.bday, address=user.address, image=user.image)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Run ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
