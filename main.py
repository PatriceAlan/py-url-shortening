from flask import Flask, render_template, request, redirect
import string
import random

app = Flask(__name__)
shortened_urls = {}


def generate_short_url(length=6):
    chars = string.ascii_letters + string.digits
    short_url = "".join(random.choice(chars) for _ in range(length))
    return short_url


@app.route("/", methods=["POST", "GET"])
def home():
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
            "url_form.html", new_url=full_short_url, old_url=long_url
        )
   
    return render_template("url_form.html", new_url="", old_url="")


@app.route("/<short_url>")
def redirect_url(short_url):
    long_url = shortened_urls.get(short_url)
    if long_url:
        return redirect(long_url)
    else:
        return "URL not found", 404


if __name__ == "__main__":
    app.run()
