import os
from flask import Flask, render_template


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    instance_path = os.path.join(os.path.dirname(__file__), "instance")
    os.makedirs(instance_path, exist_ok=True)

    database_path = os.path.join(instance_path, "py-url-shortening.sqlite")
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=database_path,
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    from . import db

    db.init_app(app)

    from . import url

    app.register_blueprint(url.bp)

    @app.route("/")
    def home():
        return render_template("home.html")

    return app
