from __future__ import division, print_function
import sys
import io
import os
import glob
import re
import numpy as np
import cv2

# Keras
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
from keras.preprocessing import image

# Flask utils
from flask import Flask, redirect, url_for, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Define a flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Model saved with Keras model.save()
MODEL_PATH = 'models/grape_disease_classifier.h5'
FILE_PATH_FINAL = None

# Load your trained model
model = load_model(MODEL_PATH)
model._make_predict_function() 
print('Model loaded. Start serving...')

def model_predict(img_path, model):
	img = cv2.imread(img_path)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	img = cv2.resize(img,(256,256))
	img = np.reshape(img,[1,256,256,3])
	disease = model.predict_classes(img)
	preds = disease[0]
	return preds

def assign_filepath(file_path):
    global FILE_PATH_FINAL
    FILE_PATH_FINAL = file_path
    

@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
	
@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']
        print(type(f))
        in_memory_file = io.BytesIO()
        f.save(in_memory_file)
        data = np.fromstring(in_memory_file.getvalue(), dtype=np.uint8)
        color_image_flag = 1
        img = cv2.imdecode(data, color_image_flag)
        img = cv2.resize(img,(256,256))

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        cv2.imwrite(file_path, img)
        '''f.save(file_path)'''
        assign_filepath(file_path)
        

        # Make prediction
        preds = model_predict(file_path, model)
        if preds == 0:
            return jsonify(dict(redirect='black_measles'))
        elif preds == 1:
             return jsonify(dict(redirect='black_rot'))
        elif preds == 2:
             return jsonify(dict(redirect='healthy'))
        elif preds == 3:
             return jsonify(dict(redirect='leaf_blight'))
        else:
            result = "none"
        return result
    return None
	
@app.route('/black_measles', methods=['GET', 'POST'])
def black_measles():
	return render_template('black_measles.html')

@app.route('/black_rot', methods=['GET', 'POST'])
def black_rot():
	return render_template('black_rot.html')

@app.route('/healthy', methods=['GET', 'POST'])
def healthy():
	return render_template('healthy.html')
	
@app.route('/leaf_blight', methods=['GET', 'POST'])
def leaf_blight():
	return render_template('leaf_blight.html')

@app.route('/file_path', methods=['GET','POST'])
def file_path():
    return FILE_PATH_FINAL
	
if __name__ == '__main__':
    '''app.run(port=5002, debug=True)'''
    # Serve the app with gevent
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
