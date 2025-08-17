
from sentence_transformers import SentenceTransformer
import numpy as np
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import math
from models import UserInput
import pandas as pd
import dendropy

# Load GPT-2 once
gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2")
print('[Utils] GPT-2 model loaded')
def get_perplexity(sentence):
    inputs = gpt2_tokenizer(sentence, return_tensors="pt")
    with torch.no_grad():
        outputs = gpt2_model(**inputs, labels=inputs["input_ids"])
        loss = outputs.loss
    return math.exp(loss.item())

def is_grammatical(entry, threshold=1000):
    perplexity = get_perplexity(entry.text)
    print(f"Sentence perplexity: {perplexity:.2f}")
    return perplexity < threshold

model_name = 'all-MiniLM-L6-v2'
model = SentenceTransformer(model_name)

def embed_sentence(sentence):
    return model.encode(sentence)

#With sentence scores, we can return the user score.

def get_sentence_scores(tree):
    scores = {}
    def walk(node, depth):
        # Get node label or fallback to a unique ID (e.g., id(node))
        label = None
        if node.taxon is not None:
            label = node.taxon.label
        elif node.label is not None:
            label = node.label
        else:
            label = str(id(node))
        scores[label] = 1 / (2 ** depth)
        for child in node.child_nodes():
            walk(child, depth + 1)
    root = tree.seed_node
    walk(root, 0)
    return scores
    
def save_distance_matrix(entries, filename="distances.csv"):
    embeddings = np.array([entry.embedding for entry in entries])
    labels = np.array([entry.text for entry in entries])
    # Normalize embeddings
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized = embeddings / norms
    # Cosine similarity matrix
    similarity_matrix = np.dot(normalized, normalized.T)
    # Convert similarity to distance
    distance_matrix = 1 - similarity_matrix
    # Create DataFrame with labels as row and column names
    df = pd.DataFrame(distance_matrix, index=labels, columns=labels)
    df.to_csv(filename)

def generate_nj_tree(filename="distances.csv", user_input=None):
    df_distances = pd.read_csv(filename, index_col=0)
    labels = df_distances.columns.tolist()
    taxon_namespace = dendropy.TaxonNamespace(labels)
    # Load the distance matrix from CSV
    pdm = dendropy.calculate.phylogeneticdistance.PhylogeneticDistanceMatrix.from_csv(
        src=filename,
        delimiter=',',
        is_first_row_column_names=True,
        taxon_namespace=taxon_namespace
    )
    tree_nj = pdm.nj_tree()
    #root the tree. 
    tree_nj.reroot_at_midpoint(update_bipartitions=True)
    #find user_input in the tree and add '*' to node.taxon.label
    if user_input:
        for node in tree_nj.preorder_node_iter():
            if node.taxon and node.taxon.label == user_input:
                print('[generate_nj_tree] user input labeled')
                node.taxon.label = '*' + node.taxon.label 
                break 
    return tree_nj
