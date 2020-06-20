from flask import Flask, render_template, jsonify, request, abort, make_response
import json
app = Flask(__name__)

#URL routing
@app.route('/hp/influencers', methods = ["POST"])
def influencers():
    #get the influencers
    res_string = request.data.decode('utf-8')
    app.logger.info(res_string)
    req_dict = json.loads(res_string)
    if(req_dict['topic'].strip() != ""):
        #add stuff
        resp = make_response("influencers")
    else:
        #add stuff
        resp = make_response("biases")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

if __name__ == '__main__':	
	app.debug=True
	app.run('0.0.0.0', port = 2004)