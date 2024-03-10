import matplotlib.pyplot as plt
import numpy as np
import PIL
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
# Fl Model
batch_size = 32
img_height = 180
img_width = 180



import matplotlib.pyplot as plt
import numpy as np
import PIL
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from keras.models import load_model


def create_model_from_weights():
    data_augmentation = keras.Sequential(
    [
        layers.RandomFlip("horizontal",
                        input_shape=(img_height,
                                    img_width,
                                    3)),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1),
    ]
    )
    class_names = ['Cyclone', 'Earthquake', 'Flood', 'Wildfire']
    num_classes = len(class_names)


    model = Sequential([
    data_augmentation,
    layers.Rescaling(1./255),
    layers.Conv2D(16, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(32, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(64, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Dropout(0.2),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(num_classes, name="outputs")
    ])
    model.load_weights('model_weights.h5')
    return model


def predict(image_path):
    model = load_model('Local_model.keras')
    class_names = ['Cyclone', 'Earthquake', 'Flood', 'Wildfire']
    #url = 'https://cloudfront-us-east-2.images.arcpublishing.com/reuters/CL6SKCKZBVL7NPI3KSSIZCIUPA.jpg'

    #flood_path = tf.keras.utils.get_file('CL6SKCKZBVL7NPI3KSSIZCIUPA.jpg',origin=url)

    #image_path = tf.keras.utils.get_file('images.jpg') #path to the image

    #img = tf.keras.utils.load_img(
    #    flood_path, target_size=(img_height, img_width)
    #)
    #image_path ='images.jpg'

    img = tf.keras.utils.load_img(image_path, target_size=(img_height, img_width))

    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0) # Create a batch

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    print(
        "This image most likely belongs to {} with a {:.2f} percent confidence."
        .format(class_names[np.argmax(score)], 100 * np.max(score))
    )

def model2():
    model = tf.keras.models.load_model('model_PLS')
    class_names = ['Cyclone', 'Earthquake', 'Flood', 'Wildfire']
    print("AICICIICID\n\n\n\n")
    image_path ='images.jpg'
    img = tf.keras.utils.load_img(image_path, target_size=(224, 224))

    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0) /255.0 # Create a batch

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    print(
        "This image most likely belongs to {} with a {:.2f} percent confidence."
        .format(class_names[np.argmax(score)], 100 * np.max(score))
    )

    predictions2 = model.predict(img_array)
    predicted_class = np.argmax(predictions2, axis=1)[0]
    predicted_label = class_names[predicted_class]
    #correct = (predicted_label == true_class)
    
    # Print the result
    print(f"Image: {image_path}")
    #print(f"True Class: {true_class}")
    print(f"Predicted Class: {predicted_label}")
    #print(f"Correct: {correct}")
    print(f"Accuracy: {100 * np.max(predictions2)}%")
    print("-" * 50)




#model2()
#predict('images.jpg')

#model.save('Local_model.keras')