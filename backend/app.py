from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    conn = sqlite3.connect("../users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", 
                   (data["username"], data["password"]))
    user = cursor.fetchone()
    return jsonify({"success": bool(user)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)