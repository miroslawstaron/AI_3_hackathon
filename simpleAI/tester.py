import subprocess

# Path to the Python script you want to run
script_path = "./test.py"

# Execute the script
try:
    result = subprocess.run(["python", script_path], capture_output=True, text=True, check=True)
    print("Output:\n", result.stdout)
    print("Error (if any):\n", result.stderr)
except subprocess.CalledProcessError as e:
    print(f"Script failed with return code {e.returncode}")
    print("Error output:\n", e.stderr)