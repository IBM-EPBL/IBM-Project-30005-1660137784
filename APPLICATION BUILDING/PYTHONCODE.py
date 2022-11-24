#importing packages
import cv2
import os
import numpy as np
from .utils import download_file
import cvlib as cv
from cvlib.object_detection import draw_bbox
import time
from playsound import playsound

#import requests
from flask import Flask, request, render_template, redirect, url_for

#loading the nodel
from cloudant.client import cloudant

#creating a database
from cloudant.client import cloudant

#Authenticate using an IAM API key
client=cloudant.iam("apikey-v2-1germironao24tlsp2ehtv8t9b0omwv5y9rzv878gdlc","73c7938e06a985726f424b64af8ac721","https://apikey-v2-1germironao24tlsp2ehtv8t9b0omwv5y9rzv878gdlc:73c7938e06a985726f424b64af8ac721@d82e7eb3-57c5-4f98-abb4-afaf429028bf-bluemix.cloudantnosqldb.appdomain.cloud",connect=True)
#creating a database
my_database=client.create_database("my_database")

#default home page or route
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/index.html')
def Home():
    return render_template('index.html')
#registration page
@app.route('/register.html')
def register():
    return render_template('register.html')

#configure the registration page
@app.route('/afterreg',methods=['POST'])
def afterreg():
    x=[x for x in request.form.values()]
    print(x)
    data= {
        '_id':x[1],
        'name':x[0],
        'psw':x[2]
    }
    print(data)

    query= {'_id':{'$eq':data['_id']}}

    docs=my_database.get_query_result(query)
    print(docs)

    print(len(docs.all()))

    if(len(docs.all())==0):
       url= my_database.create_document(data)
       #response=requests.get(url)
       return render_template('register.html', pred="Registration Successfull, Please login using your details")
    else:
        return render_template('register.html', pred="You are already a member, Please login using your details")


#login page
@app.route('/login')
def Login():
    return render_template('login.html')
@app.route('/afterlogin',methods=['POST'])
def afterlogin():
    user = request.form['_id']
    passw = request.form['psw']
    print(user,passw)

    query = {'_id':{'$eq':user}}

    docs=my_database.get_query_result(query)
    print(docs)

    print(len(docs.all()))

    if(len(docs.all())==0):
        return render_template('login.html', pred="The username is not found")
    else:
        if((user==docs[0][0]['_id'] and passw==docs[0][0]['psw'])):
            return redirect(url_for('prediction'))
        else:
            print('Invalid user')

#logout page
@app.route('/Logout')
def logout():
    return render_template('logout.html')

@app.route('/result',methods=["GET","POST"])
def res():
    webcam= cv2.VideoCapture('drowning.mp4')

    if not webcam.isOpened():
        print("Could not open webcam")
        exit()

    t0=time.time()

    centre0=np.zeros(2)
    isDrowning = False

    #loop through frames
    while webcam.isOpened():
        #read frame from webcam
        status, frame=webcam.read()


#creating bounding box
bbox, label, conf = cv.detect_common_objects(frame)
#simplifying for one person
if(len(bbox>0)):
    bbox0=bbox[0]
    centre=[0,0]

    centre =[(bbox0[0]+bbox0[2])/2,(bbox0[1]+bbox0[3])/2]

    #vertical and horizontal vertical variables
    hmov= abs(centre[0]-centre0[0])
    vmov= abs(centre[1]-centre0[1])

    #this threshold is for checking how much centre
    x=time.time()

    threshold= 10
    if(hmov>threshold or vmov>threshold):
        print(x-t0,'s')
        t0=time.time()
        isDrowning=False
    else:
        print(x-t0,'s')
        if((time.time()-t0)>10):
            isDrowning = True

        print('bbox:',bbox,'centre:',centre,'centre0:',centre0)
        print('Is he drowning:',isDrowning)

        centre0=centre

        #draw bounding box over detected objects
        out = draw_bbox(frame, bbox, label, conf, isDrowning)


#display output
cv2.imshow("Real-time object detection",out)
if(isDrowning == True):
    playsound('alarm.mp3')
    webcam.release()
    cv2.destroyAllWindows()
    return render_template('prediction.html', pred = "Emergency !!! The person is drowning")
    #press Q to stop
    if cv2.waitkey(1) & 0xff == ord('q'):
        break
    if _name_ == "_main_":
        app.run(debug=True)
