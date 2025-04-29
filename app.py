from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb+srv://gominhanyang:J6o9RZpVGw4oIkPO@cluster0.eue69zf.mongodb.net/')
db = client['letter_app']
letters_collection = db['letters']

@app.route('/')
def home():
    return 'Hello, this is the letter app connected to MongoDB!'

@app.route('/write_letter', methods=['POST'])
def write_letter():
    data = request.json
    letter = {
        'sender': data.get('sender'),
        'content': data.get('content')
    }
    letters_collection.insert_one(letter)
    return jsonify({'msg': 'Letter saved successfully!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
