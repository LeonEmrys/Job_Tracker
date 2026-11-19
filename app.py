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
if __name__ == "__main__":
    app.run(debug=True)