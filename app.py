from flask import Flask, request, jsonify
from main import find_tree_differences

app = Flask(__name__)

@app.route('/tree-differences', methods=['POST'])
def tree_differences():
    # Get the JSON data from the request body
    request_data = request.get_json()

    # Call the find_tree_differences function with the JSON data
    result = find_tree_differences(request_data)

    # Return the result as JSON
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
