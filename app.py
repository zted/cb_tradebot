"""
This simple flask app demonstrates how to spin up a web server that can run background
task with context into the app state. The state is maintained by an object, which is used
in the background task

Documentation:
advanced python scheduler (APScheduler) https://ascheduler.readthedocs.io/en/3.x/#

APScheduler integration with flask
https://github.com/viniciuschiele/flask-apscheduler for documentation of more complex examples
https://viniciuschiele.github.io/flask-apscheduler/

"""
from datetime import datetime

from flask import Flask
from flask_apscheduler import APScheduler


class TestObj:
    def __init__(self):
        self.time = None
        self.name = 'No Name'

    def __str__(self):
        return 'Name is {} with time {}'.format(self.name, self.time)


myObj = TestObj()


class Config:
    SCHEDULER_API_ENABLED = True


app = Flask(__name__)
app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


@scheduler.task('interval', id='do_job_1', seconds=30, misfire_grace_time=900)
def job1():
    """Demo job function.
    :param var_two:
    """
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    myObj.time = current_time
    print("Updated Obj Time Successfully")
    print(myObj)
    return


@app.route("/hello/<string:name>")
def hello(name: str) -> str:
    return "Hello {} and welcome!".format(name)


@app.route("/hello2/<string:name>")
def hello2(name: str) -> str:
    if name == '':
        myObj.name = 'NO NAME'
        return 'Invalid Name'
    else:
        myObj.name = name
    return "Hello {} and welcome!\nThe time is now {}".format(name, myObj)


if __name__ == "__main__":
    app.run()
