import json
import os
import requests
from pathlib import Path
import openai
from PIL import Image
import io
import hashlib


def generate_images_for_tree_nodes(client, path):
    """
    Read tree_data.json, generate images for leaf nodes, and update JSON with image paths
    """
    json_path = Path(path)  # In same directory
    images_dir = Path("generated_images")
    images_dir.mkdir(exist_ok=True)
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        print(f"Loaded tree data with {len(data.get('nodes', []))} nodes")
    except Exception as e:
        print(f"Error loading {json_path}: {e}")
        return False
    
    nodes = data.get('nodes', [])
    # Process each node
    processed_count = 0
    for i, node in enumerate(nodes):
        if 'id' not in node or node['id'].startswith('Inner'):
            continue
            
        node_id = node['id']
        print(f"node {i+1}: {node_id[:50]}...")
        PROMPT = f"""Create an image which conveys the following message using a simple visual description. Do not use any text, rather attempt to convey the look and feel of the message through common imagery. For instance, we typically associate a running man looking at his watch with being late for a bus. The message is: 
        {node_id}"""
        
        # Generate filename
        safe_filename = sanitize_filename(node_id)
        image_filename = f"{safe_filename}.png"
        image_path = images_dir / image_filename
        
        # Skip if image already exists
        if image_path.exists():
            print(f"Image already exists: {image_filename}")
            relative_path = f"generated_images/{image_filename}"
            node['image_path'] = relative_path
            node['has_generated_image'] = True
            processed_count += 1
            continue
        
        # Generate image with DALL-E
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=PROMPT,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            # Download and save image
            image_url = response.data[0].url
            if download_and_save_image(image_url, image_path):
                # Add relative path to node
                relative_path = f"generated_images/{image_filename}"
                node['image_path'] = relative_path
                node['image_prompt'] = PROMPT
                node['has_generated_image'] = True
                processed_count += 1
                print(f"✓ Generated: {image_filename}")
            else:
                node['has_generated_image'] = False
                print(f"✗ Failed to save: {image_filename}")
                
        except Exception as e:
            print(f"✗ Error generating image for '{node_id[:30]}...': {e}")
            node['has_generated_image'] = False
    
    # Save updated JSON
    try:
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"✗ Error saving JSON: {e}")
        return False
    return True

def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*\n\r\t'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    filename = filename.replace(' ', '_').replace('.', '').replace(',', '').replace('!', '').replace('?', '')
    return filename.strip('_')

def download_and_save_image(url, image_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image = image.resize((512, 512), Image.Resampling.LANCZOS)
        image.save(image_path, 'PNG', optimize=True)
        return True
        
    except Exception as e:
        print(f"Error downloading/saving image: {e}")
        return False

if __name__ == "__main__":
    API_KEY = os.getenv('OPENAI_API_KEY')
    client = openai.OpenAI(api_key=API_KEY)
    generate_images_for_tree_nodes(client,"tree_data.json")