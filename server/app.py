import sys
import os

from flask import request, Flask, jsonify
from flask_cors import CORS

sys.path.append(os.path.join(os.path.abspath(os.path.curdir), '..'))
from search_engine.query import Query


DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

CORS(app)

querier = Query()
DEFAULTS = []


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


if "__main__" == __name__:
	app.run()

