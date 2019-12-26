# import flask dependencies
from flask import Flask, request, make_response, jsonify
import shutil
import subprocess
import json
from function import *
import pandas as pd
import numpy as np
import tensorflow as tf
from konlpy.tag import Kkma
from konlpy.utils import pprint
kkma = Kkma()
# initialize the flask app
keras = tf.keras
app = Flask(__name__)

intentdf = pd.read_csv('train_intent.csv',encoding="CP949")
entitydf = pd.read_csv('train_entity.csv',encoding = "CP949")

intenttoken = tokenizer()
intenttoken.fit(intentdf['question'].values)

entitytoken = tokenizer()
entitytoken.fit(entitydf['word'].values)
entitytoken.get_char2idx()


intentmodel = keras.models.load_model('intent_model.h5')
entitymodel = keras.models.load_model('entity_model.h5')

def 형태소분석(text):
    형태소 = kkma.pos(text)
    명사 = []
    for i in 형태소:
        if i[1] == 'NNG':
            명사.append(i[0])
        else:
            pass
    return 명사

def entity분석(명사):
    inputdata = Entity_question_processing(명사,entitytoken)
    prediction = list(np.argmax(entitymodel.predict(inputdata),axis=1))
    print(명사)
    print(prediction)
    result = {}
    for a,b in zip(명사,prediction):
        if b == 0:
            result[a] = 'color'
        elif b == 1:
            result[a] = 'thing'
        elif b == 2:
            result[a] = 'loc'
    return result  
@app.route('/test',methods=['GET','POST'])
def hello():
    return 'hello'
# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    req = request.get_json()
    print(req)
    intent = req['queryResult']['intent']['displayName']
    text = req['queryResult']['queryText']
    print("유저가 한 말 : "+text)
    inputdata = Intent_question_processing([text],intenttoken)
    prediction = np.argmax(intentmodel.predict(inputdata),axis=1)
    print("예측 값 : {}".format(prediction[0]))
    if intent == 'Internet' and prediction[0] == 0:
        path = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        subprocess.call(path)
        print("internet done")
        return {'fulfillmentText':'인터넷을 켰어요'}
    elif intent == 'Paint' and prediction[0] == 1:
        path = "C:\WINDOWS\system32\mspaint.exe"
        subprocess.call(path)
        print("paint done")
        return {'fulfillmentText':'그림판을 켰어요'}
    elif intent == 'pick':
        noun = 형태소분석(text)
        result = entity분석(noun)
        key = result.keys()
        returntext = ''
        for i in key:
            returntext += (i+' = '+result[i]+' ')
        return {'fulfillmentText':returntext}

    elif intent == 'Pickandplace':
        start = req['queryResult']['parameters']['start']
        destination = req['queryResult']['parameters']['destination']
        stuff = req['queryResult']['parameters']['stuff']
        startfeature = req['queryResult']['parameters']['startfeature']
        destinationfeature = req['queryResult']['parameters']['destinationfeature']
        stufffeature = req['queryResult']['parameters']['stufffeature']
        verb = req['queryResult']['parameters']['endverb']

        returntext = ''
        returntext += '처음 물건이 있는 곳 : {}\n'.format(start)
        returntext += '처음 물건이 있는 곳 특징 : '
        if len(startfeature) == 0 :
            pass
        else:
            for i in startfeature:
                returntext += (str(i)+' ')
            returntext += '\n'
            startentity = entity분석(startfeature)
            for i in startentity.keys():
                returntext += (i + ' = ' + startentity[i] + ' ')

        returntext += '\n'
        returntext += '옮길 물건 : {}\n'.format(stuff)
        returntext += '옮길 물건의 특징 : '
        if len(stufffeature) == 0:
            pass
        else:
            for i in stufffeature:
                returntext += (str(i) + ' ')
            returntext += '\n'
            sfentity = entity분석(stufffeature)
            for i in sfentity.keys():
                returntext += (i+' = '+sfentity[i]+' ')

        returntext += '\n'
        returntext += '물건을 옮길 곳 : {}\n'.format(destination)
        returntext += '물건을 옮길 곳 특징 : '
        
        if len(destinationfeature) == 0:
            pass
        else:
            for i in destinationfeature:
                returntext += (str(i) + ' ')
            returntext += '\n'
            detentity = entity분석(destinationfeature)
            for i in detentity.keys():
                returntext += (i + ' = ' + detentity[i] + ' ')
                
        returntext += '\n'
        returntext += '할 일 : {}'.format(verb)


        

        return {'fulfillmentText':returntext}
    else:
        return {'fulfillmentText':'죄송합니다 잘 알아듣지 못했어요'}

    # print(req)    
    

    # return {'fulfillmentText': "파일이동완료"} #3



# run the app
if __name__ == '__main__':
   app.run(host='0.0.0.0',port =80)

