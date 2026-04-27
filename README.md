# 🐶 AC Financial Planner

A modern, interactive financial planning web application built with Flask.
It allows users to track transactions, manage financial goals, and visualize their financial progress in real time.

---

## 🚀 Features

### 💰 Transaction Management

* Add income and expense transactions
* Automatic balance calculation
* Real-time updates

### 🎯 Smart Goals System

* Create financial goals with target amounts
* Drag & drop priority system
* Dynamic balance allocation:

  * Positive balance fills goals by priority
  * Negative balance reduces lower-priority goals first
  * Highest priority goal can go negative if needed

### 📊 Analytics Dashboard

* Weekly, monthly, yearly financial summaries
* Cumulative charts
* Daily average and projections

### 🎮 Gamification

* XP system
* Level progression
* Achievements (streaks, milestones)

### 🐶 Interactive UI

* Animated dog mascot
* Eyes follow mouse movement
* Smooth and engaging interface

---

## 🧠 How It Works

### Balance Calculation

Balance is calculated as:

* Income → positive
* Expense → negative

### Goal Allocation Logic

#### Positive Balance:

* Filled from **highest priority → lowest**
* Each goal fills until target is reached

#### Negative Balance:

* Reduced from **lowest priority → highest**
* Goals are emptied first
* If still negative → highest priority goal goes below zero

---

## 🛠️ Tech Stack

* **Backend:** Flask (Python)
* **Database:** SQLite
* **ORM:** SQLAlchemy
* **Frontend:** HTML, CSS, JavaScript
* **Authentication:** Flask-Login

---

## 📁 Project Structure

```
/project
│
├── app.py
├── models.py
├── xp.py
│
├── /templates
│   ├── base.html
│   ├── dashboard.html
│   ├── goals.html
│   ├── transactions.html
│   ├── analytics.html
│   ├── profile.html
│
├── /static
│   ├── style.css
│   ├── dog.js
│   ├── dog.png
│   ├── dog2.png
│
└── finance.db
```

---

## ⚙️ Installation

1. Clone the repository:

```
git clone https://github.com/Rasarow/ACFinancialPlanner.git
cd ACFinancialPlanner
```

2. Install dependencies:

```
pip install flask flask_sqlalchemy flask_login
```

3. Run the app:

```
python app.py
```

4. Open in browser:

```
http://127.0.0.1:5000
```

---

## 🧪 User Testing (Summary)

A simulated user test was conducted:

* Users successfully:

  * Registered and logged in
  * Added transactions
  * Managed goals
  * Used drag & drop priority
* Real-time updates improved usability
* Interactive UI increased engagement

### Identified Improvements:

* Add onboarding/tutorial
* Improve visibility of currency switch
* Explain goal logic more clearly

---

## 📌 Future Improvements

* Mobile responsiveness
* Notifications system
* Budget categories
* Data export (CSV / PDF)
* Multi-currency support

---

## 👨‍💻 Author

Developed by Rasih Alperen Sahinoz and Celal Can Koca

---

## 📄 License

This project is for educational purposes.
