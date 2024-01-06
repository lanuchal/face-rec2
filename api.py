from flask import Flask, jsonify, request
import os
from werkzeug.utils import secure_filename
from train import  train_face
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_next_filename(directory, user_id):
    index = 0
    base_filename = secure_filename(user_id)
    filename = f"{base_filename}_{index}.jpg"
    while os.path.exists(os.path.join(directory, filename)):
        index += 1
        filename = f"{base_filename}_{index}.jpg"
    return filename

# @app.route('/findAll', methods=['GET']) 
# def findAll(): 
#     if(request.method == 'GET'): 
#         data = {"data": "Hello World"} 
#         return jsonify(data) 

# @app.route('/findOne', methods=['GET'])
# def findOne():
#     user_id = request.form['user_id']
#     print(user_id)
# Read one item

def resFail(msg):
    return {
        "status": False,
        "data": [],
        "message": msg
    }

@app.route('/train', methods=['POST'])
def trainAll():
    train_face()
    response = {
        "status": True,
        "data": [],
        "message": "Train successfully"
    }
    return jsonify(response)

@app.route('/user', methods=['GET'])
def findAll():
    if request.method == 'GET':
        try:
            files = [file for file in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, file))]
            unique_prefixes = set()
            if not files:
                return jsonify(resFail("File not found"))

            for filename in files:
                prefix = filename.split('_')[0]
                unique_prefixes.add(prefix)

            response_data = [{"username": prefix} for prefix in unique_prefixes]

            response = {
                "status": True,
                "data": response_data,
                "message": "Find all successfully"
            }
        except Exception as e:
            response = resFail(str(e)) 

        return jsonify(response)


@app.route('/user/<string:user_id>', methods=['GET'])
def get_item(user_id):
    try:
        files = [file for file in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, file))]
        unique_prefixes = set()

        for filename in files:
            prefix = filename.split('_')[0]
            if user_id == prefix:
                unique_prefixes.add(filename)
        # print(unique_prefixes)
        
        if not unique_prefixes:
            return jsonify(resFail("File not found"))

        response_data = [{"filename": prefix} for prefix in unique_prefixes]
        response = {
            "status": True,
            "data": response_data,
            "message": "Find user_id successfully"
        }
    except Exception as e:
        response = resFail(str(e)) 

    return jsonify(response)

@app.route('/user/<string:user_id>', methods=['DELETE'])
def delete(user_id):
    try:
        files = [file for file in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, file))]
        unique_prefixes = set()
        check = False

        for filename in files:
            prefix = filename.split('_')[0]
            if user_id == prefix:
                check = True
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                os.remove(file_path)
        
        if not check:
            return jsonify(resFail("user_id not found"))
            
        response = {
                "status": True,
                "data": [],
                "message": "delete successfully"
            }

    except Exception as e:
        response = resFail(str(e)) 

    return jsonify(response)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the POST request has the file part and user_id
    if 'file' not in request.files or 'user_id' not in request.form:
        return jsonify(error='No file or user_id part')

    file = request.files['file']
    user_id = request.form['user_id']

    # If the user does not select a file, the browser may send an empty file
    if file.filename == '':
        return jsonify(error='No selected file')

    # Securely save the file with a unique filename
    filename = get_next_filename(app.config['UPLOAD_FOLDER'], user_id)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    response = {
        "status": False,
        "data": [],
        "filename": filename,
        "message": "File uploaded successfully"
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5023)

    
