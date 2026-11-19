import os
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db, query_all, query_one, execute

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")


@app.route("/")
def dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS count FROM applications")
    total = cursor.fetchone()["count"]
    cursor.close()
    conn.close()
    return render_template("dashboard.html", total=total)


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


if __name__ == "__main__":
    app.run(debug=True)