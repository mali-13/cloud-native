import logging
import sqlite3

from flask import (
    Flask,
    jsonify,
    json,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    make_response,
)


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = "your secret key"

logger = app.logger

# Configure the logger
formatter = logging.Formatter(
    "%(levelname)s:%(module)s:%(asctime)s, %(message)s", datefmt="%m/%d/%Y, %H:%M:%S"
)
logger.handlers[0].setFormatter(formatter)
logger.setLevel(logging.DEBUG)


# Define the main route of the web application
@app.route("/")
def index():
    connection = get_db_connection()
    posts = connection.execute("SELECT * FROM posts").fetchall()
    connection.close()
    return render_template("index.html", posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route("/<int:post_id>")
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logger.info(f"Article not found. Article {post_id} was not found")
        return render_template("404.html"), 404
    else:
        logger.info(f"Article retrieved. Article {post['title']} retrieved!")
        return render_template("post.html", post=post)


# Define the About Us page
@app.route("/about")
def about():
    logger.info("About page retrieved!")
    return render_template("about.html")


# Define the post creation functionality
@app.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        else:
            connection = get_db_connection()
            connection.execute(
                "INSERT INTO posts (title, content) VALUES (?, ?)", (title, content)
            )
            connection.commit()
            connection.close()
            logger.info(f"Article created!")
            return redirect(url_for("index"))

    return render_template("create.html")


@app.route("/healthz")
def healthz():
    connection = get_db_connection()
    posts_table_exists = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='posts'"
    ).fetchone()
    connection.close()

    if posts_table_exists is None:
        return make_response(jsonify({"result": "ERROR - unhealthy"}), 500)

    return jsonify({"result": "OK - healthy"})


@app.route("/metrics")
def metrics():
    connection = get_db_connection()
    post_count = connection.execute(
        "SELECT COUNT(*) as posts_count FROM posts"
    ).fetchone()[0]
    db_connection_count = 1
    connection.close()

    metrics = {"post_count": post_count, "db_connection_count": db_connection_count}

    return jsonify(metrics)


# start the application on port 3111
if __name__ == "__main__":
    app.run(host="0.0.0.0", port="3111")
