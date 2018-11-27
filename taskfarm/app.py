import flask

app = flask.Flask(__name__)

@app.route('/getTask', methods=['GET'])
def getTask():
    return flask.jsonify({'task':1})

def main():
    app.run(debug=True)
    
if __name__ == '__main__':
    main()
