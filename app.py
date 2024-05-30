import os
import re
from flask import Flask, request, jsonify
import git

app = Flask(__name__)

REPO_DIR = "repositories"

@app.route('/clone', methods=['POST'])
def clone_repo():
    data = request.get_json()
    repo_url = data.get('url')
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    repo_path = os.path.join(REPO_DIR, repo_name)
    
    if not os.path.exists(REPO_DIR):
        os.makedirs(REPO_DIR)

    if not os.path.exists(repo_path):
        git.Repo.clone_from(repo_url, repo_path)
        return jsonify({"message": f"Repository {repo_name} cloned successfully"}), 200
    else:
        return jsonify({"message": f"Repository {repo_name} already exists"}), 400

def extract_content_from_repo(repo_path):
    content_dict = {}
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r', errors='ignore') as f:
                try:
                    content = f.read()
                    content_dict[file_path] = content
                    print(f"Indexed {file_path}")
                except Exception as e:
                    print(f"Could not read file {file_path}: {e}")
    return content_dict

@app.route('/index', methods=['POST'])
def index_repo():
    data = request.get_json()
    
    if 'repo_name' not in data:
        return jsonify({"message": "Missing 'repo_name' in request"}), 400
    
    repo_name = data['repo_name']
    repo_path = os.path.join(REPO_DIR, repo_name)
    
    if not os.path.exists(repo_path):
        return jsonify({"message": f"Repository {repo_name} does not exist"}), 400
    
    content_dict = extract_content_from_repo(repo_path)
    return jsonify({"indexed_files": list(content_dict.keys())}), 200

if __name__ == '__main__':
    app.run(debug=True)