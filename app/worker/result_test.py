from app import db
from sqlalchemy.exc import IntegrityError
from random import seed, randint
from ..worker.clients.api_client import APIClient
import forgery_py
from datetime import datetime, timedelta
import radar
from app.models import Results



class ResultGen:
    def __init__(self):
        self.api_client = APIClient(base_url="http://localhost:5000")

    def generate_time(self,interval, current):
        value = interval.split()
        delta = None
        if value[1] == "days":
            delta = timedelta(days=int(value[0]))
        elif value[1] == "hours":
            delta = timedelta(hours=int(value[0]))
        if delta:
            start = current - delta
            stop = current
            return radar.random_datetime(start, stop)
        else:
            print "NO DELTA VALUE"


    def generate_test_results(self,project_id, canary_id, interval, count):
        all_results = []
        seed()
        end_time = datetime.utcnow()
        for index in range(count):
            code = randint(0, 1)
            if code is 0:
                status = "pass"
                failure_details = ""
                created_at = self.generate_time(interval=interval, current=end_time)
            else:
                status = "fail"
                failure_details = forgery_py.lorem_ipsum.title(words_quantity=2)
                created_at = self.generate_time(interval=interval, current=end_time)
            data = {'status' : status,
                    'failure_details' : failure_details,
                    'created_at' : "{}".format(created_at),
                    'id': index + 1
            }
            call = self.api_client.post_results(project_id, canary_id, data)
            if call.status_code != 201:
                print "ERROR WHILE GENERATING RESULTS"


