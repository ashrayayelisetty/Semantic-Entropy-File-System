import urllib.request
import json
import os
from pathlib import Path

try:
    response = urllib.request.urlopen('http://localhost:8000/graph')
    data = json.loads(response.read().decode())
    
    print(f"API returned {len(data['files'])} files")
    
    for file_info in data['files']:
        path = file_info['id'] # or 'path'
        exists = os.path.exists(path)
        print(f"File: {path}")
        print(f"  Exists (os.path): {exists}")
        print(f"  Exists (Path): {Path(path).exists()}")
        
        # Check parent dir
        parent = os.path.dirname(path)
        print(f"  Parent exists: {os.path.exists(parent)}")
        
except Exception as e:
    print(f"Error: {e}")
