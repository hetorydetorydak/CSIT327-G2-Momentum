# 🌟 Momentum

**Employee Performance Evaluation Tracker**

---

## 📘 Project Description

**Momentum** is a web-based application designed to streamline employee performance evaluation and provide managers with actionable insights through data-driven dashboards and analytics.

It consolidates **key performance indicators (KPIs)** such as compliance, attendance, and backlog metrics into a centralized and interactive platform.

By offering **real-time visualization**, **employee performance cards**, and **trend analysis**, the system aims to improve transparency, enhance decision-making, and reduce the administrative burden of manual tracking.

---

## 🧠 Tech Stack Used

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript
- **Database:** Supabase (PostgreSQL)
- **Other Tools:** Git & GitHub for version control

---

## ⚙️ Setup & Run Instructions

### 1. Clone the repository

```bash
git clone https://github.com/hetorydetorydak/CSIT327-G2-Momentum.git
cd CSIT327-G2-Momentum
```

### 2. Create and activate a virtual environment

```bash
python -m venv .env

# On macOS/Linux
source .env/bin/activate

# On Windows
.env\Scripts\activate
```

- Create a ```supabase.env``` file in Project Root(same level as ```manage.py```)
```bash
#supabase.env

# Supabase PostgreSQL (Session Pooler) 
DATABASE_URL="postgresql://postgres.gjxvixipmhrkgbxrmcul:1u11WHlQgfqax5v8@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres"
```

### 3. Install dependencies

```bash
pip install django
pip install psycopg2 dj-database-url python-dotenv 
```

### 4. Start the development server

```bash
# On macOS/Linux
python3 manage.py runserver

# On Windows
python manage.py runserver
 # or
py manage.py runserver
```

## 👥 Team members

- John Hector P. Villarta / Lead Developer / johnhector.villarta@cit.edu
- Christian Ken Yabao / Frontend Developer / christianken.yabao@cit.edu
- Bianca Margarette G. Vallo / Backend Developer/Business Analyst / biancamargarette.vallo@cit.edu
- Prince Daniel R. Tabanas / Product Owner / princedaniel.tabanas@cit.edu
- Brye Kane L. Sy / Scrum Master/ bryekane.sy@cit.edu
