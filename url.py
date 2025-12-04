import random
import string

from flask import Blueprint, render_template, request, redirect
from .db import get_db

bp = Blueprint("url", __name__)


def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    short_code = "".join(random.choice(chars) for _ in range(length))
    return short_code


def get_short_urls():
    db = get_db()

    rows = db.execute(
        "SELECT short_code, original_url, created_at FROM url ORDER BY created_at DESC"
    ).fetchall()
    
    urls = [
        {
            "short_code": row["short_code"],
            "original_url": row["original_url"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    
    return urls


@bp.route("/create_url", methods=["POST", "GET"])
def create_updated_url():
    db = get_db()
    if request.method == "POST":
        long_url = request.form.get("url")

        if not long_url.startswith(("http://", "https://")):
            long_url = "http://" + long_url

        short_code = generate_short_code()
        while db.execute(
            "SELECT 1 FROM url WHERE short_code = ?", (short_code,)
        ).fetchone():
            short_code = generate_short_code()

        db.execute(
            "INSERT INTO url (short_code, original_url) VALUES (?, ?)",
            (short_code, long_url),
        )
        db.commit()

        full_short_url = request.host_url + short_code

        return render_template(
            "create_short_url.html", new_url=full_short_url, old_url=long_url
        )

    return render_template("create_short_url.html", new_url="", old_url="")


@bp.route("/<short_code>")
def redirect_to_url(short_code):
    db = get_db()
    
    row = db.execute(
        "SELECT id, original_url FROM url WHERE short_code = ?", 
        (short_code,)
    ).fetchone()
    
    if row:
        db.execute(
            "UPDATE url SET click_count = click_count + 1 WHERE id = ?",
            (row["id"],)
        )
        db.commit()
        
        return redirect(row["original_url"])
    else:
        return render_template("error.html", error="URL not found"), 404


@bp.route("/retrieve_url", methods=["POST", "GET"])
def retrieve_original_url():
    original_url = None
    error = None

    if request.method == "POST":
        short_url = request.form.get("short_url")

        if short_url:
            if short_url.startswith(request.host_url):
                short_code = short_url.replace(request.host_url, "")
            else:
                short_code = short_url

            db = get_db()
            row = db.execute(
                "SELECT original_url FROM url WHERE short_code = ?", (short_code,)
            ).fetchone()

            if row:
                original_url = row["original_url"]
            else:
                error = "Short URL not found!"

        else:
            error = "Please provide a short URL!"

    return render_template(
        "retrieve_original_url.html", original_url=original_url, error=error
    )


@bp.route("/update_url", methods=["POST", "GET"])
def update_short_url():
    error = None
    success = None
    original_url = None
    updated_url = None

    if request.method == "POST":
        short_url = request.form.get("short_url")

        if short_url.startswith(request.host_url):
            short_code = short_url.replace(request.host_url, "", 1)
        else:
            short_code = short_url

        db = get_db()
        row = db.execute(
            "SELECT original_url FROM url WHERE short_code = ?", (short_code,)
        ).fetchone()

        if row:
            original_url = row["original_url"]
            new_code = generate_short_code()

            while db.execute(
                "SELECT 1 FROM url WHERE short_code = ?", (new_code,)
            ).fetchone():
                new_code = generate_short_code()

            db.execute(
                "UPDATE url SET short_code = ?, updated_at = CURRENT_TIMESTAMP WHERE original_url = ?",
                (new_code, original_url),
            )
            db.commit()
            success = "Short URL updated successfully!"
            updated_url = request.host_url + new_code
        else:
            error = "Short URL not updated."

    return render_template(
        "update_short_url.html",
        original_url=original_url,
        updated_url=updated_url,
        error=error,
        success=success,
    )


@bp.route("/delete_url", methods=["GET", "POST"])
def delete_short_url():
    error = None
    success = None

    db = get_db()

    if request.method == "POST":
        short_url = request.form.get("short_url")

        if short_url.startswith(request.host_url):
            short_code = short_url.replace(request.host_url, "", 1)
        else:
            short_code = short_url

        row = db.execute(
            "SELECT original_url FROM url WHERE short_code = ?", (short_code,)
        ).fetchone()

        if row:
            db.execute("DELETE FROM url WHERE short_code = ?", (short_code,))
            db.commit()
            success = f"Short URL '{short_code}' deleted successfully!"
        else:
            error = "Short URL not found or could not be deleted."

    urls = get_short_urls()

    return render_template(
        "delete_short_url.html",
        urls=urls,
        error=error,
        success=success,
    )

@bp.route("/stats_url", methods=["GET"])
def stats():
    error = None
    success = None
    
    try:
        urls = get_short_urls_with_stats()
    except Exception as e:
        error = f"Error loading statistics: {str(e)}"
        urls = []
    
    return render_template(
        "get_url_stats.html",
        urls=urls,
        error=error,
        success=success,
    )


def get_short_urls_with_stats():
    db = get_db()
    
    urls = db.execute(
        """
        SELECT 
            id,
            short_code,
            original_url,
            created_at,
            updated_at,
            click_count as clicks
        FROM url
        ORDER BY created_at DESC
        """,
    ).fetchall()
    
    return urls
