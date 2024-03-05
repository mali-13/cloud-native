import json
import logging

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    app.logger.info("hello endpoint called")
    return "Hello World!"


@app.route("/status")
def status():
    app.logger.info("status endpoint called")
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype="application/json",
    )
    return response


@app.route("/metrics")
def metrics():
    app.logger.info("metrics endpoint called")
    response = app.response_class(
        response=json.dumps(
            {
                "status": "success",
                "code": 0,
                "data": {"UserCount": 140, "UseCountActive": 23},
            }
        ),
        status=200,
        mimetype="application/json",
    )
    return response


if __name__ == "__main__":
    logging.basicConfig(filename="app.log", level=logging.DEBUG)
    app.run(host="0.0.0.0")
