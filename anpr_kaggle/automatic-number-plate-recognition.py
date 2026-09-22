import sys
import os
#!/usr/bin/env python
# coding: utf-8

# <p id="part0"></p>
# <p style="font-family: Arials; line-height: 2; font-size: 24px; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000">AUTOMATIC LICENSE NUMBER PLATE DETECTION AND RECOGNITION</p>
# <img src= "https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/Presentation/Notebook1.png?raw=true" width="100%" align="center"  hspace="5%" vspace="5%"/>
# <p style="font-family: Arials; font-size: 20px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">TABLE OF CONTENT</p>
# 
# <p style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part2" style="color:#000000">1. INTRODUCTION</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part3" style="color:#808080">1.1 USE CASES</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part4" style="color:#808080">1.2 PROJECT ARCHITECTURE</a></p>
# 
# <p  style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 2px;  text-align: center; color: #000000; line-height:1.3"><a href="#part5" style="color:#000000">2. LABELING</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part6" style="color:#808080">2.1 UNDERSTAND & COLLECT REQUIRED DATA</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part7" style="color:#808080">2.2 LABEL IMAGES</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part8" style="color:#808080">2.3 PARSING INFORMATION FROM XML</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part9" style="color:#808080">2.4 PARSING DATA FROM XML & CONVERTING IT INTO CSV</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part10" style="color:#808080">2.5 VERIFY THE DATA</a></p>
# 
# <p style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part11" style="color:#000000">3. DATA PROCESSING</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part12" style="color:#808080">3.1 READ DATA</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part13" style="color:#808080">3.2 SPLIT TRAIN AND TEST SET</a></p>
# 
# <p style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part14" style="color:#000000">4. DEEP LEARNING FOR OBJECT DETECTION</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part15" style="color:#808080">4.1 INCEPTION-RESNET-V2 MODEL BUILDING</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part16" style="color:#808080">4.2 INCEPTION-RESNET-V2 TRAINING & SAVE</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part17" style="color:#808080">4.3 TENSORBOARD </a></p>
# 
# <p style="font-family: Arials; font-size: 18px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part14" style="color:#000000">5. PIPELINE OBJECT DETECTION MODEL</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part19" style="color:#808080">5.1 MAKE PREDICTIONS</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part20" style="color:#808080">5.2 DE-NORMALIZE THE OUTPUT</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part21" style="color:#808080">5.3 BOUNDING BOX</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part22" style="color:#808080">5.4 CREATE PIPELINE</a></p>
# 
# <p style="font-family: Arials; font-size: 18px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part23" style="color:#000000">6. OPTICAL CHARACTER RECOGNITION - OCR</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part24" style="color:#808080">6.1 TESSERACT OCR</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part25" style="color:#808080">6.2 LIMITATIONS OF PYTESSERACT</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part26" style="color:#808080">6.3 EXTRACT NUMBER PLATE TEXT FROM IMAGE</a></p>
# 
# <p style="font-family: Arials; font-size: 18px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part27" style="color:#000000">7. NUMBER PLATE WEB APP</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part28" style="color:#808080">7.1 REQUERED TOOLS</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part29" style="color:#808080">7.2 FLASK APP</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part30" style="color:#808080">7.3 TEMPLATE INHERITANC</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part31" style="color:#808080">7.4 HTTP METHOD UPLOAD FILE IN FLASK</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part32" style="color:#808080">7.5 INTEGRATE NPD AND OCR TO FLASK APP</a></p>
# 
# <p style="font-family: Arials; font-size: 18px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part33" style="color:#000000">8. RAEAL TIME NUMBER PLATE RECOGNITIONT WITH YOLO</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part34" style="color:#808080">8.1 EXPLANATION OF REQUIRED DATA</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part35" style="color:#808080">8.2 DATA PREPARATION</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part36" style="color:#808080">8.3 TRAINING YOLO</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part37" style="color:#808080">8.4 PREDICTING RESULTS FROM YOLO</a></p>
# 
# <p  style="text-indent: 1vw; font-family: Arials; font-size: 14px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part38" style="color:#808080">8.5 REAL TIME OBJECT DETECTION</a></p>
# 
# <p style="font-family: Arials; font-size: 18px; font-style: normal; font-weight: bold; letter-spacing: 2px; text-align: center; color: #000000; line-height:1.3"><a href="#part39" style="color:#000000">9. CONCLUSION</a></p>
# 
# <p id="part2"></p>
# 
# # <span style="font-family: Arials; font-size: 20px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">1. INTRODUCTION</span>
# <hr style="height: 0.5px; border: 0; background-color: #000000">
# 
# <table><tr>
# <td> <img src= "https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/Presentation/Test.gif?raw=true" width="100%" align="center"  hspace="5%" vspace="5%"/> </td>
# <td> <img src= "https://user-images.githubusercontent.com/91852182/172154404-ccb2a6b5-deb4-4321-91ff-a8f13457b352.gif" width="100%" align="center"  hspace="5%" vspace="5%"/> </td>
# </tr></table>
# 
# In Today’s Day and Age Security has become one of the biggest concerns for any organization, and automation of such security is essential. However, many of the current solutions are still not robust in real-world situations, commonly depending on many constraints. In the following project, we will understand how to recognize License number plates using the Python programming language. We will utilize OpenCV for this project in order to identify the license number plates and the python pytesseract for the characters and digits extraction from the plate. As well this project will  presents a robust and efficient ALPR system based on the state-of-the-art YOLO object detector. We will Web App with a Python program that automatically recognizes the License Number Plate by the end of this journi. The results have shown that the trained neural network is able to perform with high accuracy of nearly 90-95 percent in recognizing license plates in low resolution images using this system.
# 
# <p id="part3"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">1.1 USE CASES</span>
# 
# License plate detection is identifying the part of the car that is predicted to be the number plate. Recognition is identifying the values that make up the license plate. License plate detection and recognition is the technology that uses computer vision to detect and recognize a license plate from an input image of a car. This technology applies in many areas. On roads, it is used to identify the cars that are breaking the traffic rules. In security, it is used to capture the license plates of the vehicles getting into and out of certain premises. In parking lots, it is used to capture the license plates of the cars being parked. The list of its applications goes on and on.
# 
# <img src= "https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/Presentation/Notebook2.png?raw=true" width="100%" align="center"  hspace="5%" vspace="5%"/>
# 
# <p id="part4"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">1.2 PROJECT ARCHITECTURE</span>
# 
# <img src= "https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/Presentation/Notebook3.png?raw=true" width="60%" align="center"  hspace="5%" vspace="5%"/>
# 
# In the below architecture *Figure 2*, there are six modules. Labeling, Training, Save Model, OCR and Pipeline, and RESTful API. The process is as follows. First, we will collect the image. Then we have to label images for object detection of License Plate or Number Plate using Image Annotation Tool [Github](https://github.com/Asikpalysik/Automatic-License-Plate-Detection/tree/main/labelImg-master) which is open-source software developed in python GUI. Then after labeling the image we will work on data preprocessing, build and train a deep learning object detection model (Inception Resnet V2) in TensorFlow 2. Once we have done with the Object Detection model training process, then using this model we will crop the image which contains the license plate which is also called the region of interest (ROI), and pass the ROI to Optical Character Recognition API Tesseract in Python (PyTesseract). As well extract text from images. Now, we will put it all together and build a Pipeline Deep Learning model. In the final module, we will learn to create a web app project using FLASK Python. With that, we are finally ready with our App.
# 
# <img src= "https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/Presentation/Notebook4.png?raw=true" width="100%" align="center"  hspace="5%" vspace="5%"/>
# 
# <p id="part5"></p>
# 
# # <span style="font-family: Arials; font-size: 20px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">2. LABELING</span>
# <hr style="height: 0.5px; border: 0; background-color: #000000">
# 
# <p id="part6"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">2.1 UNDERSTAND & COLLECT REQUIRED DATA</span>
# 
# For building the license plate recognition we need data. For that, we need to collect the vehicle images where the number plate appears on it as much as we can. [Here](https://github.com/Asikpalysik/Automatic-License-Plate-Detection/tree/main/images) is the sample data that I used for building this project. Below you can see few examples *Figure 3,4*.
# 
# <img src= "https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/Presentation/Notebook5.png?raw=true" width="100%" align="center"  hspace="5%" vspace="5%"/>
# 
# <p id="part7"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">2.2 LABEL IMAGES</span>
# 
# For label images, I used the LabelImg image annotation tool. Download the labelImg from [GitHub](https://github.com/Asikpalysik/Automatic-License-Plate-Detection/tree/main/labelImg-master) and follow the instruction to install the package. After that open, the GUI as give the instruction and click on CreateRectBox and draw the rectangle box as shown below and save the output in XML.
# 
# <img src= "https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/Presentation/Notebook6.png?raw=true" width="100%" align="center"  hspace="5%" vspace="5%"/>
# 
# This is a manual process and you need to do it for all the images. Be careful while doing labeling because the labeling process has a direct impact on the accuracy of the model. [Click here for a video tutorial](https://www.youtube.com/watch?v=XxslbNwcdaI).  On *Figure 5* you can find main window.
# 
# <p id="part8"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">2.3 PARSING INFORMATION FROM XML</span>
# 
# Example of our .xml files will look as below.
# ```
# <annotation>
#     <folder>images</folder>
#     <filename>N1.jpeg</filename>
#     <path>/Users/asik/Desktop/ANPR/imagesN1.jpeg</path>
#     <source>
#         <database>Unknown</database>
#     </source>
#     <size>
#         <width>1920</width>
#         <height>1080</height>
#         <depth>3</depth>
#     </size>
#     <segmented>0</segmented>
#     <object>
#         <name>number_plate</name>
#         <pose>Unspecified</pose>
#         <truncated>0</truncated>
#         <difficult>0</difficult>
#         <bndbox>
#             <xmin>1093</xmin>
#             <ymin>645</ymin>
#             <xmax>1396</xmax>
#             <ymax>727</ymax>
#         </bndbox>
#     </object>
# </annotation>
# ```
# Once you are done with the labeling process now we need to do some data preprocessing. Since the output of the label is XML in order to use this for the training process we need data in array format. For that, we will take the useful information from the label which are the diagonal points of the rectangle box or bounding box which are *xmin, ymin, xmax, ymax* respectively. This is available in XML. So we need to extract the information and save it in any convenient format, here I will convert bounding information into CSV and later on, I will convert that into an array using Pandas. Now let’s see how to parse the information using Python.
# 
# 
# <p id="part9"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">2.4 PARSING DATA FROM XML AND CONVERTING IT INTO CSV</span>
# 
# 
# Firstly let me load all librariies wich i will us in this project at one time.As well I will using **xml.etree** python library to parse the data from XML and also import pandas and glob. Using glob let first get all the XML files that are produced during labeling.

# In[ ]:


import os
import cv2
import numpy as np
import pandas as pd
import tensorflow as tf
import pytesseract as pt
pt.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import plotly.express as px
import matplotlib.pyplot as plt
import xml.etree.ElementTree as xet

from glob import glob
from skimage import io
from shutil import copy
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import TensorBoard
from sklearn.model_selection import train_test_split
from tensorflow.keras.applications import InceptionResNetV2
from tensorflow.keras.layers import Dense, Dropout, Flatten, Input
from tensorflow.keras.preprocessing.image import load_img, img_to_array


# In[ ]:


path = glob('input/number-plate-detection/annotations/*.xml')
labels_dict = dict(filepath=[],xmin=[],xmax=[],ymin=[],ymax=[])
for filename in path:

    info = xet.parse(filename)
    root = info.getroot()
    member_object = root.find('object')
    labels_info = member_object.find('bndbox')
    xmin = int(labels_info.find('xmin').text)
    xmax = int(labels_info.find('xmax').text)
    ymin = int(labels_info.find('ymin').text)
    ymax = int(labels_info.find('ymax').text)

    labels_dict['filepath'].append(filename)
    labels_dict['xmin'].append(xmin)
    labels_dict['xmax'].append(xmax)
    labels_dict['ymin'].append(ymin)
    labels_dict['ymax'].append(ymax)


# In the above code, we individually take each file and parse into xml.etree and find the object -> bndbox. Then we extract xmin,xmax,ymin,ymax and saved those values in the dictionary. After we convert it into a pandas data frame and save that into CSV file and save it in project folder as shown below.

# In[ ]:


df = pd.DataFrame(labels_dict)
df.to_csv('labels.csv',index=False)
df.head()


# With the above code, we successfully extract the diagonal position of each image and convert the data from an unstructured to a structured format.You can have A look data above. Now also extract the respective image filename of the XML.

# In[ ]:


filename = df['filepath'][0]
def getFilename(filename):
    filename_image = xet.parse(filename).getroot().find('filename').text
    filepath_image = os.path.join('input/number-plate-detection/images',filename_image)
    return filepath_image
getFilename(filename)


# In[ ]:


image_path = list(df['filepath'].apply(getFilename))
image_path[:10]#random check


# <p id="part10"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">2.5 VERIFY THE DATA</span>
# 
# As till now we did the manual process it is important to verify the information is we got is valid or not. For that just verify the bounding box is appearing properly for a given image. Here I consider the image N2.jpeg and the corresponding diagonal position can found in df. Result you can see on *Figure 8*

# In[ ]:


file_path = image_path[87] #path of our image N2.jpeg
img = cv2.imread(file_path) #read the image
# xmin-1804/ymin-1734/xmax-2493/ymax-1882 
img = io.imread(file_path) #Read the image
fig = px.imshow(img)
fig.update_layout(width=600, height=500, margin=dict(l=10, r=10, b=10, t=10),xaxis_title='Figure 8 - N2.jpeg with bounding box')
fig.add_shape(type='rect',x0=1804, x1=2493, y0=1734, y1=1882, xref='x', yref='y',line_color='cyan')


# <p id="part11"></p>
# 
# # <span style="font-family: Arials; font-size: 20px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">3. DATA PROCESSING</span>
# 
# <p id="part12"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">3.1 READ DATA</span>
# 
# This is a very important step, in this process we will take each and every image and convert it into an array using OpenCV and resize the image into 224 x 224 which is the standard compatible size of the pre-trained transfer learning model.

# In[ ]:


#Targeting all our values in array selecting all columns
labels = df.iloc[:,1:].values
data = []
output = []
for ind in range(len(image_path)):
    image = image_path[ind]
    img_arr = cv2.imread(image)
    h,w,d = img_arr.shape
    # Prepprocesing
    load_image = load_img(image,target_size=(224,224))
    load_image_arr = img_to_array(load_image)
    norm_load_image_arr = load_image_arr/255.0 # Normalization
    # Normalization to labels
    xmin,xmax,ymin,ymax = labels[ind]
    nxmin,nxmax = xmin/w,xmax/w
    nymin,nymax = ymin/h,ymax/h
    label_norm = (nxmin,nxmax,nymin,nymax) # Normalized output
    # Append
    data.append(norm_load_image_arr)
    output.append(label_norm)


# After that, we will normalize the image just by dividing with maximum number as we know that the maximum number for an 8-bit image is 28 -1 = 255. That the reason we will divide our image 255.0. The way of diving an array with the maximum value is called Normalization (Min-Max Scaler). We also need to normalize our labels too. Because for the deep learning model the output range should be between 0 to 1. For normalizing labels, we need to divide the diagonal points with the width and height of the image. And finally values in a python list.
# <p id="part13"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">3.2 SPLIT TRAIN AND TEST SET</span>
# In the next step, we will convert the list into an array using __Numpy__.

# In[ ]:


# Convert data to array
X = np.array(data,dtype=np.float32)
y = np.array(output,dtype=np.float32)


# Now split the data into training and testing set using __sklearn__.

# In[ ]:


# Split the data into training and testing set using sklearn.
x_train,x_test,y_train,y_test = train_test_split(X,y,train_size=0.8,random_state=0)
x_train.shape,x_test.shape,y_train.shape,y_test.shape


# <p id="part14"></p>
# 
# # <span style="font-family: Arials; font-size: 20px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">4. DEEP LEARNING FOR OBJECT DETECTION </span>
# 
# <p id="part15"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">4.1 INCEPTION-RESNET-V2 MODEL BUILDING</span>
# 
# Inception-ResNet-v2 is a convolutional neural network that is trained on more than a million images from the ImageNet database. The network is 164 layers deep and can classify images into 1000 object categories, such as keyboard, mouse, pencil, and many animals. As a result, the network has learned rich feature representations for a wide range of images. The Inception-ResNet-v2 was used for the classification task. The architecture of the network is shown in Figure 9 . Inception-Resnet-v2 is formulated based on a combination of the Inception structure and the Residual connection. In the Inception-Resnet block multiple sized convolutional filters are combined by residual connections. The usage of reyfual connections not only avoids the degradation problm caused by deep structures but also reduces the training time.
# 
# <img src= "https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/Presentation/Notebook7.png?raw=true" width="50%" align="center"  hspace="5%" vspace="5%"/>
# 
# We are ready to train a deep learning model for object detection. Here we will use the Inception-ResNet-v2 model with pre-trained weights and train this to our data. We are already import necessary libraries from TensorFlow previously, lets continue.
# 

# In[ ]:


inception_resnet = InceptionResNetV2(weights="imagenet",include_top=False, input_tensor=Input(shape=(224,224,3)))
# ---------------------
headmodel = inception_resnet.output
headmodel = Flatten()(headmodel)
headmodel = Dense(500,activation="relu")(headmodel)
headmodel = Dense(250,activation="relu")(headmodel)
headmodel = Dense(4,activation='sigmoid')(headmodel)


# ---------- model
model = Model(inputs=inception_resnet.input,outputs=headmodel)


# Now compile the model and  have a look at our summary. Don't de surprise summary will be a bit massiv. The summary is textual and includes information about: The layers and their order in the model. The output shape of each layer. The number of parameters (weights) in each layer.

# In[ ]:


# Complie model
model.compile(loss='mse',optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4))
model.summary()


# <p id="part16"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">4.2 INCEPTION-RESNET-V2 TRAINING AND SAVE</span>

# In[ ]:


tfb = TensorBoard('object_detection')
history = model.fit(x=x_train,y=y_train,batch_size=10,epochs=180,
                    validation_data=(x_test,y_test),callbacks=[tfb])


# In[ ]:


model.save('./object_detection.h5')


# <p id="part17"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">4.3 TENSORBOARD</span>
# 
# Lest have a look at on scalars on TensorBoard. In order to do it we will need to run simple command with right path for our "object detection". After we will see output with hosted link open it with Chrome. I was using VSCode for this project and for me it was way easy to run TensorBoard overview results, but in Kaggle it a bit more complicated and could  be disscused in other topic. For now i will show one screenshot of result which we have. We can see on scalars *Figure 12* how is our model preform. Our train and validation set don’t have over fitting behavior and our loss with respect of epochs is less.
# 
# You can simple type <code>!tensorboard --logdir="./object_detection"</code> it will generate link with text, click on link and here we go. <code>Serving TensorBoard on localhost; to expose to the network, use a proxy or pass --bind_all TensorBoard 2.6.0 at http://localhost:6006/ (Press CTRL+C to quit)</code>
# 
# <img src= "https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/Presentation/Notebook8.png?raw=true" width="80%" align="center" hspace="5%" vspace="5%"/>
# 
# <p id="part18"></p>
# 
# # <span style="font-family: Arials; font-size: 20px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">5. PIPELINE OBJECT DETECTION MODEL</span>
# 
# <p id="part19"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">5.1 MAKE PREDICTIONS</span>
# 
# This is the final step in object detection. In this step, we will put it all together and get the prediction for a given image. First, I would like to try with one of my test pictures of car. Let load our model.

# In[ ]:


# Load model
model = tf.keras.models.load_model('./object_detection.h5')
print('Model loaded Sucessfully')


# Next is loading our TEST picture with right path to it. I loaded some more images for this purpose  only - folder __TEST__.

# In[ ]:


path = 'input/number-plate-detection/TEST/TEST.jpeg'
image = load_img(path) # PIL object
image = np.array(image,dtype=np.uint8) # 8 bit array (0,255)
image1 = load_img(path,target_size=(224,224))
image_arr_224 = img_to_array(image1)/255.0  # Convert into array and get the normalized output

# Size of the orginal image
h,w,d = image.shape
print('Height of the image =',h)
print('Width of the image =',w)


# Now we can have a look at our image *Figure 13*

# In[ ]:


fig = px.imshow(image)
fig.update_layout(width=700, height=500,  margin=dict(l=10, r=10, b=10, t=10), xaxis_title='Figure 13 - TEST Image')


# So, let's look into the shape of my image.

# In[ ]:


image_arr_224.shape


# But in order to pass this image of a model, we need to provide the data in the dynamic fourth dimension. And what one indicates is a number of images. So here we are just passing only one image.

# In[ ]:


test_arr = image_arr_224.reshape(1,224,224,3)
test_arr.shape


# <p id="part20"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">5.2 DE-NORMALIZE THE OUTPUT</span>

# In[ ]:


# Make predictions
coords = model.predict(test_arr)
coords


# We have got the output from the model and output what we got is the normalized output. So, what we need to do is to convert back into our original form values, which actually we did in during the training process, in the training process, we have the original form values and convert that normalized one. So basically, we will de-normalize the values back.

# In[ ]:


# Denormalize the values
denorm = np.array([w,w,h,h])
coords = coords * denorm
coords


# <p id="part21"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">5.3 BOUNDING BOX</span>
# 
# Now we will draw bounding box on top of the image. I just want to provide the two diagonal points. Let's make use of these points and let's draw the rectangle box.

# In[ ]:


coords = coords.astype(np.int32)
coords


# In[ ]:


# Draw bounding on top the image
xmin, xmax,ymin,ymax = coords[0]
pt1 =(xmin,ymin)
pt2 =(xmax,ymax)
print(pt1, pt2)


# In[ ]:


cv2.rectangle(image,pt1,pt2,(0,255,0),3)
fig = px.imshow(image)
fig.update_layout(width=700, height=500, margin=dict(l=10, r=10, b=10, t=10))


# <p id="part22"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">5.4 CREATE PIPELINE</span>
# 
# Now what we'll do, let's put it all together in one place and create function. And in the end visualize it. Our output will return image and coordinates of bounding box.

# In[ ]:


# Create pipeline
path = 'input/number-plate-detection/TEST/TEST.jpeg'
def object_detection(path):

    # Read image
    image = load_img(path) # PIL object
    image = np.array(image,dtype=np.uint8) # 8 bit array (0,255)
    image1 = load_img(path,target_size=(224,224))

    # Data preprocessing
    image_arr_224 = img_to_array(image1)/255.0 # Convert to array & normalized
    h,w,d = image.shape
    test_arr = image_arr_224.reshape(1,224,224,3)

    # Make predictions
    coords = model.predict(test_arr)

    # Denormalize the values
    denorm = np.array([w,w,h,h])
    coords = coords * denorm
    coords = coords.astype(np.int32)

    # Draw bounding on top the image
    xmin, xmax,ymin,ymax = coords[0]
    pt1 =(xmin,ymin)
    pt2 =(xmax,ymax)
    print(pt1, pt2)
    cv2.rectangle(image,pt1,pt2,(0,255,0),3)
    return image, coords

image, cods = object_detection(path)

fig = px.imshow(image)
fig.update_layout(width=700, height=500, margin=dict(l=10, r=10, b=10, t=10),xaxis_title='Figure 14')


# <p id="part23"></p>
# 
# # <span style="font-family: Arials; font-size: 20px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">6. OPTICAL CHARACTER RECOGNITION - OCR</span>
# <hr style="height: 0.5px; border: 0; background-color: #000000">
# 
# <p id="part24"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">6.1 TESSERACT OCR</span>
# 
# Optical character recognition (OCR) software that is used to extract text from the image. Tesseract OCR have a python API and it is open source. Firstly, we will do installation of it. It pretty simple and depend on you OS. You can find manual and files to download for installation [here](https://guides.library.illinois.edu/c.php?g=347520&p=4121425).
# 
# <p id="part25"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">6.2 LIMITATIONS OF PYTESSERACT</span>
# 
# Tesseract works best when there is a clean segmentation of the foreground text from the background. In practice, it can be extremely challenging to guarantee these types of setups. There are a variety of reasons you might not get good quality output from Tesseract like if the image has noise on the background. The better the image quality (size, contrast, lightning) the better the recognition result. It requires a bit of preprocessing to improve the OCR results, images need to be scaled appropriately, have as much image contrast as possible, and the text must be horizontally aligned. Tesseract OCR is quite powerful but does have the following limitations.
# 
# __Tesseract limitations summed in the list.__
# <ul>
#   <li>The OCR is not as accurate as some commercial solutions available to us.</li>
#   <li>Doesn't do well with images affected by artifacts including partial occlusion, distorted perspective, and complex background.</li>
#   <li>It is not capable of recognizing handwriting.</li>
#   <li>It may find gibberish and report this as OCR output.</li>
#   <li>If a document contains languages outside of those given in the -l LANG arguments, results may be poor.</li>  
#   <li>It is not always good at analyzing the natural reading order of documents. For example, it may fail to recognize that a document contains two columns, and may try to join text across columns.</li>
#   <li>Poor quality scans may produce poor quality OCR.</li>
#   <li>It does not expose information about what font family text belongs to.</li>
# </ul>
# 
# <p id="part26"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">6.3 EXTRACT NUMBER PLATE TEXT FROM IMAGE</span>
# 
# Firstly, we will load our image and convert to array. Crop our bounding box with coordinates of it. We will identify region of interest (ROI) and have look at our cropped image *Figure 15*.

# In[ ]:


img = np.array(load_img(path))
xmin ,xmax,ymin,ymax = cods[0]
roi = img[ymin:ymax,xmin:xmax]
fig = px.imshow(roi)
fig.update_layout(width=350, height=250, margin=dict(l=10, r=10, b=10, t=10),xaxis_title='Figure 15 Cropped image')


# With use of tesseract, we will extract the text from the mage.
# 

# In[ ]:


# extract text from image
text = pt.image_to_string(roi)
print(text)


# Obviously, we didn't get the proper text, but at least you can able to get 90 percent of the information. It just an example and again will need to say that as more data than better prediction. We will come to that point in future. What I realize here: First of all we don't have much data, to resolve this problem and I added to this topic more sets almost the same data sets from other kagglers posted recently. Secondly i don't see that this model perfom well be honest with you, but full process which has beed done gave as a chance to undertand concept, we will buld another model with help of YOLO and where we can see how it perfom to conpear our results. Second of of Tesseract, I already explain some limetation of it, but image preproccessing can be another topic and it could even requre to build AI on it. So, now I want you to show how to build simple web and next step after it we will start with new model.

# <p id="part27"></p>
# 
# # <span style="font-family: Arials; font-size: 20px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">7. NUMBER PLATE WEB APP</span>
# <hr style="height: 0.5px; border: 0; background-color: #000000">
# 
# This part I’m briefly will explain all about installation and integration it to web. I do understand that some steps are self-explained but I doing it as manual and if it helps at list for one person it is meaning something for me. In other case you can skip few steps and have a couple of coffee.
# 
# 
# <p id="part28"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">7.1 REQUERED TOOLS</span>
# 
# In order to run our project and we need to install [VSCode](https://code.visualstudio.com/download) and few extensions important one you can find in list below. Extensions which will help us in future.
# 
# 
# - [All autocomplete](https://marketplace.visualstudio.com/items?itemName=Atishay-Jain.All-Autocomplete)
# - [Python extension pack](https://marketplace.visualstudio.com/items?itemName=donjayamanne.python-extension-pack)
# - [Yaml](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)
# - [Bootstrap 4, font awesome 4, font awesome 5 free & pro snippets](https://marketplace.visualstudio.com/items?itemName=thekalinga.bootstrap4-vscode)
# - [Django](https://marketplace.visualstudio.com/items?itemName=batisteo.vscode-django)  
# - [Html boilerplate](https://marketplace.visualstudio.com/items?itemName=sidthesloth.html5-boilerplate)
# - [Html snippets](https://marketplace.visualstudio.com/items?itemName=abusaidm.html-snippets)
# - [Flask-snippets](https://marketplace.visualstudio.com/items?itemName=cstrap.flask-snippets)
# 
# 
# <p id="part29"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">7.2 FLASK APP</span>
# 
# Firstly, make sure install flask. `!pip install flask`. And crate new file __App.py__.
# 
# 
# ```
# flask import Flask
# 
# #Webserver gateway interface
# app = Flask (__name__)
# 
# @app.route('/')
# def index():
#     return "Hello World"
# 
# if __name__ =="__main__":
#     app.run()>
#  ```
# Run in as on terminal (make sure you are in same directory where is you project.) You will see output like this `Running on http://127.0.0.1:5000 (Press CTRL+C to quit)` Open URL in Chrome to check it *Figure 16*
# 
# <img src= "https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/Presentation/Notebook10.png?raw=true" width="50%" align="center"  hspace="5%" vspace="5%"/>
# 
# Next create folder __templates__ in our project in folder __templates__ create new file as layout.html. Since we installed extensions just type html and choose boilerplate you will see something as on *Figure 17* and *!DOCTYPE html*
# 
# <img src= "https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/Presentation/Notebook12.png?raw=true" width="50%" align="center"  hspace="5%" vspace="5%"/>
# 
# ```
# <!DOCTYPE html>
# 
# <html>
#     <head>
#         <meta charset="utf-8">
#         <meta http-equiv="X-UA-Compatible" content="IE=edge">
#         <title></title>
#         <meta name="description" content="">
#         <meta name="viewport" content="width=device-width, initial-scale=1">
#         <link rel="stylesheet" href="">
#     </head>
#     <body>
#         <!--[if lt IE 7]>
#             <p class="browsehappy">You are using an <strong>outdated</strong> browser. Please <a href="#">upgrade your browser</a> to improve your experience.</p>
#         <![endif]-->
#         
#         <script src="" async defer></script>
#     </body>
# </html>
# ```
# 
# And now we can star to build our page. We can change Title and add body type etc. We will need to modify our app.py, layout (and Bootstrap to layout you can find as well [link](https://getbootstrap.com/docs/5.2/getting-started/introduction/) here we are interesting) and adding footer. At this stage it will look as below.
# 
# __app.py__
# ```
# from flask import Flask, render_template
# 
# #Webserver gateway interface
# app = Flask(__name__)
# 
# @app.route('/')
# def index():
#     return render_template('layout.html')
# 
# if __name__ == "__main__":
#     app.run(debug=True)
# ```
# __layout.html__
# ```
# <!DOCTYPE html>
# 
# <html>
#   <head>
#     <meta charset="utf-8" />
#     <meta http-equiv="X-UA-Compatible" content="IE=edge" />
#     <title>AUTOMATIC NUMBER-PLATE RECOGNITION</title>
#     <link
#       href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/css/bootstrap.min.css"
#       rel="stylesheet"
#       integrity="sha384-0evHe/X+R7YkIZDRvuzKMRqM+OrBnVFBL6DOitfPri4tjfHxaWutUpFmBp4vmVor"
#       crossorigin="anonymous"
#     />
#     <script
#       src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/js/bootstrap.bundle.min.js"
#       integrity="sha384-pprn3073KE6tl6bjs2QrFaJGz5/SUsLqktiwsUTF55Jfv3qYSDhgCecCxMW52nD2"
#       crossorigin="anonymous"
#     ></script>
#     <meta name="description" content="" />
#     <meta name="viewport" content="width=device-width, initial-scale=1" />
#     <link rel="stylesheet" href="" />
#   </head>
#   <body>
#     <!-- Navigation bar -->
#     <nav class="navbar navbar-light" style="background-color: #c1dce0">
#       <div class="container">
#         <a class="navbar-brand" href="/">
#           <h1 class="display-6">NUMBER PLATE OCR</h1>
#         </a>
#       </div>
#     </nav>
#     <!-- Footer -->
#     <footer>
#       <hr />
#       <a href="http://aslanahmedov.com"> CONTACT ME</a>
#     </footer>
#     <script src="" async defer></script>
#   </body>
# </html>
# ```
# <p id="part30"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">7.3 TEMPLATE INHERITANC</span>
# 
# We will create new file as html and name it as index.html and we are planning to write all functionality to out index.html. First go to our layout.html under </nav> block our body - see below.
# ```
# </nav>
#     {% block body %}
#     
#     {% endblock  %}
# ```
# In index.html we need to extend layout.html and block body of it as below.
# ```
# {% extends 'layout.html' %}
# {% block body %}
# {% endblock %}
# ```
# In app.py change layout.html to index.html and save it. CTRL+S always-everywhere!
# We will add some forms as well to index.html see below.
# ```
# {% extends 'layout.html' %} 
# {% block body %}
# <div class="container">
#   <br /><br /><br />
#   <form action="#" method="POST" enctype="multipart/form-data">
#     <div class="input-group">
#       <input type="file" class="form-control" name="image_name" required />
#       <input type="submit" value="UPLOAD" class="btn btn-outline-secondary" />
#     </div>
#   </form>
# </div>
# ```
# <p id="part31"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">7.4 HTTP METHOD UPLOAD FILE IN FLASK</span>
# 
# So now when we are upload the file, we need to receive it in flask and save it in some folder. That is called Static. For that create folder __static__ and, in this folder, create folder __upload__. In app.py (our flask) import few necessary libraries as well add methods and create base path/upload path. See below
# 
# 
# ```
# from flask import Flask, render_template, request
# import os
# # Webserver gateway interface
# app = Flask(__name__)
# 
# BASE_PATH = os.getcwd()
# UPLOAD_PATH = os.path.join(BASE_PATH, 'static/upload/')
# 
# @app.route('/', methods=['POST'])
# def index():
#     if request.method == 'POST':
#         upload_file = request.files['image_name']
#         filename = upload_file.filename
#         path_save = os.path.join(UPLOAD_PATH,filename)
#         upload_file.save(path_save)
#      
# 
#         return render_template('index.html')
# 
#     return render_template('index.html')
# 
# if __name__ == "__main__":
#     app.run(debug=True)
# ```
# 
# <p id="part32"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">7.5 INTEGRATE NPD AND OCR TO FLASK APP</span>
# 
# Now will make use of this upload image and we will make the predictions using deep learning model. Firstly, we will create one more file and name it as deeplearning.py in this file we are simply add our pipeline basically all necessary libraries and function with correct path to model. Create as well two more folder as roi and predict in static folder in the end your code will look like [this](https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/WebbApp/deeplearning.py). On flask as well "add text" - you can find it [here](https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/WebbApp/app.py). So, we are almost done. Now when we are uploading picture of car with plate number our model predicts bounding box, crop it at same time, save outputs to folder roi and folder predict. In order to display it on web we will modify index.html and add text future to save text as well. You can find ready code [here](https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/WebbApp/templates/index.html). And on *Figure 19* you can see result. All files and folder for Web please feel free to check [here](https://github.com/Asikpalysik/Automatic-License-Plate-Detection/tree/main/WebbApp).
# 
# <img src= "https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/Presentation/Notebook13.png?raw=true" width="100%" align="center"  hspace="5%" vspace="5%"/>
# 
# <p id="part33"></p>
# 
# # <span style="font-family: Arials; font-size: 20px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">8. RAEAL TIME NUMBER PLATE RECOGNITIONT WITH YOLO</span>
# 
# <p id="part34"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">8.1 EXPLANATION OF REQUIRED DATA</span>
# 
# YOLO or You only look once, is one of the most widely used, deep learning-based object detection algorithm out there.YOLO divides an image into a grid system, and each grid detects objects within itself. They can be used for real-time object detection based on the data streams. They require very few computational resources.The network architecture of Yolov5. It consists of three parts: (1) Backbone: CSPDarknet, (2) Neck: PANet, and (3) Head: Yolo Layer. The data are first input to CSPDarknet for feature extraction, and then fed to PANet for feature fusion. Finally, Yolo Layer outputs detection results (class, score, location, size).
# 
# <img src= "https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/Presentation/Notebook14.png?raw=true" width="100%" align="center"  hspace="5%" vspace="5%"/>
# 
# Our previous process is great, but there is a problem with the model. The major problem with the model is model has very low precision in detecting the license plate and also it is very, very slow processing. To overcome the above limitations, particularly the precision, we will use the most powerful of the reduction model available till now is YOLO. Now, let us see how we can use our existing data preparation to our YOLO model. The labeling and the data preprocessing work, what we have did for the existing work can be applied to the same Yola model. But there is one major difference we need to do in YOLO is our label. Previously that you have seen, we used the xmin, xmax, ymin, ymax. and VI Max is our actual output. But for YOLO is a center X-Y position of the bounding box and width and height of the bounding box, and particularly the X-Y position is referred to the center of the bounding box. Let me give you an example *Figure 20*. For this image, the labeling for the YOLO should be the center X and Y, and which should be the normalized between the width and height of the image. And W and H are the respective width and height of the bounding box normalized to width and height of the image.
# 
# <img src= "https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/Presentation/Notebook9.png?raw=true" width="100%" align="center"  hspace="5%" vspace="5%"/>
# 
# So, in the labeling process, basically this is what the format we now have to prepare our data plus center position of X center position of Y this refers to the bounding box and width and height of the bounding box. [class, center_x, center_y, w, h]. That is what one of the changes we need to make. And the next thing is that the folder structure which we need to prepare, particularly for the YOLO, will look something like *Figure 21*.
# 
# <img src= "https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/Presentation/Notebook11.png?raw=true" width="100%" align="center"  hspace="5%" vspace="5%"/>
# 
# Let consider the data images. Inside the data images we should how train and test. In the training test folder, we have to maintain all out images related to the training and the corresponding labels should be there in .txt format. And moreover, the label information data should consist same name as our image. Just like our training data, we will also prepare our test data.
# 
# I will write function and using that function, I can try to extract weight of the image, height of the image and also the file name from the xml files. Creating function parsing and return will be our filename, wight and height and apply all to our data frame as below. 

# In[ ]:


# parsing
def parsing(path):
    parser = xet.parse(path).getroot()
    name = parser.find('filename').text
    filename = f'input/number-plate-detection/images/{name}'

    # width and height
    parser_size = parser.find('size')
    width = int(parser_size.find('width').text)
    height = int(parser_size.find('height').text)

    return filename, width, height
df[['filename','width','height']] = df['filepath'].apply(parsing).apply(pd.Series)
df.head()


# Now the next step is let me calculate the center_x, center_y, width and height, which is normalized to width and height. And as well normalize width and height of bounding box.

# In[ ]:


# center_x, center_y, width , height
df['center_x'] = (df['xmax'] + df['xmin'])/(2*df['width'])
df['center_y'] = (df['ymax'] + df['ymin'])/(2*df['height'])

df['bb_width'] = (df['xmax'] - df['xmin'])/df['width']
df['bb_height'] = (df['ymax'] - df['ymin'])/df['height']
df.head()


# <p id="part35"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">8.2 DATA PREPARATION</span>
# 
# One of the major challenges in the training of YOLO is hardware itself. YOLO requires a fast-processing chip used to get trained. It is extremely difficult to train the YOLO in normal CPUs. Firstly, we have to clone YOLOV5 to our work space. You can find it [here](https://github.com/ultralytics/yolov5) and install all requirements. Make sure you in right folder type as below, let's do it.

# In[ ]:


os.system('git clone https://github.com/ultralytics/yolov5')


# In[ ]:


os.system(f'{sys.executable} -m pip install -r ./yolov5/requirements.txt')


# We need to make a one more folder and make into it two more - name it as __data_images__ and __train__ and __test__. We will split data to train and split.

# In[ ]:


os.makedirs('./yolov5/data_images/', exist_ok=True)


# In[ ]:


os.makedirs('./yolov5/data_images/test/', exist_ok=True)


# In[ ]:


os.makedirs('./yolov5/data_images/train/', exist_ok=True)


# In[ ]:


### split the data into train and test
df_train = df.iloc[:200]
df_test = df.iloc[200:]


# We will copy each image into the folder train and test and generate .txt which has label info.

# In[ ]:


train_folder = './yolov5/data_images/train'

values = df_train[['filename','center_x','center_y','bb_width','bb_height']].values
for fname, x,y, w, h in values:
    image_name = os.path.split(fname)[-1]
    txt_name = os.path.splitext(image_name)[0]

    dst_image_path = os.path.join(train_folder,image_name)
    dst_label_file = os.path.join(train_folder,txt_name+'.txt')

    # copy each image into the folder
    copy(fname,dst_image_path)

    # generate .txt which has label info
    label_txt = f'0 {x} {y} {w} {h}'
    with open(dst_label_file,mode='w') as f:
        f.write(label_txt)

        f.close()

test_folder = './yolov5/data_images/test'

values = df_test[['filename','center_x','center_y','bb_width','bb_height']].values
for fname, x,y, w, h in values:
    image_name = os.path.split(fname)[-1]
    txt_name = os.path.splitext(image_name)[0]

    dst_image_path = os.path.join(test_folder,image_name)
    dst_label_file = os.path.join(test_folder,txt_name+'.txt')

    # copy each image into the folder
    copy(fname,dst_image_path)

    # generate .txt which has label info
    label_txt = f'0 {x} {y} {w} {h}'
    with open(dst_label_file,mode='w') as f:
        f.write(label_txt)

        f.close()


# As well I will create __data.yaml__ file with path to train and validation, as well number of classes as 1, name it in list as license plate. You will need to save this in your dataset because we will need to provide the path on it later.
# 
# ```
# train: data_images/train
# val: data_images/test
# nc: 1
# names: [
#     'license_plate'
# ]
# ```

# <p id="part36"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">8.3 TRAINING YOLO</span>
# 
# Next step is basically train model. It could take time be ready for it. You can use Kaggle or GoogleColab for it. We already set out data.yaml file, lets us give path to it and train model. Below you will find code to cleare you GPU(It helped me a lot and will save you time.)

# In[ ]:


os.system(f'{sys.executable} -m pip install GPUtil')

import torch
from GPUtil import showUtilization as gpu_usage
from numba import cuda

def free_gpu_cache():
    print("Initial GPU Usage")
    gpu_usage()                             

    torch.cuda.empty_cache()

    cuda.select_device(0)
    cuda.close()
    cuda.select_device(0)

    print("GPU Usage after emptying the cache")
    gpu_usage()

free_gpu_cache()  


# In[ ]:


os.system(f'{sys.executable} ./yolov5/train.py --data input/number-plate-detection/data.yaml --cfg ./yolov5/models/yolov5s.yaml --batch-size 8 --name Model --epochs 100')


# When model trained, we need to save our it in order to use it at OCR in onnx format as below:

# In[ ]:


os.system(f'{sys.executable} ./yolov5/export.py --weight ./yolov5/runs/train/Model/weights/best.pt --include torchscript onnx')


# All right, we have successfully safed our model after unzip it. We can notice that there is a model folder.
# We can find predicted pictures and we are able to detect the license plate very accurately. There might be the few wrong results, but still our model detects the license plate accurately. PR cow is eventually very  important for me that will tell you the detection rate. We can see that our precision recall tell us that we can able to detect our model with 0.92 Precision and 0.5 mean Average Precision, you can find example of one of val_batch below
# <img src= "https://github.com/Asikpalysik/Automatic-License-Plate-Detection/blob/main/Presentation/Notebook15.png?raw=true" width="100%" align="center"  hspace="5%" vspace="5%"/>
# 
# <p id="part37"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">8.4 PREDICTING RESULTS FROM YOLO</span>
# 
# Let’s do some images settings which is omportant to provide in model construction.  Input settings we need to pass as 640 by 640.

# In[ ]:


# settings
INPUT_WIDTH =  640
INPUT_HEIGHT = 640


# Let me first load TEST image, it will have a plate number on it.

# In[ ]:


# LOAD THE IMAGE
img = io.imread('input/number-plate-detection/TEST/TEST.jpeg')

fig = px.imshow(img)
fig.update_layout(width=700, height=400, margin=dict(l=10, r=10, b=10, t=10))
fig.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)
fig.show()


# Now, we will load our YOLO model.

# In[ ]:


# LOAD YOLO MODEL
net = cv2.dnn.readNetFromONNX('./yolov5/runs/train/Model/weights/best.onnx')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)


# The next step is I need to parse this image to my YOLO model and get the prediction. Important - size we need to set as input width a 640 and input height is 640.
# 
# We have the 25200 rows and 6 columns.  The first four columns will give you the information about the bounding box, which is center X and, Center Y, W and H. And these values are normalized to 640 by 640. And the next two values are the confidence and the probabilities. Confidence tells us what is the confidence for the detecting the bounding box and the next one is the probability score of the class, since we have only one class that is number plate.
# 
# Let’s make a list of boxes and confidence and place it order. As well we need to identify our X_factor and Y_factor of image.
# 
# We have to filter detections based on the confidence score and the probability score. Let me take the confidence >0.4 and filter from class >0.25.
# 
# There is will be one of major issue with YOLO modeling it will give you the repeated boxes, but the same object it might give you that multiple boxes. For that we need to perform the non-maximum suppression. To do it we need to provide all our clean boxes and confidences. 
# 
# In the end of that part of code I will take bounding boxes and draw the rectangle box to our image. And will write it all in functions. 

# In[ ]:


def get_detections(img,net):
    # 1.CONVERT IMAGE TO YOLO FORMAT
    image = img.copy()
    row, col, d = image.shape

    max_rc = max(row,col)
    input_image = np.zeros((max_rc,max_rc,3),dtype=np.uint8)
    input_image[0:row,0:col] = image

    # 2. GET PREDICTION FROM YOLO MODEL
    blob = cv2.dnn.blobFromImage(input_image,1/255,(INPUT_WIDTH,INPUT_HEIGHT),swapRB=True,crop=False)
    net.setInput(blob)
    preds = net.forward()
    detections = preds[0]

    return input_image, detections

def non_maximum_supression(input_image,detections):

    # 3. FILTER DETECTIONS BASED ON CONFIDENCE AND PROBABILIY SCORE

    # center x, center y, w , h, conf, proba
    boxes = []
    confidences = []

    image_w, image_h = input_image.shape[:2]
    x_factor = image_w/INPUT_WIDTH
    y_factor = image_h/INPUT_HEIGHT

    for i in range(len(detections)):
        row = detections[i]
        confidence = row[4] # confidence of detecting license plate
        if confidence > 0.4:
            class_score = row[5] # probability score of license plate
            if class_score > 0.25:
                cx, cy , w, h = row[0:4]

                left = int((cx - 0.5*w)*x_factor)
                top = int((cy-0.5*h)*y_factor)
                width = int(w*x_factor)
                height = int(h*y_factor)
                box = np.array([left,top,width,height])

                confidences.append(confidence)
                boxes.append(box)

    # 4.1 CLEAN
    boxes_np = np.array(boxes).tolist()
    confidences_np = np.array(confidences).tolist()

    # 4.2 NMS
    index = cv2.dnn.NMSBoxes(boxes_np,confidences_np,0.25,0.45)

    return boxes_np, confidences_np, index

def drawings(image,boxes_np,confidences_np,index):
    # 5. Drawings
    for ind in index:
        x,y,w,h =  boxes_np[ind]
        bb_conf = confidences_np[ind]
        conf_text = 'plate: {:.0f}%'.format(bb_conf*100)
        license_text = extract_text(image,boxes_np[ind])


        cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,255),2)
        cv2.rectangle(image,(x,y-30),(x+w,y),(255,0,255),-1)
        cv2.rectangle(image,(x,y+h),(x+w,y+h+25),(0,0,0),-1)


        cv2.putText(image,conf_text,(x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),1)
        cv2.putText(image,license_text,(x,y+h+27),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),1)

    return image


# In[ ]:


# predictions flow with return result
def yolo_predictions(img,net):
    # step-1: detections
    input_image, detections = get_detections(img,net)
    # step-2: NMS
    boxes_np, confidences_np, index = non_maximum_supression(input_image, detections)
    # step-3: Drawings
    result_img = drawings(img,boxes_np,confidences_np,index)
    return result_img


# Here we will not only detect license plate but else extract test from it. We already done it before let’s repeat it again. We will write function. First from bounding box we need to take our x,y,w,h and extract ROI. I place it at top of our functions in drawing part.

# In[ ]:


# extrating text
def extract_text(image,bbox):
    x,y,w,h = bbox
    roi = image[y:y+h, x:x+w]

    if 0 in roi.shape:
        return 'no number'

    else:
        text = pt.image_to_string(roi)
        text = text.strip()

        return text


# In[ ]:


# test
img = io.imread('input/number-plate-detection/TEST/TEST.jpeg')
results = yolo_predictions(img,net)


# In[ ]:


fig = px.imshow(img)
fig.update_layout(width=700, height=400, margin=dict(l=10, r=10, b=10, t=10))
fig.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)
fig.show()


# The accuracy of the model is really pretty accurate. However, there are few misclassification, but still our model is performing really well. If you want to get more and more good accuracy, what you have to do is feed more and more data and then you can able to predict very good results. 
# 
# <p id="part38"></p>
# 
# # <span style="font-family: Arials; font-size: 16px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">8.5 REAL TIME OBJECT DETECTION</span>
# 
# In real time prediction my point is that the detection is very perfect and in order to get very, very good predictions, we need to get very high 4K definition camera so that we can able to extract the text properly.
#  
# ```
# cap = cv2.VideoCapture('input/number-plate-detection/TEST/TEST.mp4')
# while True:
#     ret, frame = cap.read()
#     
#     if ret == False:
#         print('Unable to read video')
#         break
#         
#     results = yolo_predictions(frame,net)
#     
#     cv2.namedWindow('YOLO',cv2.WINDOW_KEEPRATIO)
#     cv2.imshow('YOLO',results)
#     if cv2.waitKey(30) == 27 :
#         break
#         
# cv2.destroyAllWindows()
# cap.release()
# ```
# <img src= "https://user-images.githubusercontent.com/91852182/172154404-ccb2a6b5-deb4-4321-91ff-a8f13457b352.gif" width="80%" align="center"  hspace="5%" vspace="5%"/>

# <p id="part39"></p>
# 
# # <span style="font-family: Arials; font-size: 20px; font-style: normal; font-weight: bold; letter-spacing: 3px; text-align: center; color: #000000; line-height:1.0">9. CONCLUSION</span>
# <hr style="height: 0.5px; border: 0; background-color: #000000">
# 
# 
# With the increase in the number of vehicles, vehicle tracking has become an important research area for efficient traffic control, surveillance, and finding stolen cars. For this purpose, efficient real-time license plate detection and recognition are of great importance. Due to the variation in the background and font color, font style, size of the license plate, and non-standard characters, license plate recognition is a great challenge in developing countries. To overcome such issues, this study applies a deep-learning strategy to improve license plate recognition efficiency. The collected images have been captured under various lighting/contrast conditions, distance from the camera, varying angle of rotation, and validated to produce a high recognition rate. The approach can be effectively used by law enforcement agencies and private organizations to improve homeland security. Future work may include training and validation of the existing algorithm using the hybrid classifier method and improvement of the robustness of the license plate recognition system in varying weather conditions.
# 
# *All files you can find as well on my [GITHUB](https://github.com/Asikpalysik/Automatic-License-Plate-Detection)
# If you find this post useful please __UPVOTE__, and if you have any question feel free to [CONTACT ME.](http://aslanahmedov.com)*
