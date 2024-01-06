import subprocess

# Run scan.py in a separate process
subprocess.Popen(['python', 'scan.py'])

# Run api.py in a separate process
subprocess.Popen(['python', 'api.py'])
