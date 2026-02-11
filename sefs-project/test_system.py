"""Integration test for SEFS system"""

import time
import requests
from pathlib import Path

API_BASE = "http://localhost:8000"


def test_health():
    """Test if API is running"""
    response = requests.get(f"{API_BASE}/health")
    print(f"✅ Health check: {response.json()}")
    return response.status_code == 200


def test_files():
    """Test file detection"""
    time.sleep(3)  # Wait for processing
    response = requests.get(f"{API_BASE}/files")
    data = response.json()
    print(f"✅ Files detected: {data['count']}")
    return data['count'] > 0


def test_clusters():
    """Test clustering"""
    response = requests.get(f"{API_BASE}/clusters")
    data = response.json()
    clusters = data.get('clusters', {})
    print(f"✅ Clusters created: {len(clusters)}")
    for cid, info in clusters.items():
        print(f"   Cluster {cid}: {info['count']} files")
    return len(clusters) > 0


def test_folders():
    """Test OS folders"""
    response = requests.get(f"{API_BASE}/folders")
    data = response.json()
    folders = data.get('folders', [])
    print(f"✅ OS folders created: {len(folders)}")
    for folder in folders:
        print(f"   {folder['name']}: {folder['count']} files")
    return len(folders) > 0


def test_graph():
    """Test graph data"""
    response = requests.get(f"{API_BASE}/graph")
    data = response.json()
    nodes = data.get('nodes', [])
    print(f"✅ Graph nodes: {len(nodes)}")
    return len(nodes) > 0


def test_generate_names():
    """Test AI name generation"""
    response = requests.post(f"{API_BASE}/generate-names")
    data = response.json()
    print(f"✅ Name generation: {data.get('status', 'unknown')}")
    return response.status_code == 200 and data.get('status') == 'name generation triggered'


def run_tests():
    """Run all tests"""
    print("=" * 50)
    print("SEFS System Integration Test")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("File Detection", test_files),
        ("Clustering", test_clusters),
        ("OS Folders", test_folders),
        ("Graph Data", test_graph),
        ("Generate Names", test_generate_names),
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n🧪 Testing: {name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {name} passed")
            else:
                print(f"❌ {name} failed")
        except Exception as e:
            print(f"❌ {name} failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{len(tests)} tests passed")
    print("=" * 50)


if __name__ == "__main__":
    run_tests()
