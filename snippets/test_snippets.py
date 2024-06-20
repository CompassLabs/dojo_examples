# test_runner.py
import subprocess
import glob
import os
import sys
sys.path.append("..")

def test_all_files():
    # Specify the directory where your other test files are located
    test_directory = '.'
    
    # Find all the test files in the specified directory
    test_files = glob.glob(os.path.join(test_directory, '**', '*.py'), recursive=True)
    print("a", test_files)
    
    for test_file in test_files:
        if "test" in test_file:
            continue
        print(test_file)
        # Run each test file using subprocess
        result = subprocess.run(['pytest', test_file], capture_output=True, text=True)
        
        # Check if the test run was successful
        ### assert result.returncode == 0, f"Test failed for {test_file}\n{result.stdout}\n{result.stderr}"


if __name__=="__main__":
    test_all_files()