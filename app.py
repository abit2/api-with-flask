#!flask/bin/python
from flask import Flask, jsonify,request,session
from celery import Celery
import time

app = Flask(__name__)
celery = Celery(app.name)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'status': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'status': False
    }
]

countdown = [
    {
        'id' : 1,
        'timeleft': 0,
        'kill': 0
    },
    {
        'id' : 2,
        'timeleft': 0,
        'kill': 0
    },
]

state = [
        {
        'status' : 'OK',
        }
        ]

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/api/serverStatus', methods=['GET'])
def get_tasks():
    if request.method == 'GET':
        return jsonify({'tasks': countdown})

@app.route("/api/request", methods=['GET'])         #api/request?connId=19&timeout=80
def get_task():
    if request.method == 'GET':
        connId=request.args.get('connId',type=int)
        timeout=request.args.get('timeout',30,type=int) 
        for task in tasks:
            if task['id'] == connId:
                task['status'] = 'running'
                wait(timeout,connId)
                # wait.apply_async(args=[timeout,connId],countdown=timeout)
        return jsonify({'details' : state})

@app.route('/api/kill', methods=['PUT'])
def update_tasks():
    g_json = request.get_json(force=True)
    id_got = g_json["connId"]
    counter=0
    for count in countdown:
        if count["id"]!=id_got:
            counter+=1
    if counter==len(countdown):
        return "innvalid connection Id :"+ str(id_got)
    for count in countdown:
        if count["id"]==id_got:
            count["kill"]=1
    for task in tasks:
        if task["id"]==id_got:
            task["status"]="killed"
    state[0]["status"]="killed"
    return jsonify({'details' : state})

# @celery.task
def wait(timeout,id):
    for i in range(timeout,0,-1):
        time.sleep(1)
        for count in countdown:
            if count['id'] == id:
                if count['kill'] == 1:
                    state[0]['status']='killed'
                    break
                print("timeleft>>>>>>>>>>>>>",i)
                count['timeleft'] = i


if __name__ == '__main__':
    app.run(debug=True,threaded=True)
