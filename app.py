import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///finance.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    monthly_income = db.Column(db.Float, default=0)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    kind = db.Column(db.String(20), nullable=False)  # income/expense
    category = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(255), default="")
    date = db.Column(db.Date, default=datetime.utcnow().date)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Float, nullable=False)

def current_user():
    uid = session.get("user_id")
    return User.query.get(uid) if uid else None

def totals(user_id):
    rows = Transaction.query.filter_by(user_id=user_id).all()
    income = sum(x.amount for x in rows if x.kind == "income")
    expense = sum(x.amount for x in rows if x.kind == "expense")
    return income, expense, income - expense

@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("landing.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for("register"))
        user = User(name=name, email=email,
                    password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        return redirect(url_for("dashboard"))
    return render_template("auth.html", mode="register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.")
            return redirect(url_for("login"))
        session["user_id"] = user.id
        return redirect(url_for("dashboard"))
    return render_template("auth.html", mode="login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    income, expense, balance = totals(user.id)
    transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.date.desc(), Transaction.id.desc()).limit(12).all()
    budgets = Budget.query.filter_by(user_id=user.id).all()
    return render_template("dashboard.html", user=user, income=income, expense=expense,
                           balance=balance, transactions=transactions, budgets=budgets)

@app.post("/api/transaction")
def add_transaction():
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json() or {}
    kind = data.get("kind")
    try:
        amount = float(data.get("amount", 0))
    except ValueError:
        amount = 0
    if kind not in ("income", "expense") or amount <= 0:
        return jsonify({"error": "Invalid transaction"}), 400
    row = Transaction(user_id=user.id, kind=kind,
                      category=(data.get("category") or "Other").strip(),
                      amount=amount, note=(data.get("note") or "").strip())
    db.session.add(row)
    db.session.commit()
    return jsonify({"ok": True})

@app.post("/api/budget")
def add_budget():
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json() or {}
    try:
        amount = float(data.get("amount", 0))
    except ValueError:
        amount = 0
    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400
    row = Budget(user_id=user.id, category=(data.get("category") or "Other").strip(), amount=amount)
    db.session.add(row)
    db.session.commit()
    return jsonify({"ok": True})

@app.post("/api/ai-advice")
def ai_advice():
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    income, expense, balance = totals(user.id)
    rows = Transaction.query.filter_by(user_id=user.id, kind="expense").all()
    by_cat = {}
    for r in rows:
        by_cat[r.category] = by_cat.get(r.category, 0) + r.amount
    top = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)[:5]

    # Safe fallback works without an external API key.
    advice = []
    if income <= 0:
        advice.append("Add your monthly income so the advisor can calculate a realistic budget.")
    else:
        savings_rate = max(0, balance / income * 100)
        advice.append(f"Your current recorded savings rate is about {savings_rate:.1f}%.")
        if savings_rate < 20:
            advice.append("Consider targeting a gradual 20% savings rate by reviewing non-essential spending.")
        else:
            advice.append("You are currently recording a savings rate of 20% or more; keep an emergency fund goal in view.")
    if top:
        advice.append("Your largest expense categories are: " + ", ".join(f"{c} (₹{a:,.0f})" for c, a in top[:3]) + ".")
    if balance < 0:
        advice.append("Recorded expenses are above recorded income. Review recurring and discretionary costs first.")
    else:
        advice.append(f"Recorded balance is ₹{balance:,.0f}. Consider assigning part of it to savings before discretionary spending.")

    return jsonify({"advice": advice, "note": "This demo uses rule-based financial insights. Add a Gemini/OpenAI API integration only when you have your own secure API key."})

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
