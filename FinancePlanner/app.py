from flask import Flask, render_template, redirect, request, session, jsonify
from models import db, User, Transaction, Goal, DailyLogin, Achievement
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta
from xp import add_xp, handle_leveling
import calendar

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def create_tables():
    db.create_all()


# ================= CURRENCY =================
def get_currency():
    return session.get("currency") or "$"


@app.route("/set_currency/<cur>")
@login_required
def set_currency(cur):
    if cur in ["$", "₽"]:
        session["currency"] = cur
    return redirect(request.referrer or "/")


@app.context_processor
def inject_currency():
    return {"currency": get_currency()}


# ================= POPUP =================
def set_popup(msg):
    session["popup"] = msg


def get_popup():
    return session.pop("popup", None)


# ================= BALANCE =================
def get_balance(uid):
    tx = Transaction.query.filter_by(user_id=uid).all()
    total = 0.0

    for t in tx:
        if not t.amount:
            continue
        try:
            amt = float(t.amount)
        except:
            continue

        total += amt if t.type == "income" else -amt

    return total


# ================= GOALS (FIXED CORE LOGIC) =================
def update_goals(uid):
    balance = get_balance(uid)

    goals = Goal.query.filter_by(user_id=uid)\
        .order_by(Goal.priority.asc(), Goal.id.asc()).all()

    for g in goals:
        g.current_amount = 0.0

    # POSITIVE BALANCE -> fill from low priority to high
    if balance >= 0:
        remaining = balance

        for g in goals:
            if remaining <= 0:
                break

            target = float(g.target_amount or 0)
            fill = min(target, remaining)

            g.current_amount = fill
            remaining -= fill

    # NEGATIVE BALANCE -> UNFILL from LOW PRIORITY first
    else:
        remaining = abs(balance)

        for g in reversed(goals):  # low priority first (last in list)
            if remaining <= 0:
                break

            current = float(g.current_amount or 0)
            reduce_amount = min(current, remaining)

            g.current_amount = current - reduce_amount
            remaining -= reduce_amount

        # if still negative left → allow highest priority to go negative
        if remaining > 0 and goals:
            top = goals[0]
            top.current_amount -= remaining

    db.session.commit()


# ================= STREAK =================
def streak(uid):
    logs = DailyLogin.query.filter_by(user_id=uid)\
        .order_by(DailyLogin.date.desc()).all()

    today = date.today()
    s = 0

    for i, l in enumerate(logs):
        if l.date == today - timedelta(days=i):
            s += 1
        else:
            break

    return s


# ================= ACHIEVEMENTS =================
def check_achievements(user):
    existing = {a.title for a in Achievement.query.filter_by(user_id=user.id).all()}

    def give(title, desc, badge):
        if title not in existing:
            db.session.add(Achievement(
                user_id=user.id,
                title=title,
                description=f"{desc}|{badge}"
            ))

    tx_count = Transaction.query.filter_by(user_id=user.id).count()

    give("Daily Login", "Login reward", "gray")

    if tx_count >= 1:
        give("First Step", "First transaction", "bronze")

    if tx_count >= 10:
        give("Momentum", "10 transactions", "silver")

    if streak(user.id) >= 3:
        give("Consistency", "3 day streak", "gold")

    db.session.commit()


# ================= DASHBOARD =================
@app.route('/')
@login_required
def dashboard():
    tx = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.id.desc()).limit(5).all()

    update_goals(current_user.id)
    check_achievements(current_user)

    goals = Goal.query.filter_by(user_id=current_user.id)\
        .order_by(Goal.priority.asc()).all()

    return render_template(
        "dashboard.html",
        transactions=tx,
        balance=get_balance(current_user.id),
        goals=goals,
        level=current_user.level,
        xp=current_user.xp,
        xp_needed=current_user.xp_needed,
        popup=get_popup()
    )


# ================= LOGIN =================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form['username']).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)

            today = date.today()

            if not DailyLogin.query.filter_by(user_id=user.id, date=today).first():
                db.session.add(DailyLogin(user_id=user.id, date=today))
                add_xp(user, 5)
                db.session.commit()

            set_popup(f"🔥 Welcome Back! {streak(user.id)} day streak")
            return redirect('/')

    return render_template("login.html", popup=get_popup())


# ================= REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        u = User(
            username=request.form['username'],
            password=generate_password_hash(request.form['password']),
            xp=0,
            level=1,
            xp_needed=100
        )

        db.session.add(u)
        db.session.commit()

        set_popup("🔥 Account Created!")
        return redirect('/login')

    return render_template("register.html", popup=get_popup())


# ================= LOGOUT =================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


# ================= ADD =================
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == "POST":
        t = Transaction(
            user_id=current_user.id,
            amount=float(request.form['amount']),
            type=request.form['type'],
            description=request.form['description'],
            date=date.today()
        )

        db.session.add(t)

        add_xp(current_user, 10)
        handle_leveling(current_user)

        db.session.commit()
        update_goals(current_user.id)

        return redirect('/')

    return render_template("add_transaction.html")


# ================= TRANSACTIONS =================
@app.route('/transactions')
@login_required
def transactions():
    tx = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.id.desc()).all()

    return render_template(
        "transactions.html",
        transactions=tx,
        currency=get_currency()
    )


@app.route('/delete_transaction/<int:id>')
@login_required
def delete_transaction(id):
    t = Transaction.query.get(id)

    if t and t.user_id == current_user.id:
        db.session.delete(t)
        db.session.commit()

    update_goals(current_user.id)
    return redirect('/transactions')


# ================= GOALS =================
@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    if request.method == "POST":
        g = Goal(
            user_id=current_user.id,
            target_amount=float(request.form['target']),
            description=request.form['description'],
            current_amount=0.0,
            priority=999
        )

        db.session.add(g)
        db.session.commit()

        update_goals(current_user.id)
        return redirect('/goals')

    goals = Goal.query.filter_by(user_id=current_user.id)\
        .order_by(Goal.priority.asc()).all()

    return render_template("goals.html", goals=goals, currency=get_currency())


# ================= DRAG DROP FIX (LIVE UPDATE SUPPORT) =================
@app.route('/update_priority', methods=['POST'])
@login_required
def update_priority():
    data = request.json.get("order", [])

    for i, gid in enumerate(data):
        g = Goal.query.get(int(gid))
        if g:
            g.priority = i

    db.session.commit()

    # CRITICAL FIX: recalc immediately and return fresh state
    update_goals(current_user.id)

    goals = Goal.query.filter_by(user_id=current_user.id)\
        .order_by(Goal.priority.asc()).all()

    return jsonify({
        "ok": True,
        "goals": [
            {
                "id": g.id,
                "description": g.description,
                "current_amount": g.current_amount,
                "target_amount": g.target_amount
            } for g in goals
        ]
    })


# ================= ANALYTICS =================
@app.route('/analytics')
@login_required
def analytics():
    tx = Transaction.query.filter_by(user_id=current_user.id).all()
    today = date.today()

    def net(days):
        cutoff = today - timedelta(days=days)
        total = 0.0

        for t in tx:
            if t.date and t.date >= cutoff:
                v = float(t.amount)
                total += v if t.type == "income" else -v

        return total

    week = net(7)
    month = net(30)
    year = net(365)

    daily_avg = round(week / 7, 1) if week else 0.0

    monthly_projection = round(daily_avg * 30, 1)
    yearly_projection = round(daily_avg * 365, 1)

    def cumulative(days):
        data = []
        running = 0.0

        for i in range(days, -1, -1):
            d = today - timedelta(days=i)

            for t in tx:
                if t.date == d:
                    v = float(t.amount)
                    running += v if t.type == "income" else -v

            data.append({"x": d.strftime("%d %b"), "y": running})

        return data

    def year_data():
        data = []
        running = 0.0

        for m in range(1, today.month + 1):
            for t in tx:
                if t.date and t.date.month == m and t.date.year == today.year:
                    v = float(t.amount)
                    running += v if t.type == "income" else -v

            data.append({"x": calendar.month_abbr[m], "y": running})

        return data

    return render_template(
        "analytics.html",
        week={"net": round(week, 1)},
        month={"net": round(month, 1)},
        year={"net": round(year, 1)},
        daily_avg=daily_avg,
        monthly_projection=monthly_projection,
        yearly_projection=yearly_projection,
        week_chart=cumulative(7),
        month_chart=cumulative(30),
        year_chart=year_data(),
        currency=get_currency()
    )


# ================= PROFILE =================
@app.route('/profile')
@login_required
def profile():
    achievements = Achievement.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "profile.html",
        user=current_user,
        streak=streak(current_user.id),
        achievements=achievements,
        popup=get_popup()
    )


if __name__ == "__main__":
    app.run(debug=True)