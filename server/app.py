from flask import request, Flask, jsonify
from flask_cors import CORS

import sys
import os
sys.path.append(os.path.join(os.path.abspath(os.path.curdir), '..'))
from search_engine.query import Query
import logging


def r(a):
	return open(a,"r+").read()


DEBUG = True

app = Flask(__name__, static_folder="ico")
app.config.from_object(__name__)

CORS(app)

querier = Query()
DEFAULTS = []


@app.route("/", methods=["POST","GET"])
def mn():
	if request.method == "GET":
		return r("a.html")
	else:
		try:
			m = r("result.html").replace(
                "<--Co-->",
                '\n'.join(querier.query(request.form['search']))
            )
		except:
			m = r("404.html")
		return m


@app.route("/query", methods=["GET", "POST"])
def query_fn():
    global DEFAULTS
    response_object = {'status': 'success'}
    if request.method == 'POST':
        query = request.get_data()
        print(query)
        DEFAULTS = [{'url': url, 'abstract': abstract} for url, abstract in querier.server_query(query)]
        response_object['defaults'] = DEFAULTS
        response_object['message'] = f'query succeed: {query}'
    else:
        response_object['defaults'] = DEFAULTS
    return jsonify(response_object)


@app.route("/about", methods=["GET"])
def mn1():
	return jsonify('pong!')


@app.route("/dev")
def mn2():
	return r("dev.html")


@app.route("/contact",methods=["GET","POST"])
def mn3():
	if (request.method == "GET"):
		return r("form.html").replace("sdfsdfzds","contact")
	else:
		rt = "\n\n\nEmail: "+request.form["email"]+"\n\nMessage: "+request.form["message"]
		open("con/data.txt","a").write(rt)
		return r("form.html").replace("sdfsdfzds","contact") + "<script>alert('Your response has been submitted');</script>"


@app.route("/feedback", methods=["GET","POST"])
def mn4():
	if (request.method == "GET"):
		return r("form.html").replace("message","feedback").replace("sdfsdfzds","feedback")
	else:
		rt = "\n\n\nEmail: "+request.form["email"]+"\n\nMessage: "+request.form["message"]
		open("con/data.txt","a").write(rt)
		return r("form.html").replace("message","feedback").replace("sdfsdfzds","feedback") +\
                "<script>alert('Your response has been submitted');</script>"


@app.route("/report")
def mn5():
	if (request.method == "GET"):
		return r("form.html").replace("message","issue").replace("sdfsdfzds","report")
	else:
		rt = "\n\n\nEmail: "+request.form["email"]+"\n\nMessage: "+request.form["message"]
		open("con/data.txt","a").write(rt)
		return r("form.html").replace("message","issue").replace("sdfsdfzds","report") +\
                "<script>alert('Your response has been submitted');</script>"


if "__main__" == __name__:
	app.run()

