from flask import Flask, request, jsonify
from dotenv import load_dotenv
from newsletter_trends_jonas.workflow import compile_workflow

app = Flask(__name__)

@app.route('/get_graph_state', methods=['POST'])
def get_graph_state():
    data = request.json
    
    app = compile_workflow()
    
    response = app.invoke({"country": data["country"],
                           "head": data["head"],
                           "k": data["k"],
                           "subjects": data["subjects"],
                           "favorite_team": data["favorite_team"]
                           }
                        )
    

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)