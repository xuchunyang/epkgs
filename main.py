from flask import Flask, g, make_response, abort
import os
import sqlite3
import json

app = Flask(__name__)

# $ wget https://raw.githubusercontent.com/emacsmirror/epkgs/master/epkg.sqlite
# FIXME: The database should be updated periodically
app.config.from_object(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, "epkg.sqlite"),
))
app.config.from_envvar("FLASK_SETTING", silent=True)

def connect_db():
    rv = sqlite3.connect(app.config["DATABASE"])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()

@app.route("/")
def index():
    response = make_response("Web API for https://github.com/emacsmirror/epkgs")
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route("/<name>")
def package(name):
    db = get_db()
    cur = db.execute("select * from packages where name = '\"{}\"'".format(name))
    pkg = cur.fetchone()
    if pkg:
        data = json.dumps(dict((k, pkg[k]) for k in pkg.keys()))
        response = make_response(data)
        response.headers["Content-Type"] = "text/json"
        return response
    else:
        abort(404)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8080)
