# \# Job Application Tracker

# 

# A web application for tracking job applications. Built with Python (Flask), MySQL, and HTML/CSS (Bootstrap).

# 

# \## Features

# \- Full CRUD (add, view, edit, delete with confirmation) for companies, jobs, applications, and contacts

# \- Dashboard with totals, applications by status, and recent applications

# \- Job Match: enter your skills and see jobs ranked by match percentage, with missing skills

# \- JSON columns for job requirements and interview data

# 

# \## Requirements

# \- Python 3.10+

# \- MySQL Server 8.0+ (tested on 8.4)

# 

# \## Setup

# 

# 1\. \*\*Clone the repository\*\*

# &#x20;  ```

# &#x20;  git clone https://github.com/LeonEmrys/job\_tracker.git

# &#x20;  cd job\_tracker

# &#x20;  ```

# 

# 2\. \*\*Install Python dependencies\*\*

# &#x20;  ```

# &#x20;  pip install -r requirements.txt

# &#x20;  ```

# &#x20;  (On Windows you can use `py -m pip install -r requirements.txt`.)

# 

# 3\. \*\*Create the database.\*\* From the project folder, log in to MySQL and run the schema script:

# &#x20;  ```

# &#x20;  mysql -u root -p

# &#x20;  ```

# &#x20;  Then at the `mysql>` prompt:

# &#x20;  ```

# &#x20;  source schema.sql

# &#x20;  ```

# &#x20;  This creates the `job\_tracker` database, the four tables, and some sample data.

# 

# 4\. \*\*Configure your database password.\*\* Copy `.env.example` to `.env` and put in your MySQL password:

# &#x20;  ```

# &#x20;  DB\_HOST=localhost

# &#x20;  DB\_USER=root

# &#x20;  DB\_PASSWORD=your\_mysql\_password\_here

# &#x20;  DB\_NAME=job\_tracker

# &#x20;  ```

# 

# 5\. \*\*Run the app\*\*

# &#x20;  ```

# &#x20;  python app.py

# &#x20;  ```

# &#x20;  (On Windows: `py app.py`.)

# 

# 6\. Open http://127.0.0.1:5000 in your browser.

# 

# \## Project Structure

# \- `app.py`: Flask routes and application logic

# \- `database.py`: database connection and query helpers

# \- `schema.sql`: database creation script with sample data

# \- `templates/`: HTML templates

# \- `static/`: CSS

# \- `AI\_USAGE.md`: documentation of GenAI usage

# \- `requirements.txt`: Python dependencies

# 

# \## Database Tables

# `companies`, `jobs` (JSON `requirements`), `applications` (JSON `interview\_data`), `contacts`.

# Foreign keys use `ON DELETE CASCADE`.

