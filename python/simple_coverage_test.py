"""Simple Coverage Test for Python Files"""

import os
import sys
import subprocess

def test_file_coverage(file_path):
    """Test coverage for a single file using subprocess"""
    try:
        # Run the file with coverage
        cmd = f"python -m coverage run --source=. {file_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {file_path} executed successfully")
            return True
        else:
            print(f"❌ {file_path} failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ {file_path} error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("SIMPLE COVERAGE TEST")
    print("=" * 60)
    
    # Clear any existing coverage data
    os.system("python -m coverage erase")
    
    # List of files to test
    files = [
        "python/step1_csv_import.py",
        "python/step2_nps_analysis.py",
        "python/step3_visualizations.py", 
        "python/step4_word_cloud.py",
        "python/step5_track_improvements.py",
        "python/step6_session_rankings.py",
        "python/step7_lowest_nps.py"
    ]
    
    # Test each file
    success_count = 0
    for file_path in files:
        if os.path.exists(file_path):
            if test_file_coverage(file_path):
                success_count += 1
        else:
            print(f"⚠️  {file_path} not found")
    
    print(f"\n📊 Results: {success_count}/{len(files)} files executed successfully")
    
    # Generate coverage report
    print("\n" + "=" * 60)
    print("COVERAGE REPORT")
    print("=" * 60)
    
    os.system("python -m coverage report --show-missing")
    
    # Generate HTML report
    os.system("python -m coverage html")
    print("\n📄 HTML report generated in htmlcov/ directory")

if __name__ == "__main__":
    main()
