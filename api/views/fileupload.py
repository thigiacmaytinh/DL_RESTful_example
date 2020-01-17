from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from django.core.files.storage import FileSystemStorage
from django.conf import settings as djangoSettings
import os
import random
import string
from api.apps import *
import base64
from api.saveBase64Image import *
from PIL import Image
import datetime
import face_recognition
import cv2

####################################################################################################

@api_view(["POST"])           
def UploadFile(request):
    try:

        if request.method == 'POST' and request.FILES['uploadfile']:
            #get image data
            uploadfile = request.FILES['uploadfile']            

            #set path
            upload_folder_abs = os.path.join(djangoSettings.MEDIA_ROOT)
            random_name = GenerateRandomName(uploadfile.name)
            saved_file_abs = os.path.join(upload_folder_abs, random_name)

            #save file
            fs = FileSystemStorage(upload_folder_abs)
            filename = fs.save(random_name , uploadfile)    
            
            #load image to detect face
            image = face_recognition.load_image_file(saved_file_abs)
            face_locations = face_recognition.face_locations(image)

            #load image in opencv to draw faces
            matDraw = cv2.imread(saved_file_abs)
            for face_location in face_locations:

                # Print the location of each face in this image
                top, right, bottom, left = face_location
                cv2.rectangle(matDraw, (left, top), (right, bottom), [255,0,0], 2)
            
            #save drawed image
            tempFilePath = upload_folder_abs + "\\temp.jpg"
            cv2.imwrite(tempFilePath , matDraw)

            #convert drawed image to base64
            with open(tempFilePath, "rb") as image_file:
                base64Str = base64.b64encode(image_file.read())

            #result is json object
            result = {
                "num" : len(face_locations),
                "text" : face_locations,
                "img": base64Str}


            #remove tempfile
            os.remove(saved_file_abs)
            os.remove(tempFilePath)


            return Response(
                result,
                status=SUCCESS_CODE, content_type="application/json")
    except Exception as e:
        return Response(
                {'Error': str(e)},
                status=ERROR_CODE, content_type="application/json")

####################################################################################################

@api_view(["POST"])           
def uploadbase64(request):
    try:
        folder_name = request.POST.get("folder_name")
        file_name = request.POST.get("file_name")
        images = request.POST.get("imgs")
        uploaded_file_urls = SaveBase64ToImg(folder_name, file_name, images)
        respond = {"url" : uploaded_file_urls}

        return Response(
                {respond},
                content_type="application/json",
                status=SUCCESS_CODE)
   
    except Exception as e:
        print(str(e))
        return Response(
                {'Error': str(e)},
                status=ERROR_CODE,
                content_type="application/json"
                )

