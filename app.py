from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import pymysql
from flask_cors import CORS
import requests
import openai
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import cv2
import os
import numpy as np
from werkzeug.utils import secure_filename
from io import BytesIO
import base64

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Database configuration
db_user = "root"
db_password = ""
db_name = "users_db"
db_connection_name = "localhost"

# Database configuration for python
#db_user = "appl3m4n"
#db_password = "romanroman"
#db_name = "appl3m4n$users_db"
#db_connection_name = "appl3m4n.mysql.pythonanywhere-services.com"

app.config['SECRET_KEY'] = 'thisisasecretkey'
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Replace with your OpenAI API key
str1 = "sk-proj-VZeebfbISGNPnpTyL_jfGEhDiFZLm7nxC7-"
str2 = "jxzicheaKb2uff_ch6OniIlM0HXuSGuLT_k1LxfT3BlbkFJvrXO_"
str3 = "ditN99xACAqJ_ifMX8_OkVNhQM2IXEqMY_"
str4 = "a6jPViBTHVv9d8Uv7_DMapROEnk9ET30wUA"

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        # Get the conversation data from the frontend
        data = request.json
        messages = data.get("messages", [])
        
        # Make a request to the OpenAI API
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {str1+str2+str3+str4}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-3.5-turbo",  # Use "gpt-4" if required
                "messages": messages,
            },
        )

        # Parse and return the API response
        response_data = response.json()
        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/full_conversation', methods=['POST'])
def full_conversation():
    try:
        # Get the conversation messages from the request
        data = request.json
        messages = data.get("messages", [])
        
        if not messages:
            return jsonify({"error": "No messages provided"}), 400
        
        # Add an initial message to set the tone for the chatbot
        messages.insert(0, {
            "role": "system", 
            "content": "You are a tinder bot who is representing me. You are a funny, charming, and romantic chatbot who loves making people smile. Your task is to keep the conversation lighthearted, funny, and sweet. Keep it romantic and fun, especially if the user is talking to someone special. Respond in a playful and loving tone."
        })

        # Log the conversation messages to check if they are received correctly
        print("Received messages:", messages)

        # Send request to OpenAI API using requests
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {str1+str2+str3+str4}",  # Construct the API key here
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-3.5-turbo",  # Use your desired model
                "messages": messages,
            }
        )

        # Parse and return the API response
        response_data = response.json()
        print("OpenAI response:", response_data)

        return jsonify(response_data)
    
    except Exception as e:
        print("Error:", str(e))  # Log the error for debugging
        return jsonify({"error": str(e)}), 500

# Helper function to get database connection
def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',
        user=db_user,
        password=db_password,
        db=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM login WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
        if user_data:
            return User(user_data['id'], user_data['username'], user_data['password'])
    finally:
        connection.close()
    return None

# RegisterForm class
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM login WHERE username = %s", (username.data,))
                existing_user = cursor.fetchone()
            if existing_user:
                raise ValidationError('That username already exists. Please choose a different one.')
        finally:
            connection.close()

# LoginForm class
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

# Routes
@app.route('/')
def index():
    # Connect to the database
    connection = get_db_connection()
    views = 0
    try:
        with connection.cursor() as cursor:
            # Retrieve current views
            cursor.execute("SELECT count FROM page_views WHERE id = 1")
            result = cursor.fetchone()
            if result:
                views = result['count']
            
            # Increment the views count
            cursor.execute("UPDATE page_views SET count = count + 1 WHERE id = 1")
            connection.commit()
    finally:
        connection.close()

    return render_template('index_open.html', views=views)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None  # Variable to store the error message
    if request.method == 'POST':  # Check if the form is submitted
        username = form.username.data
        password = form.password.data

        # Custom validation for username and password length
        if len(username) < 4:
            error = "Username must be at least 4 characters long."
        elif len(password) < 8:
            error = "Password must be at least 8 characters long."
        else:
            connection = get_db_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM login WHERE username = %s", (username,))
                    user_data = cursor.fetchone()
                if user_data and bcrypt.check_password_hash(user_data['password'], password):
                    user = User(user_data['id'], user_data['username'], user_data['password'])
                    login_user(user)
                    return redirect(url_for('index'))
                else:
                    error = "Invalid username or password."
            finally:
                connection.close()

    return render_template('login.html', form=form, error=error)



@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    error = None  # Variable to store the error message
    if request.method == 'POST':  # Check if the form is submitted
        username = form.username.data
        password = form.password.data

        # Debugging: Print inputs
        print(f"Username: {username}, Password: {password}")

        # Custom validation for username and password length
        if len(username) < 4:
            error = "Username must be at least 4 characters long."
        elif len(password) < 8:
            error = "Password must be at least 8 characters long."
        else:
            connection = get_db_connection()
            try:
                with connection.cursor() as cursor:
                    # Check if the username already exists
                    cursor.execute("SELECT * FROM login WHERE username = %s", (username,))
                    existing_user = cursor.fetchone()
                    if existing_user:
                        error = "That username already exists. Please choose a different one."
                    else:
                        # Hash the password and save the user in the database
                        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                        cursor.execute("INSERT INTO login (username, password) VALUES (%s, %s)", (username, hashed_password))
                        connection.commit()
                        print("User successfully registered!")  # Debugging
                        return redirect(url_for('login'))
            finally:
                connection.close()
        print(f"Error: {error}")  # Debugging
    return render_template('register.html', form=form, error=error)

@app.route('/option1')
def option1():
    return render_template('option1.html', current_user=current_user)

@app.route('/option2')
def option2():
    return render_template('option2.html', current_user=current_user)

@app.route('/option3')
def option3():
    return render_template('option3.html', current_user=current_user)

@app.route('/option4')
def option4():
    return render_template('option4.html', current_user=current_user)

@app.route('/option5')
def option5():
    return render_template('option5.html', current_user=current_user)

@app.route('/chat1.html')
@login_required
def chat1():
    return render_template('chat1.html', current_user=current_user)

@app.route('/chat2.html')
@login_required
def chat2():
    return render_template('chat2.html', current_user=current_user)

@app.route('/chat3.html')
@login_required
def chat3():
    return render_template('chat3.html', current_user=current_user)

@app.route('/subscribe', methods=['POST'])
@login_required
def subscribe():
    # Handle the payment and subscription logic here (e.g., integrate with a payment gateway)
    
    # For now, we simulate a successful payment process
    # You can integrate with a payment API like Stripe, PayPal, etc.
    
    # For this example, assume the payment is successful
    flash("Payment successful! You are now subscribed.", "success")
    
    # After the subscription, you can redirect the user to the main page or a new page
    return redirect(url_for('index'))

# face detect
# Set up upload folder and allowed file extensions
# Allowed file extensions
# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Upload folder for storing uploaded images
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load the pre-trained Haar Cascade model for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Check if file has allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to handle the upload of multiple images
@app.route('/upload', methods=['POST'])
def upload_files():
    if 'images' not in request.files:
        return jsonify({"error": "No images part in the request."}), 400

    files = request.files.getlist('images')
    
    if len(files) < 2 or len(files) > 6:
        return jsonify({"error": "Please upload between 2 and 6 images."}), 400

    results = {}

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Load and process the image
            img = cv2.imread(filepath)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            
            faces = face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                # If faces are detected, draw rectangles around them in green
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green color (BGR format)
            else:
                # No faces detected, apply semi-transparent red tint to the entire image
                overlay = img.copy()  # Create a copy of the image for overlay
                red_overlay = np.zeros_like(overlay, dtype=np.uint8)  # Create a blank red image
                red_overlay[:] = [0, 0, 255]  # Set the entire image to red (BGR format)

                # Blend the original image with the red overlay to add opacity
                alpha = 0.4  # Opacity factor (0.0 is fully transparent, 1.0 is fully opaque)
                cv2.addWeighted(red_overlay, alpha, overlay, 1 - alpha, 0, img)  # Blend the two images

                # Draw a red rectangle around the whole image to highlight it
                #height, width, _ = img.shape
                #cv2.rectangle(img, (0, 0), (width, height), (0, 0, 255), 5)  # Red border

            # Now `img` contains the processed image with the desired effect
            # Now `img` contains the processed image with the desired effect
            # Encode the processed image (with or without face rectangles) to PNG
            _, img_encoded = cv2.imencode('.png', img)
            img_bytes = img_encoded.tobytes()

            # Convert image bytes to base64 to include in response
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')

            # Store the result for the current image
            if len(faces) > 0:
                results[filename] = {"status": "Faces detected", "image": img_base64}
            else:
                results[filename] = {"status": "No faces detected", "image": img_base64}

        else:
            results[file.filename] = {"status": "Invalid file type"}

    # Prepare the response to return to the frontend
    response = {}
    for filename, result in results.items():
        response[filename] = {
            "status": result["status"],
            "image": result["image"]
        }

    # Return the results as JSON
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
