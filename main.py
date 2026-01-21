# app.py
from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

# Stockage en mémoire des articles (utilisez une base de données en production)
articles = {}
next_id = 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/articles', methods=['GET'])
def get_articles():
    return jsonify(list(articles.values()))

@app.route('/api/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    if article_id in articles:
        return jsonify(articles[article_id])
    return jsonify({'error': 'Article non trouvé'}), 404

@app.route('/api/articles', methods=['POST'])
def create_article():
    global next_id
    data = request.json
    article = {
        'id': next_id,
        'title': data.get('title', 'Sans titre'),
        'blocks': data.get('blocks', []),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    articles[next_id] = article
    next_id += 1
    return jsonify(article), 201

@app.route('/api/articles/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    if article_id not in articles:
        return jsonify({'error': 'Article non trouvé'}), 404
    
    data = request.json
    articles[article_id]['title'] = data.get('title', articles[article_id]['title'])
    articles[article_id]['blocks'] = data.get('blocks', articles[article_id]['blocks'])
    articles[article_id]['updated_at'] = datetime.now().isoformat()
    return jsonify(articles[article_id])

@app.route('/api/articles/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    if article_id in articles:
        del articles[article_id]
        return jsonify({'message': 'Article supprimé'})
    return jsonify({'error': 'Article non trouvé'}), 404

if __name__ == '__main__':
    app.run(debug=True)