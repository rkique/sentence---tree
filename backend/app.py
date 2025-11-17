from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, UserInput
from utils import embed_sentence #get_perplexity
from utils import save_distance_matrix, generate_nj_tree, get_sentence_scores
import os
from datetime import datetime
import time

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'test_sentence_tree.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)
CORS(app)

# Create table (this reinitialization may be necessary if file deleted)
with app.app_context():
    db.create_all()

start_date = datetime(2025, 8, 7)
daily_prompt = None
prompts = None
days_difference = None
distance_matrix_path = None

with open('days.txt', 'r') as f:
    prompts = [line.strip() for line in f.readlines() if line.strip()]
        
def load_daily():
    global daily_prompt, days_difference
    #initialize once each day
    today = datetime.today()
    # days_difference = (today - start_date).days
    days_difference = 0 #15
    daily_prompt = prompts[days_difference % len(prompts)]
    daily_prompt = 'I love Brown because,.'
    print('[load_daily] loaded')
    return daily_prompt
    
@app.route('/api/daily-prompt')
def get_daily_prompt():
    return load_daily()

@app.route('/api/get_sentence_scores')
def sentence_scores():
    tree = generate_nj_tree(distance_matrix_path)
    scores = get_sentence_scores(tree)
    print(f'[sentence_scores] scores are {scores}')
    return jsonify(scores)

@app.route('/api/check-grammar', methods=['POST'])
def check_grammar():
    """Check grammaticality of text using GPT-2 perplexity"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        temp_input = type('UserInput', (), {'text': text})()
        perplexity = get_perplexity(text)
        is_gram = True
        
        return jsonify({
            'is_grammatical': is_gram,
            'perplexity': perplexity
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit-input', methods=['POST'])
def submit_input():
    global distance_matrix_path
    """Submit user input, store with embedding, and return tree data"""
    # try:
    data = request.json
    user_text = data['text'].strip()
    start, end = daily_prompt.split(',')
    user_sentence = start + ' ' + user_text + ' ' + end
    distance_matrix_path = f"distances/distances_{days_difference}.csv"
    #for debugging purposes
    if user_text == 'debug':
        print('[submit_input] debug, skipping to render...')
        user_sentence = UserInput.query.filter_by(day=days_difference).order_by(UserInput.id.desc()).first().text
    else:
        user_sentences = [row[0] for row in UserInput.query.with_entities(UserInput.text).all()]
        print('[DEBUG] Existing texts in DB:', user_sentences)

        if user_sentence in user_sentences:
            print(f"[submit-input] Text already exists in DB: {user_text}")
            return jsonify({'error': 'Text already exists in the database'}), 400
        
        embedding = embed_sentence(user_sentence)
        user_input = UserInput(text=user_sentence,\
                                embedding=embedding,\
                                day=days_difference)
        
        db.session.add(user_input)
        db.session.commit()
        # We can use one table, but save separate distance_matrices.
        entries = UserInput.query.filter_by(day=days_difference).all()
        save_distance_matrix(entries, distance_matrix_path)

    time.sleep(0.1)  # Small delay to ensure file is fully written
    if not os.path.exists(distance_matrix_path):
        error = "Distance matrix file was not created"
        print(f"[submit-input] {error}")
        raise FileNotFoundError(error)
    print(f'[using] {distance_matrix_path}')
    print(f'[submit_input] user_sentence: {user_sentence}')
    tree = generate_nj_tree(distance_matrix_path, user_input=user_sentence)
    tree_data = convert_tree_to_d3_format(tree)
    
    return jsonify({
        'status': 'success',
        'tree_data': tree_data
    })

def convert_tree_to_d3_format(tree):
    """Convert dendropy tree to D3.js force-directed graph format"""
    nodes = []
    links = []
    node_id_counter = 0
    
    node_map = {}
    root_node = tree.seed_node  # Get the actual root node of the tree
    for node in tree.preorder_node_iter():
        if node.taxon:
        # Leaf node
            if node.taxon.label.startswith('*'):
                # special user node
                isUser = True
            else:
                # other leaf node
                isUser = False
            node_id = node.taxon.label
            nodes.append({
                'id': node_id,
                'name': node_id,
                'isLeaf': True,
                'isUser': isUser
            })
        elif node == root_node:
            node_id = "Root"
            nodes.append({
                'id': node_id,
                'name': 'Root', #will render as Root
                'isRoot': True,
                'isLeaf': False
            })
        else:
            # Internal node
            node_id = f"Inner{node_id_counter}"
            node_id_counter += 1
            nodes.append({
                'id': node_id,
                'name': '',
                'isLeaf': False
            })
        node_map[node] = node_id
    
    # Process edges
    for node in tree.preorder_node_iter():
        if node.parent_node:
            parent_id = node_map[node.parent_node]
            child_id = node_map[node]
            distance = node.edge_length or 0.1
            
            links.append({
                'source': parent_id,
                'target': child_id,
                'distance': abs(distance)
            })
    
    return {
        'nodes': nodes,
        'links': links
    }

# Serve static files for the SPA
@app.route('/')
def serve_spa():
    return send_from_directory('dist', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(f'dist/{path}'):
        return send_from_directory('dist', path)
    else:
        return send_from_directory('dist', 'index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
