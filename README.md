# 🧠 Mental Health Chatbot (Flask + Dialogflow + PostgreSQL)

This is a full-stack web application designed to provide users with mental health support through an intelligent chatbot. It integrates Google Dialogflow for natural language understanding, uses Flask for backend services, and PostgreSQL for database management. Users can register, log in, and interact with a chatbot that understands mental health queries based on pre-trained intents.

---

## 🔧 Prerequisites

- Python 3.8+
- PostgreSQL
- Flask packages (see below)
- Google Cloud SDK
- A service account with Dialogflow API enabled

---

## 📂 Project Structure

```
📁 project/
│
├── app.py                        # Main Flask backend
├── structured_mental_health.json # Intent data for Dialogflow
├── vast-ytfa-36b7391b4430.json   # Google Cloud service account key
├── google-cloud-sdk-453.0.0-linux-x86_64.tar.gz  # SDK (optional local setup)
├── templates/
│   ├── login.html
│   └── signup.html
```

---

## 📦 Installation & Setup

1. **Clone the repository**:

```bash
git clone https://github.com/<your-username>/mental-health-chatbot.git
cd mental-health-chatbot
```

2. **Set up a virtual environment (optional but recommended)**:

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

Create `requirements.txt` with:

```txt
Flask
Flask-Bcrypt
Flask-Login
Flask-Cors
psycopg2-binary
google-cloud-dialogflow
google-auth
```

4. **Configure PostgreSQL Database**:

Make sure PostgreSQL is running and create a database:

```sql
CREATE DATABASE mental_health_bot;
```

Update credentials inside `app.py` if needed:

```python
DB_NAME = "mental_health_bot"
DB_USER = "postgres"
DB_PASSWORD = "123456"
DB_HOST = "localhost"
DB_PORT = "5432"
```

5. **Enable Google Dialogflow API**:

- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project (or use the existing one: `vast-ytfa`)
- Enable **Dialogflow API**
- Download the service account key and place it as `vast-ytfa-36b7391b4430.json`
- Export credentials:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="vast-ytfa-36b7391b4430.json"
```

6. **Import Dialogflow Intents** (Optional):

```python
from app import import_intents_from_json
import_intents_from_json("structured_mental_health.json")
```

---

## 🚀 Run the App

```bash
python app.py
```

Open your browser and navigate to `http://localhost:5000`.

---

## ✨ Features

- User Authentication (Sign Up & Login)
- Secure password storage with Bcrypt
- Dialogflow chatbot integration
- JSON-based intent loading
- RESTful chat API
- Session handling with Flask-Login

---

## 🔐 Notes

- Replace `your_secret_key` in `app.py` with a strong secret key.
- This app uses a hardcoded `session_id` — consider using dynamic session management for production.
- The app runs in `debug=True` mode. Disable this in production.

---

## 📄 License

MIT License

