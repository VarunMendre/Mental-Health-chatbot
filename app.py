from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import psycopg2
import json
from flask_cors import CORS
import os
from google.cloud import dialogflow
from google.oauth2 import service_account

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# PostgreSQL Database Configuration
DB_NAME = "mental_health_bot"
DB_USER = "postgres"
DB_PASSWORD = "123456"
DB_HOST = "localhost"
DB_PORT = "5432"

def get_db_connection():
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

# User Class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return User(user[0], user[1], user[2]) if user else None

# Dialogflow Integration
DIALOGFLOW_PROJECT_ID = "vast-ytfa"
GOOGLE_APPLICATION_CREDENTIALS = "vast-ytfa-36b7391b4430.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vast-ytfa-36b7391b4430.json"  # Ensure this matches your key filename


def detect_intent_texts(session_id, text, language_code="en"):
    credentials = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)
    session_client = dialogflow.SessionsClient(credentials=credentials)
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, session_id)
    
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    
    try:
        response = session_client.detect_intent(request={"session": session, "query_input": query_input})
        return response.query_result.fulfillment_text
    except Exception as e:
        print(f"Dialogflow API Error: {e}")
        return "I'm having trouble connecting to Dialogflow. Please try again later."

# Import Intents from JSON File
def import_intents_from_json(json_file):
    with open(json_file, "r") as f:
        data = json.load(f)
    
    credentials = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)
    client = dialogflow.IntentsClient(credentials=credentials)
    parent = f"projects/{DIALOGFLOW_PROJECT_ID}/agent"
    
    for intent in data["intents"]:
        training_phrases = [
            dialogflow.Intent.TrainingPhrase(parts=[dialogflow.Intent.TrainingPhrase.Part(text=phrase)])
            for phrase in intent["patterns"]
        ]
        responses = [dialogflow.Intent.Message(text=dialogflow.Intent.Message.Text(text=[resp])) for resp in intent["responses"]]
        
        intent_obj = dialogflow.Intent(display_name=intent["tag"], training_phrases=training_phrases, messages=responses)
        client.create_intent(request={"parent": parent, "intent": intent_obj})
    
    print("Intents imported successfully!")

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if username already exists
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()
        
        if existing_user:
            cur.close()
            conn.close()
            return jsonify({"error": "Username already exists"}), 400
        
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING id", (username, email, hashed_password))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        user = User(user_id, username, email)
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user and bcrypt.check_password_hash(user[3], password):
            user_obj = User(user[0], user[1], user[2])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# Index Route - Redirects to Login if Not Authenticated
@app.route('/')
@login_required
def dashboard():
    return render_template('index.html', username=current_user.username)

# Chat Route - Requires Login
@app.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    
    print(f"Received message: {user_message}")
    response = detect_intent_texts("session-12345", user_message)
    print(f"Dialogflow Response: {response}")
    
    return jsonify({"reply": response})

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
