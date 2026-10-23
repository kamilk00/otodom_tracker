# Otodom Property Price Tracker 🏠📉

A modern, multi-user Django web application designed to track real estate listings from **Otodom.pl**, monitor price trends over time, and automatically notify users of price drops.

---

## 🌟 Key Features

* **Multi-User Listing Tracking (M2M Architecture):** Multiple users can track the exact same Otodom property simultaneously. Stopping tracking removes the listing from the user's dashboard without deleting global price history.
* **Automated Price Scraper & Monitoring:** A custom Django management command (`update_prices`) scrapes live listings, detects price changes, and records price histories.
* **Smart Notification System:**
  * Generates per-user alerts when price drops are detected.
  * Interactive navbar badge with dynamic unread counter (via custom Django Context Processor).
  * Auto-marks notifications as read when clicking on property details.
  * "Mark all as read" action and dedicated **Notification History** page.
* **Interactive Price Charts:** Visualizes price trends over time using **Chart.js** with localized timezone support.
* **Clean Data Lifecycle Management:** Automatically detects expired/deleted Otodom listings (HTTP 404/410 or missing markup) and deactivates them (`is_active = False`).

---

## 🛠 Tech Stack

* **Backend:** Python 3.10+, Django 5.x, SQLite / PostgreSQL
* **Frontend:** HTML5, Tailwind CSS, JavaScript, Chart.js
* **Scraping:** Requests, LXML

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone [https://github.com/kamilk00/otodom-tracker.git](https://github.com/kamilk00/otodom-tracker.git)
cd otodom-tracker
```

### 2. Set up virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create superuser & start dev server
```bash
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000` in your browser.

---

## ⚙️ Management Commands

To trigger price checks, update historical data, create user alerts, and deactivate expired listings, run:

```bash
python manage.py update_prices
```

*Tip: This command can be scheduled using Cron jobs or Celery for fully automated daily monitoring.*