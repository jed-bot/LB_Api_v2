import os
import numpy as np
from keras.models import load_model
from keras.preprocessing import image

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'ingredient_classifier_200_epochs.h5')
model = load_model(MODEL_PATH)  # Load once at startup

def predict_image(img_path):
    """Process image and return predictions"""
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return model.predict(img_array)[0].tolist()