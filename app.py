import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db, query_all, query_one, execute

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")


@app.route("/")
def dashboard():
    counts = query_one(
        "SELECT "
        "(SELECT COUNT(*) FROM companies) AS companies, "
        "(SELECT COUNT(*) FROM jobs) AS jobs, "
        "(SELECT COUNT(*) FROM applications) AS applications, "
        "(SELECT COUNT(*) FROM contacts) AS contacts"
    )
    status_counts = {s: 0 for s in STATUSES}
    for row in query_all("SELECT status, COUNT(*) AS count FROM applications GROUP BY status"):
        status_counts[row["status"]] = row["count"]
    recent = query_all(
        "SELECT a.application_date, a.status, j.job_title, co.company_name "
        "FROM applications a "
        "LEFT JOIN jobs j ON a.job_id = j.job_id "
        "LEFT JOIN companies co ON j.company_id = co.company_id "
        "ORDER BY a.application_date DESC, a.application_id DESC LIMIT 5"
    )
    return render_template("dashboard.html", counts=counts,
                           status_counts=status_counts, recent=recent)

# ---------- Companies ----------

@app.route("/companies")
def companies():
    rows = query_all("SELECT * FROM companies ORDER BY company_name")
    return render_template("companies.html", companies=rows)


@app.route("/companies/add", methods=["GET", "POST"])
def add_company():
    if request.method == "POST":
        name = request.form["company_name"].strip()
        if not name:
            flash("Company name is required.", "danger")
            return render_template("company_form.html", company=request.form, action="Add")
        execute(
            "INSERT INTO companies (company_name, industry, website, city, state, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (name, request.form["industry"], request.form["website"],
             request.form["city"], request.form["state"], request.form["notes"]),
        )
        flash("Company added.", "success")
        return redirect(url_for("companies"))
    return render_template("company_form.html", company={}, action="Add")


@app.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
def edit_company(company_id):
    company = query_one("SELECT * FROM companies WHERE company_id = %s", (company_id,))
    if not company:
        flash("Company not found.", "danger")
        return redirect(url_for("companies"))
    if request.method == "POST":
        name = request.form["company_name"].strip()
        if not name:
            flash("Company name is required.", "danger")
            return render_template("company_form.html", company=request.form, action="Edit")
        execute(
            "UPDATE companies SET company_name=%s, industry=%s, website=%s, "
            "city=%s, state=%s, notes=%s WHERE company_id=%s",
            (name, request.form["industry"], request.form["website"],
             request.form["city"], request.form["state"], request.form["notes"], company_id),
        )
        flash("Company updated.", "success")
        return redirect(url_for("companies"))
    return render_template("company_form.html", company=company, action="Edit")


@app.route("/companies/<int:company_id>/delete", methods=["POST"])
def delete_company(company_id):
    execute("DELETE FROM companies WHERE company_id = %s", (company_id,))
    flash("Company deleted.", "success")
    return redirect(url_for("companies"))

# ---------- Contacts ----------

def validate_contact(form):
    if not form["contact_name"].strip():
        return "Contact name is required."
    if not form["company_id"]:
        return "Please choose a company."
    if form["email"] and "@" not in form["email"]:
        return "Email must contain an @."
    return None


def contact_values(form):
    return (
        form["company_id"],
        form["contact_name"].strip(),
        form["title"],
        form["email"],
        form["phone"],
        form["linkedin_url"],
        form["notes"],
    )


@app.route("/contacts")
def contacts():
    rows = query_all(
        "SELECT c.*, co.company_name FROM contacts c "
        "LEFT JOIN companies co ON c.company_id = co.company_id "
        "ORDER BY c.contact_name"
    )
    return render_template("contacts.html", contacts=rows)


@app.route("/contacts/add", methods=["GET", "POST"])
def add_contact():
    companies = query_all("SELECT company_id, company_name FROM companies ORDER BY company_name")
    if request.method == "POST":
        error = validate_contact(request.form)
        if error:
            flash(error, "danger")
            return render_template("contact_form.html", contact=request.form,
                                   companies=companies, action="Add")
        execute(
            "INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            contact_values(request.form),
        )
        flash("Contact added.", "success")
        return redirect(url_for("contacts"))
    return render_template("contact_form.html", contact={}, companies=companies, action="Add")


@app.route("/contacts/<int:contact_id>/edit", methods=["GET", "POST"])
def edit_contact(contact_id):
    contact = query_one("SELECT * FROM contacts WHERE contact_id = %s", (contact_id,))
    if not contact:
        flash("Contact not found.", "danger")
        return redirect(url_for("contacts"))
    companies = query_all("SELECT company_id, company_name FROM companies ORDER BY company_name")
    if request.method == "POST":
        error = validate_contact(request.form)
        if error:
            flash(error, "danger")
            return render_template("contact_form.html", contact=request.form,
                                   companies=companies, action="Edit")
        execute(
            "UPDATE contacts SET company_id=%s, contact_name=%s, title=%s, email=%s, "
            "phone=%s, linkedin_url=%s, notes=%s WHERE contact_id=%s",
            contact_values(request.form) + (contact_id,),
        )
        flash("Contact updated.", "success")
        return redirect(url_for("contacts"))
    return render_template("contact_form.html", contact=contact, companies=companies, action="Edit")


@app.route("/contacts/<int:contact_id>/delete", methods=["POST"])
def delete_contact(contact_id):
    execute("DELETE FROM contacts WHERE contact_id = %s", (contact_id,))
    flash("Contact deleted.", "success")
    return redirect(url_for("contacts"))
# ---------- Jobs ----------

JOB_TYPES = ["Full-time", "Part-time", "Contract", "Internship"]


def parse_requirements(value):
    """Turn the JSON column into a Python list of skills."""
    if not value:
        return []
    if isinstance(value, (bytes, bytearray)):
        value = value.decode()
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return []
    return value if isinstance(value, list) else []


def skills_from_text(text):
    return [s.strip() for s in text.split(",") if s.strip()]


def to_int(text):
    text = text.strip()
    return int(text) if text else None


def validate_job(form):
    if not form["job_title"].strip():
        return "Job title is required."
    if not form["company_id"]:
        return "Please choose a company."
    if form["job_type"] not in JOB_TYPES:
        return "Please choose a job type."
    try:
        low = to_int(form["salary_min"])
        high = to_int(form["salary_max"])
    except ValueError:
        return "Salary must be a whole number."
    if low is not None and high is not None and low > high:
        return "Minimum salary cannot be higher than maximum salary."
    return None


def job_values(form):
    return (
        form["company_id"],
        form["job_title"].strip(),
        form["job_type"],
        to_int(form["salary_min"]),
        to_int(form["salary_max"]),
        form["job_url"],
        form["date_posted"] or None,
        json.dumps(skills_from_text(form["requirements"])),
    )


@app.route("/jobs")
def jobs():
    rows = query_all(
        "SELECT j.*, co.company_name FROM jobs j "
        "LEFT JOIN companies co ON j.company_id = co.company_id "
        "ORDER BY j.date_posted DESC, j.job_title"
    )
    for row in rows:
        row["skills"] = parse_requirements(row["requirements"])
    return render_template("jobs.html", jobs=rows)


@app.route("/jobs/add", methods=["GET", "POST"])
def add_job():
    companies = query_all("SELECT company_id, company_name FROM companies ORDER BY company_name")
    if request.method == "POST":
        error = validate_job(request.form)
        if error:
            flash(error, "danger")
            return render_template("job_form.html", job=request.form, companies=companies,
                                   job_types=JOB_TYPES, requirements_text=request.form["requirements"],
                                   action="Add")
        execute(
            "INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, "
            "job_url, date_posted, requirements) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            job_values(request.form),
        )
        flash("Job added.", "success")
        return redirect(url_for("jobs"))
    return render_template("job_form.html", job={}, companies=companies, job_types=JOB_TYPES,
                           requirements_text="", action="Add")


@app.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def edit_job(job_id):
    job = query_one("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for("jobs"))
    companies = query_all("SELECT company_id, company_name FROM companies ORDER BY company_name")
    if request.method == "POST":
        error = validate_job(request.form)
        if error:
            flash(error, "danger")
            return render_template("job_form.html", job=request.form, companies=companies,
                                   job_types=JOB_TYPES, requirements_text=request.form["requirements"],
                                   action="Edit")
        execute(
            "UPDATE jobs SET company_id=%s, job_title=%s, job_type=%s, salary_min=%s, "
            "salary_max=%s, job_url=%s, date_posted=%s, requirements=%s WHERE job_id=%s",
            job_values(request.form) + (job_id,),
        )
        flash("Job updated.", "success")
        return redirect(url_for("jobs"))
    return render_template("job_form.html", job=job, companies=companies, job_types=JOB_TYPES,
                           requirements_text=", ".join(parse_requirements(job["requirements"])),
                           action="Edit")


@app.route("/jobs/<int:job_id>/delete", methods=["POST"])
def delete_job(job_id):
    execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))
    flash("Job deleted.", "success")
    return redirect(url_for("jobs"))

# ---------- Applications ----------

STATUSES = ["Applied", "Screening", "Interview", "Offer", "Rejected", "Withdrawn"]


def parse_interview(value):
    """Turn the interview_data JSON column into a Python dict."""
    if not value:
        return {}
    if isinstance(value, (bytes, bytearray)):
        value = value.decode()
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return {}
    return value if isinstance(value, dict) else {}


def interview_json(form):
    data = {}
    if form["interview_round"].strip():
        data["round"] = int(form["interview_round"])
    if form["interview_date"]:
        data["date"] = form["interview_date"]
    if form["interview_notes"].strip():
        data["notes"] = form["interview_notes"].strip()
    return json.dumps(data) if data else None


def validate_application(form):
    if not form["job_id"]:
        return "Please choose a job."
    if not form["application_date"]:
        return "Application date is required."
    if form["status"] not in STATUSES:
        return "Please choose a status."
    if form["interview_round"].strip():
        try:
            int(form["interview_round"])
        except ValueError:
            return "Interview round must be a whole number."
    return None


def application_values(form):
    return (
        form["job_id"],
        form["application_date"],
        form["status"],
        form["resume_version"],
        1 if form.get("cover_letter_sent") else 0,
        interview_json(form),
    )


def job_options():
    return query_all(
        "SELECT j.job_id, j.job_title, co.company_name FROM jobs j "
        "LEFT JOIN companies co ON j.company_id = co.company_id "
        "ORDER BY co.company_name, j.job_title"
    )


def interview_from_form(form):
    return {
        "round": form["interview_round"],
        "date": form["interview_date"],
        "notes": form["interview_notes"],
    }


@app.route("/applications")
def applications():
    rows = query_all(
        "SELECT a.*, j.job_title, co.company_name FROM applications a "
        "LEFT JOIN jobs j ON a.job_id = j.job_id "
        "LEFT JOIN companies co ON j.company_id = co.company_id "
        "ORDER BY a.application_date DESC"
    )
    for row in rows:
        row["interview"] = parse_interview(row["interview_data"])
    return render_template("applications.html", applications=rows)


@app.route("/applications/add", methods=["GET", "POST"])
def add_application():
    if request.method == "POST":
        error = validate_application(request.form)
        if error:
            flash(error, "danger")
            return render_template("application_form.html", application=request.form,
                                   jobs=job_options(), statuses=STATUSES,
                                   interview=interview_from_form(request.form), action="Add")
        execute(
            "INSERT INTO applications (job_id, application_date, status, resume_version, "
            "cover_letter_sent, interview_data) VALUES (%s, %s, %s, %s, %s, %s)",
            application_values(request.form),
        )
        flash("Application added.", "success")
        return redirect(url_for("applications"))
    return render_template("application_form.html", application={}, jobs=job_options(),
                           statuses=STATUSES, interview={}, action="Add")


@app.route("/applications/<int:application_id>/edit", methods=["GET", "POST"])
def edit_application(application_id):
    application = query_one(
        "SELECT * FROM applications WHERE application_id = %s", (application_id,))
    if not application:
        flash("Application not found.", "danger")
        return redirect(url_for("applications"))
    if request.method == "POST":
        error = validate_application(request.form)
        if error:
            flash(error, "danger")
            return render_template("application_form.html", application=request.form,
                                   jobs=job_options(), statuses=STATUSES,
                                   interview=interview_from_form(request.form), action="Edit")
        execute(
            "UPDATE applications SET job_id=%s, application_date=%s, status=%s, "
            "resume_version=%s, cover_letter_sent=%s, interview_data=%s "
            "WHERE application_id=%s",
            application_values(request.form) + (application_id,),
        )
        flash("Application updated.", "success")
        return redirect(url_for("applications"))
    return render_template("application_form.html", application=application,
                           jobs=job_options(), statuses=STATUSES,
                           interview=parse_interview(application["interview_data"]),
                           action="Edit")


@app.route("/applications/<int:application_id>/delete", methods=["POST"])
def delete_application(application_id):
    execute("DELETE FROM applications WHERE application_id = %s", (application_id,))
    flash("Application deleted.", "success")
    return redirect(url_for("applications"))

# ---------- Job Match ----------

def calculate_matches(user_skills):
    """Rank jobs by the percentage of their required skills the user has."""
    have = {skill.lower() for skill in user_skills}
    rows = query_all(
        "SELECT j.job_id, j.job_title, j.requirements, co.company_name FROM jobs j "
        "LEFT JOIN companies co ON j.company_id = co.company_id"
    )
    results = []
    for row in rows:
        required = parse_requirements(row["requirements"])
        if not required:
            continue
        matched = [s for s in required if s.lower() in have]
        missing = [s for s in required if s.lower() not in have]
        results.append({
            "job_title": row["job_title"],
            "company_name": row["company_name"],
            "matched": matched,
            "missing": missing,
            "total": len(required),
            "percent": round(100 * len(matched) / len(required)),
        })
    results.sort(key=lambda r: (-r["percent"], r["job_title"]))
    return results


@app.route("/job-match", methods=["GET", "POST"])
def job_match():
    skills_text = ""
    results = None
    if request.method == "POST":
        skills_text = request.form["skills"]
        skills = skills_from_text(skills_text)
        if not skills:
            flash("Please enter at least one skill.", "danger")
        else:
            results = calculate_matches(skills)
    return render_template("job_match.html", skills_text=skills_text, results=results)


if __name__ == "__main__":
    app.run(debug=True)