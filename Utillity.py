from asyncore import read
from base64 import *
import base64
import os
import uuid
from PIL import Image

from email.mime import image

def Get_img_Encorded_value(filename):
    image=open(filename,'rb')
    image_reader=image.read()
    img_64_encord=base64.encodebytes(image_reader)
    return img_64_encord

def Get_img_Decord_Value(img_encord_data,file_name):
    img_encord_data=bytes(img_encord_data.strip('\n'),'utf-8')
    img_64_decord =base64.decodebytes(img_64_decord)
    result_img=open(file_name,'wb')
    result_img.write(img_64_decord)
    return result_img

def upload_file(file):
    UPLOAD_FOLDER="./static/img/"
    file_name=uuid.uuid4().hex+ '_' + file.filename
    path = os.path.join(UPLOAD_FOLDER, file_name)
    file.save(path)
    return path
