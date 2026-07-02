from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
from dotenv import load_dotenv
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


def get_db_connection():
    host = os.getenv("MYSQL_HOST", "localhost")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DB", "ai_solutions2")
    if database == "ai_solutions":
        print("Warning: MYSQL_DB is set to ai_solutions; overriding to ai_solutions2")
        database = "ai_solutions2"
    port = int(os.getenv("MYSQL_PORT", "3306"))

    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        charset="utf8mb4",
        autocommit=False,
    )

    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cur.execute(f"USE `{database}`")
        print(f"Connected to database: {database}")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS inquiries (
                id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone_number VARCHAR(30) DEFAULT NULL,
                company_name VARCHAR(150) DEFAULT NULL,
                country VARCHAR(100) DEFAULT NULL,
                job_title VARCHAR(100) DEFAULT NULL,
                job_details TEXT NOT NULL,
                status ENUM('Pending','In Progress','Completed') NOT NULL DEFAULT 'Pending',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                KEY idx_inquiries_status (status),
                KEY idx_inquiries_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_users (
                id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'admin',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci
            """
        )

    return conn


def ensure_default_admin_user():
    default_username = os.getenv("ADMIN_USERNAME", "admin")
    default_password = os.getenv("ADMIN_PASSWORD", "admin")
    default_email = os.getenv("ADMIN_EMAIL", "admin@aisolutions.com")

    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM admin_users WHERE username = %s LIMIT 1",
                    (default_username,),
                )
                existing = cursor.fetchone()

                if existing is None:
                    cursor.execute(
                        "INSERT INTO admin_users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                        (default_username, default_email, generate_password_hash(default_password), "admin"),
                    )
                else:
                    cursor.execute(
                        "UPDATE admin_users SET email = %s, password = %s, role = %s WHERE id = %s",
                        (default_email, generate_password_hash(default_password), "admin", existing[0]),
                    )
            conn.commit()
        finally:
            conn.close()
    except pymysql.Error as db_error:
        print(f"Admin seed DB error: {db_error}")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if "admin_id" in session:
        return redirect(url_for("admin_dashboard"))

    if request.method == "GET":
        return render_template("admin_login.html")

    error = None
    if request.method == "POST":
        ensure_default_admin_user()
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        if not username or not password:
            error = "Invalid username or password."
        else:
            try:
                conn = get_db_connection()
                try:
                    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                        cursor.execute(
                            "SELECT id, username, password, role FROM admin_users WHERE username = %s LIMIT 1",
                            (username,),
                        )
                        admin = cursor.fetchone()
                finally:
                    conn.close()
            except pymysql.Error as db_error:
                print(f"Admin login DB error: {db_error}")
                error = "Unable to verify login right now."
            else:
                stored_hash = (admin or {}).get("password", "") if admin else ""
                password_ok = False
                if stored_hash:
                    try:
                        password_ok = check_password_hash(stored_hash, password)
                    except ValueError:
                        password_ok = False

                if admin and password_ok:
                    session.clear()
                    session["admin_id"] = admin["id"]
                    session["admin_username"] = admin["username"]
                    session["admin_role"] = admin["role"]
                    return redirect(url_for("admin_dashboard"))

                error = "Invalid username or password."

    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    message = session.pop("dashboard_message", None)

    try:
        conn = get_db_connection()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, full_name, email, company_name, country, status, created_at
                    FROM inquiries
                    ORDER BY created_at DESC
                    """
                )
                inquiries = cursor.fetchall()

                cursor.execute("SELECT COUNT(*) AS total FROM inquiries")
                total = cursor.fetchone()["total"] or 0

                cursor.execute("SELECT COUNT(*) AS pending FROM inquiries WHERE status = 'Pending'")
                pending = cursor.fetchone()["pending"] or 0

                cursor.execute("SELECT COUNT(*) AS in_progress FROM inquiries WHERE status = 'In Progress'")
                in_progress = cursor.fetchone()["in_progress"] or 0

                cursor.execute("SELECT COUNT(*) AS completed FROM inquiries WHERE status = 'Completed'")
                completed = cursor.fetchone()["completed"] or 0
        finally:
            conn.close()
    except pymysql.Error as db_error:
        print(f"Admin dashboard DB error: {db_error}")
        inquiries = []
        total = pending = in_progress = completed = 0
        error = "Unable to load inquiries right now."
    else:
        error = None

    stats = {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
    }

    return render_template("admin_dashboard.html", inquiries=inquiries, stats=stats, error=error, message=message)


@app.route("/admin/inquiries/<int:inquiry_id>/status", methods=["POST"])
def update_inquiry_status(inquiry_id):
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    new_status = (request.form.get("status") or "").strip()
    allowed_statuses = {"Pending", "In Progress", "Completed"}

    if new_status not in allowed_statuses:
        session["dashboard_message"] = "Invalid inquiry status."
        return redirect(url_for("admin_dashboard"))

    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE inquiries SET status = %s WHERE id = %s",
                    (new_status, inquiry_id),
                )
            conn.commit()
        finally:
            conn.close()
    except pymysql.Error as db_error:
        print(f"Update inquiry status DB error: {db_error}")
        session["dashboard_message"] = "Unable to update the inquiry status right now."
    else:
        session["dashboard_message"] = "Inquiry status updated successfully."

    return redirect(url_for("admin_dashboard"))


@app.route("/contact", methods=["POST"])
def contact():
    data = request.form
    required_fields = [
        ("full_name", "Full Name"),
        ("email", "Email"),
        ("job_details", "Job Details"),
    ]
    field_names = [
        "full_name",
        "email",
        "phone_number",
        "company_name",
        "country",
        "job_title",
        "job_details",
    ]

    values = {}
    for field_name in field_names:
        values[field_name] = (data.get(field_name) or "").strip()

    missing = [label for field_name, label in required_fields if not values[field_name]]

    if missing:
        print(f"Contact form validation failed. Missing: {', '.join(missing)}")
        return jsonify({"success": False, "message": f"Please complete the required fields: {', '.join(missing)}."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO inquiries
                (full_name, email, phone_number, company_name, country, job_title, job_details)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    values["full_name"],
                    values["email"],
                    values["phone_number"],
                    values["company_name"],
                    values["country"],
                    values["job_title"],
                    values["job_details"],
                ),
            )
            conn.commit()
            return jsonify({"success": True, "message": "Thank you. Your inquiry has been captured successfully."})
        except pymysql.Error as db_error:
            conn.rollback()
            print(f"MySQL insert error: {db_error}")
            return jsonify({"success": False, "message": "We could not save your inquiry right now. Please try again later."}), 500
        finally:
            cursor.close()
            conn.close()
    except pymysql.Error as db_error:
        print(f"MySQL connection error: {db_error}")
        return jsonify({"success": False, "message": "Could not connect to the database. Please ensure XAMPP MySQL is running."}), 500
    except Exception as exc:
        print(f"Unexpected contact form error: {exc}")
        return jsonify({"success": False, "message": "Submission failed due to an unexpected error."}), 500


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False, host="0.0.0.0", port=5000)
