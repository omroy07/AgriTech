from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Allow frontend (Live Server) to call API


forum_posts = []


@app.route('/forum', methods=['GET', 'POST'])
def forum_api():
    if request.method == 'POST':
        data = request.get_json()
        forum_posts.append(data)
        return jsonify({"status": "success"})
    else:
        return jsonify(forum_posts)


if __name__ == '__main__':
    app.run(port=5000, debug=True)