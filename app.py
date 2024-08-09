from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
import os
import string
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(".env")

app = Flask(__name__)

# Configure Flask app using environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(10), unique=True, nullable=False)

    def __init__(self, original_url, short_url):
        self.original_url = original_url
        self.short_url = short_url


def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(6))
    return short_url


@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data.get('url')

    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    short_url = generate_short_url()
    url = URL(original_url=original_url, short_url=short_url)
    db.session.add(url)
    db.session.commit()

    return jsonify({"short_url": request.host_url + short_url})


@app.route('/<short_url>', methods=['GET'])
def redirect_url(short_url):
    url = URL.query.filter_by(short_url=short_url).first_or_404()
    return redirect(url.original_url)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
