"""Test AI Naming Setup
Verifies that AI-powered naming is working correctly"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from dotenv import load_dotenv
load_dotenv("backend/.env")

def test_environment():
    """Test environment variables"""
    print("=" * 60)
    print("Testing Environment Configuration")
    print("=" * 60)
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("MODEL_NAME")
    
    print(f"\nGEMINI_API_KEY: {'✓ Set' if gemini_key else '✗ Not set'}")
    print(f"OPENAI_API_KEY: {'✓ Set' if openai_key else '✗ Not set'}")
    print(f"MODEL_NAME: {model_name if model_name else '✗ Not set'}")
    
    if not gemini_key and not openai_key:
        print("\n⚠️  No API keys found!")
        print("AI naming will use fallback (keyword-based naming)")
        print("\nTo enable AI naming:")
        print("1. Create backend/.env file")
        print("2. Add: GEMINI_API_KEY=your_key_here")
        print("3. Add: MODEL_NAME=gemini/gemini-1.5-flash")
        return False
    
    return True


def test_ai_namer():
    """Test AI namer initialization"""
    print("\n" + "=" * 60)
    print("Testing AI Namer Initialization")
    print("=" * 60)
    
    try:
        from ai_namer import get_ai_namer
        
        namer = get_ai_namer()
        
        if namer.ai_available:
            print("\n✓ AI namer initialized successfully")
            print(f"✓ Using: {'Gemini' if os.getenv('GEMINI_API_KEY') else 'OpenAI'}")
            return True
        else:
            print("\n⚠️  AI namer initialized but AI not available")
            print("Will use fallback naming")
            return False
            
    except Exception as e:
        print(f"\n✗ Error initializing AI namer: {e}")
        return False


def test_naming():
    """Test actual naming functionality"""
    print("\n" + "=" * 60)
    print("Testing AI Naming Functionality")
    print("=" * 60)
    
    try:
        from ai_namer import get_ai_namer
        
        namer = get_ai_namer()
        
        # Test data
        cluster_assignments = {
            "ai_paper_1.txt": 0,
            "ai_paper_2.txt": 0,
            "recipe_1.txt": 1,
            "recipe_2.txt": 1,
        }
        
        file_contents = {
            "ai_paper_1.txt": "Deep learning and neural networks for machine learning",
            "ai_paper_2.txt": "Transformer architecture and attention mechanisms",
            "recipe_1.txt": "Chocolate cake recipe with flour, sugar, and eggs",
            "recipe_2.txt": "Pasta carbonara with eggs, cheese, and pancetta",
        }
        
        print("\nGenerating names for 2 clusters...")
        names = namer.generate_names(cluster_assignments, file_contents)
        
        print("\nGenerated names:")
        for cluster_id, name in names.items():
            print(f"  Cluster {cluster_id}: {name}")
        
        # Check if names are meaningful (not just Cluster_X)
        meaningful = any(
            not name.startswith("Cluster_") and name != "Uncategorized"
            for name in names.values()
        )
        
        if meaningful:
            print("\n✓ AI naming is working!")
            return True
        else:
            print("\n⚠️  Using fallback naming (keyword-based)")
            return False
            
    except Exception as e:
        print(f"\n✗ Error testing naming: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SEFS AI Naming Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: Environment
    results.append(("Environment", test_environment()))
    
    # Test 2: AI Namer
    results.append(("AI Namer Init", test_ai_namer()))
    
    # Test 3: Naming
    results.append(("AI Naming", test_naming()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! AI naming is fully configured.")
    elif passed_count > 0:
        print("\n⚠️  Some tests passed. System will work with fallback naming.")
    else:
        print("\n❌ All tests failed. Please check your configuration.")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
