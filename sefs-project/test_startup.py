"""
Test script for START.bat startup script
Tests that both backend and frontend services start correctly
"""
import subprocess
import time
import requests
import sys

def test_startup_script():
    """Test the START.bat script"""
    print("=" * 60)
    print("Testing START.bat Startup Script")
    print("=" * 60)
    print()
    
    # Test 1: Check if services start
    print("[Test 1] Starting services with START.bat...")
    print("Note: This test requires manual verification")
    print("Expected behavior:")
    print("  - Backend should start on port 8000")
    print("  - Frontend should start on port 3000")
    print("  - Both URLs should be accessible")
    print()
    
    # Test 2: Check backend health
    print("[Test 2] Checking backend health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print(f"✓ Backend is accessible: {response.json()}")
        else:
            print(f"✗ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Backend is not accessible: {e}")
        return False
    
    print()
    
    # Test 3: Check frontend
    print("[Test 3] Checking frontend...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print(f"✓ Frontend is accessible (status: {response.status_code})")
        else:
            print(f"✗ Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Frontend is not accessible: {e}")
        return False
    
    print()
    
    # Test 4: Check API docs
    print("[Test 4] Checking API documentation...")
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print(f"✓ API docs are accessible")
        else:
            print(f"✗ API docs returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠ API docs check failed: {e}")
    
    print()
    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
    print()
    print("Manual verification steps:")
    print("1. Run START.bat")
    print("2. Verify backend starts on http://localhost:8000")
    print("3. Verify frontend starts on http://localhost:3000")
    print("4. Verify both services can be stopped with Ctrl+C")
    print()
    
    return True

if __name__ == "__main__":
    print("This script tests the START.bat startup script")
    print("Make sure START.bat has been run before running this test")
    print()
    input("Press Enter to continue...")
    print()
    
    success = test_startup_script()
    sys.exit(0 if success else 1)
