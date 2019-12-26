# import flask dependencies
from flask import Flask, request, make_response, jsonify
import shutil
import subprocess
import json
# initialize the flask app
app = Flask(__name__)

simple = {
      "fulfillmentText": "This is a text response",
      "fulfillmentMessages": [
        {
          "card": {
            "title": "card title",
            "subtitle": "card text",
            "imageUri": "https://assistant.google.com/static/images/molecule/Molecule-Formation-stop.png",
            "buttons": [
              {
                "text": "button text",
                "postback": "https://assistant.google.com/"
              }
            ]
          }
        }
      ],
      "source": "example.com",
      "payload": {
        "google": {
          "expectUserResponse": True,
          "richResponse": {
            "items": [
              {
                "simpleResponse": {
                  "textToSpeech": "this is a simple response"
                }
              }
            ]
          }
        },
        "facebook": {
          "text": "Hello, Facebook!"
        },
        "slack": {
          "text": "This is a text response for Slack."
        }
      },
      "outputContexts": [
        {
          "name": "projects/${PROJECT_ID}/agent/sessions/${SESSION_ID}/contexts/context name",
          "lifespanCount": 5,
          "parameters": {
            "param": "param value"
          }
        }
      ],
      "followupEventInput": {
        "name": "event name",
        "languageCode": "en-US",
        "parameters": {
          "param": "param value"
        }
      }
    }
# default route
@app.route('/')
def index():
    return 'Hello World!'

# function for responses
def results():
    # build a request object
    req = request.get_json(force=True)

    # fetch action from json
    action = req.get('queryResult').get('action')

    # return a fulfillment response
    return {'fulfillmentText': 'This is a response from webhook.'}

# create a route for webhook
# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    req = request.get_json(force=True)
    doing = req['queryResult']['action']
    print(doing)
    if doing == "input.unknown":
        return {'fulfillmentText':"미안해요 잘 못 들었어요"}
    elif doing == "move":
        pathname = req['queryResult']['parameters']['pathname'] #1
        filename = req['queryResult']['parameters']['filename']
        if pathname[0][-1] == '/':
            try:
                shutil.move("{}{}".format(pathname[0],filename),"{}".format(pathname[1]))
                print("move {}{} {}".format(pathname[0],filename,pathname[1]))
                return {'fulfillmentText': "파일이동완료"} #3
            except:
                return {'fulfillmentText':'Syntax Error Or cannot find file'}
        else:
            try:
                shutil.move("{}{}".format(pathname[0],filename),"{}".format(pathname[1]))
                print("move {}/{} {}".format(pathname[0],filename,pathname[1]))
                return {'fulfillmentText': "파일이동완료"} #3
            except:
                return {'fulfillmentText':'Syntax Error Or cannot find file'}
    elif doing == "Internet":
        
        path = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        subprocess.call(path)
        print("done")
        return {'fulfillmentText':'Internet 실행완료'}
    elif doing == "test":
        print(req)
        with open('response.json','w',encoding='utf-8') as f:
          json.dump(req,f,indent='\t')
        return {'fulfillmentText':'실행완료'}

    # print(req)    
    

    # return {'fulfillmentText': "파일이동완료"} #3



# run the app
if __name__ == '__main__':
   app.run(host='0.0.0.0',port =80)