# Personal Finance Advisor Bot

A student-friendly full-stack Flask project for an AI-powered personal finance management platform.
 
Full documentation 
https://docs.google.com/document/d/1YGCN3y00azXyACo4s22o-3UTq-GiuIwl/edit?usp=drivesdk&ouid=111108828297196725448&rtpof=true&sd=true

## Features
- User registration and login
- Secure password hashing and session-based access
- Income and expense recording
- Expense categories
- Budget planning
- Savings/balance tracking
- Interactive dashboard
- Category-wise spending chart
- Rule-based financial insights
- SQLite database
- Responsive JavaScript frontend
- Ready for optional Gemini/OpenAI integration
- Designed so it can later be exposed with ngrok

## Tech stack
Python, Flask, Flask-SQLAlchemy, SQLite, Jinja2, HTML, CSS, JavaScript.

## Run locally

### Windows
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Open http://127.0.0.1:5000

## Optional ngrok
After the Flask app is running:
```bash
ngrok http 5000
```

## Important
Do not commit `.env` or real API keys to GitHub.
The included AI-advice endpoint is intentionally rule-based so the project runs without paid API access. A Gemini/OpenAI call can be added later using an environment variable.
