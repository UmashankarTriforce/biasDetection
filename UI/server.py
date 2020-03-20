from flask import Flask, render_template, jsonify, request, abort, make_response
import json
app = Flask(__name__)

#URL routing
@app.route('/hp/influencers', methods = ["POST"])
def influencers():
    #get the influencers
    app.logger.info(request.data.decode('utf-8'))

    resp = make_response("influencers")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

if __name__ == '__main__':	
	app.debug=True
	app.run('0.0.0.0', port = 1729)