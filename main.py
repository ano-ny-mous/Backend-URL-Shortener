from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random, string

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# URL Model
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(6), unique=True, nullable=False)

# Generate a unique short code
def generate_short_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# Create database tables
with app.app_context():
    db.create_all()

# API Home Route
@app.route('/')
def home():
    return jsonify({"message": "URL Shortener API is running! Use /shorten to shorten URLs."})

# Shorten URL
@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    long_url = data.get('url')

    if not long_url:
        return jsonify({"error": "URL is required"}), 400

    short_code = generate_short_code()
    new_url = URL(long_url=long_url, short_code=short_code)
    db.session.add(new_url)
    db.session.commit()

    return jsonify({"short_url": f"https://{request.host}/{short_code}"})

# Redirect Short URL to Original URL
@app.route('/<short_code>')
def redirect_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first()
    if url:
        return redirect(url.long_url, code=302)
    return jsonify({"error": "Short URL not found"}), 404

# Run Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
