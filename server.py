from flask import Flask, request, jsonify
from main import process1, process2  # Assuming process2 exists and is to be imported

app = Flask(__name__)

@app.route('/')
def index(): 
    return jsonify({'message': 'Welcome'})

@app.route('/process1', methods=['POST'])
def process1_route():
    """Process the data using process1."""
    data = request.get_json()
    result = process1(data)  # Make sure process1 is designed to handle the input data appropriately
    return jsonify(result)

@app.route('/process2', methods=['POST'])
def process2_route():
    """Process the data using process2."""
    data = request.get_json()
    result = process2(data)  # Make sure process2 is designed to handle the input data appropriately
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='localhost', port=5001) # This will only allow connections from the same machine
    #app.run(host='0.0.0.0', port=5001) # This will allow connections from any machine in the same network
