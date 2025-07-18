import os
import sys
import subprocess
from flask import Flask, render_template

app = Flask(__name__)

def run_tkinter_script(script_name):
    script_path = os.path.join('modules', script_name)
    print("Launching:", script_path)
    if not os.path.exists(script_path):
        print("Script not found:", script_path)
        return
    subprocess.Popen(
        [sys.executable, script_path],
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/disk_scheduling', methods=['GET'])
def disk_scheduling():
    print("disk_scheduling route hit!")
    run_tkinter_script('disk_scheduling.py')
    return '', 204

@app.route('/cpu_scheduling', methods=['GET'])
def cpu_scheduling():
    print("cpu_scheduling route hit!")
    run_tkinter_script('cpu_scheduling.py')
    return '', 204

@app.route('/memory_management', methods=['GET'])
def memory_management():
    print("memory_management route hit!")
    run_tkinter_script('memory_management.py')
    return '', 204

@app.route('/page_Replacement', methods=['GET'])
def page_replacement():
    print("page_replacement route hit!")
    run_tkinter_script('page_Replacement.py')
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
