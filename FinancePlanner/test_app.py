# test_app.py

import pytest
from app import app, db, User, Transaction, Goal, get_balance, update_goals
from werkzeug.security import generate_password_hash
from datetime import date


# TEST CONFIG

@pytest.fixture
def client():

    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:

        with app.app_context():
            db.create_all()

            # create test user
            user = User(
                username="testuser",
                password=generate_password_hash("1234"),
                xp=0,
                level=1,
                xp_needed=100
            )

            db.session.add(user)
            db.session.commit()

        yield client

        with app.app_context():
            db.drop_all()


# HELPER

def login(client):
    return client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "1234"
        },
        follow_redirects=True
    )


# 1. REGISTER TEST

def test_register(client):

    response = client.post(
        "/register",
        data={
            "username": "newuser",
            "password": "abcd"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(username="newuser").first()

        print("\n[REGISTER TEST]")
        print("Expected: User should be created")
        print("Actual:", "User created" if user else "User NOT created")

        assert user is not None

    print("STATUS: PASS")


# 2. LOGIN TEST

def test_login(client):

    response = login(client)

    print("\n[LOGIN TEST]")
    print("Expected: Login success")
    print("Actual Status Code:", response.status_code)

    assert response.status_code == 200

    print("STATUS: PASS")


# 3. ADD INCOME TRANSACTION

def test_add_income_transaction(client):

    login(client)

    response = client.post(
        "/add",
        data={
            "amount": 1000,
            "type": "income",
            "description": "Salary"
        },
        follow_redirects=True
    )

    with app.app_context():

        tx = Transaction.query.first()

        print("\n[ADD INCOME TRANSACTION TEST]")
        print("Expected: Transaction exists")
        print("Actual:", tx.description if tx else "No transaction")

        assert tx is not None
        assert tx.amount == 1000

    print("STATUS: PASS")


# 4. ADD EXPENSE TRANSACTION

def test_add_expense_transaction(client):

    login(client)

    client.post(
        "/add",
        data={
            "amount": 500,
            "type": "expense",
            "description": "Food"
        },
        follow_redirects=True
    )

    with app.app_context():

        tx = Transaction.query.first()

        print("\n[ADD EXPENSE TRANSACTION TEST]")
        print("Expected: Expense transaction added")
        print("Actual Type:", tx.type)

        assert tx.type == "expense"

    print("STATUS: PASS")


# 5. BALANCE CALCULATION TEST

def test_balance_calculation(client):

    login(client)

    with app.app_context():

        user = User.query.filter_by(username="testuser").first()

        t1 = Transaction(
            user_id=user.id,
            amount=1000,
            type="income",
            description="Salary",
            date=date.today()
        )

        t2 = Transaction(
            user_id=user.id,
            amount=200,
            type="expense",
            description="Shopping",
            date=date.today()
        )

        db.session.add_all([t1, t2])
        db.session.commit()

        balance = get_balance(user.id)

        print("\n[BALANCE TEST]")
        print("Income: +1000")
        print("Expense: -200")
        print("Expected Balance: 800")
        print("Actual Balance:", balance)

        assert balance == 800

    print("STATUS: PASS")


# 6. GOAL PRIORITY TEST

def test_goal_priority_system(client):

    login(client)

    with app.app_context():

        user = User.query.filter_by(username="testuser").first()

        income = Transaction(
            user_id=user.id,
            amount=1000,
            type="income",
            description="Salary",
            date=date.today()
        )

        db.session.add(income)

        g1 = Goal(
            user_id=user.id,
            description="Emergency Fund",
            target_amount=500,
            current_amount=0,
            priority=0
        )

        g2 = Goal(
            user_id=user.id,
            description="Vacation",
            target_amount=700,
            current_amount=0,
            priority=1
        )

        db.session.add_all([g1, g2])
        db.session.commit()

        update_goals(user.id)

        db.session.refresh(g1)
        db.session.refresh(g2)

        print("\n[GOAL PRIORITY TEST]")
        print("Expected:")
        print("Emergency Fund = 500")
        print("Vacation = 500")

        print("Actual:")
        print("Emergency Fund =", g1.current_amount)
        print("Vacation =", g2.current_amount)

        assert g1.current_amount == 500
        assert g2.current_amount == 500

    print("STATUS: PASS")



# 7. ANALYTICS PAGE TEST

def test_analytics_page(client):

    login(client)

    response = client.get("/analytics")

    print("\n[ANALYTICS PAGE TEST]")
    print("Expected: Analytics page loads")
    print("Actual Status Code:", response.status_code)

    assert response.status_code == 200

    print("STATUS: PASS")


# 8. PROFILE PAGE TEST

def test_profile_page(client):

    login(client)

    response = client.get("/profile")

    print("\n[PROFILE PAGE TEST]")
    print("Expected: Profile page loads")
    print("Actual Status Code:", response.status_code)

    assert response.status_code == 200

    print("STATUS: PASS")