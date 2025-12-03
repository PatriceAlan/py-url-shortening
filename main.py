from flask import Flask, render_template, request, redirect
from flask_hot_reload import HotReload
import string
import random

app = Flask(__name__)
HotReload(app)

shortened_urls = {}


def generate_short_url(length=6):
    chars = string.ascii_letters + string.digits
    short_url = "".join(random.choice(chars) for _ in range(length))
    return short_url

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/create_url", methods=["POST", "GET"])
def create_new_short_url():
    if request.method == "POST":
        long_url = request.form.get("url")

        if not long_url.startswith(("http://", "https://")):
            long_url = "http://" + long_url

        short_code = generate_short_url()
        while short_code in shortened_urls:
            short_code = generate_short_url()

        shortened_urls[short_code] = long_url
        full_short_url = request.host_url + short_code

        return render_template(
            "create_short_url.html", new_url=full_short_url, old_url=long_url
        )
   
    return render_template("create_short_url.html", new_url="", old_url="")


@app.route("/retrieve_url", methods=["POST", "GET"])
def retrieve_original_url():
    original_url = None
    error = None
    short_url = None
    
    if request.method == "POST":
        short_url = request.form.get("short_url")
        
        if short_url:
        
            if short_url.startswith(request.host_url):
                short_code = short_url.replace(request.host_url, "")
            else:
                short_code = short_url
        
            original_url = shortened_urls.get(short_code)
            if not original_url:
                error = "Short URL not found!"
    
        else:
            error = "Please provide a short URL!"
    
    return render_template("retrieve_original_url.html", original_url=original_url, error=error)
    


@app.route("/<short_url>")
def redirect_url(short_url):
    long_url = shortened_urls.get(short_url)
    if long_url:
        return redirect(long_url)
    else:
        return "URL not found", 404


if __name__ == "__main__":
    app.run(debug=True)
