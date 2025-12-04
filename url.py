import random
import string

from flask import (
    Blueprint, render_template, request, redirect
)
from .db import get_db

bp = Blueprint('url', __name__)

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    short_code = "".join(random.choice(chars) for _ in range(length))
    return short_code


@bp.route("/create_url", methods=["POST", "GET"])
def create_new_short_url():
    db = get_db()
    if request.method == "POST":
        long_url = request.form.get("url")

        if not long_url.startswith(("http://", "https://")):
            long_url = "http://" + long_url

        short_code = generate_short_code()
        while db.execute("SELECT 1 FROM url WHERE short_code = ?", 
                         (short_code,)).fetchone():
            short_code = generate_short_code()
        
        db.execute(
            'INSERT INTO url (short_code, original_url) VALUES (?, ?)',
            (short_code, long_url)
        )
        db.commit()

        full_short_url = request.host_url + short_code

        return render_template(
            "create_short_url.html", new_url=full_short_url, old_url=long_url
        )

    return render_template("create_short_url.html", new_url="", old_url="")


@bp.route("/<short_code>")
def redirect_short_url(short_code):
    db = get_db()
    row = db.execute(
        "SELECT original_url FROM url WHERE short_code = ?",
        (short_code,)
    ).fetchone()
    
    if row:
        return redirect(row["original_url"])
    else:
        return "Short URL not found", 404
    


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
                "SELECT original_url FROM url WHERE short_code = ?",
                (short_code,)
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