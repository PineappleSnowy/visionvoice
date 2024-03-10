import time

from flask import Flask, jsonify, render_template
import random

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('test.html')


@app.route('/getRandomPosition')
def get_random_position():
    x = random.randint(0, 350)  # Random x position within canvas
    y = random.randint(0, 250)  # Random y position within canvas
    return jsonify({'x': x, 'y': y})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
