from flask import Flask, render_template
from flask_apscheduler import APScheduler

class Config:
    SCHEDULER_API_ENABLED = True


app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


@app.route('/')
def main_page():
    return render_template('index.html')


@scheduler.task('interval', id='do_job_1', seconds=5)
def job1():
    print('Job 1 executed')

if __name__ == '__main__':
    app.run()