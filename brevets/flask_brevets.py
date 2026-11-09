"""Flask application for the ACP brevet time calculator."""

import logging
import secrets

import flask
from flask import request

import acp_times
import config


app = flask.Flask(__name__)
CONFIG = config.configuration(proxied=__name__ != "__main__")
app.secret_key = CONFIG.SECRET_KEY or secrets.token_hex(24)
app.debug = getattr(CONFIG, "DEBUG", False)
if app.debug:
    app.logger.setLevel(logging.DEBUG)


@app.route("/")
@app.route("/index")
def index():
    return flask.render_template("calc.html")


@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template("404.html"), 404


@app.route("/_calc_times")
def _calc_times():
    """Return control times for km, brevet, and an ISO 8601 start time."""
    km = request.args.get("km")
    brevet = request.args.get("brevet")
    start = request.args.get("start")
    if any(value is None or value == "" for value in (km, brevet, start)):
        return flask.jsonify(error="Provide km, brevet, and start."), 400
    try:
        opening = acp_times.open_time(km, brevet, start)
        closing = acp_times.close_time(km, brevet, start)
    except (ValueError, OverflowError):
        return flask.jsonify(error="Enter a valid distance, brevet, and start time."), 400
    return flask.jsonify(result={"open": opening, "close": closing})


if __name__ == "__main__":
    app.run(port=CONFIG.PORT, host="0.0.0.0")
