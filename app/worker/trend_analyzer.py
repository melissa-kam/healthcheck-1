from __future__ import division
from ..worker.base_trend_analyzer import BaseTrendAnalyzer
from ..worker.clients.api_client import APIClient
from datetime import datetime, timedelta
from .result_test import ResultGen

gen = ResultGen()

class TrendAnalyzer(BaseTrendAnalyzer):
    def __init__(self):
        self.api_client = APIClient(base_url="http://localhost:5000")

# Always clear your table after each call to trend
    def process_trend(self, project_id, canary_id, interval, resolution, threshold):
        gen.generate_test_results(project_id=project_id, canary_id=canary_id, interval=interval,count=10)
        results = self.api_client.get_results(project_id=project_id, canary_id=canary_id, interval=interval, sample_size=None)
        results_list = sorted(results.get('results'))
        resolution = self.time_conversion(resolution)
        status_list = []
        length = len(results_list)
        analysis_list = []
        start_time = datetime.strptime(results_list[0].get('created_at'), '%a, %d %b %Y %H:%M:%S %Z')
        border = start_time + resolution
        index = 0
        while index < length:
            if index != length - 1:
                created_at = datetime.strptime(results_list[index].get('created_at'), '%a, %d %b %Y %H:%M:%S %Z')
                if created_at <= border:
                    analysis_list.append(results_list[index].get('status'))
                    index += 1
                else:
                    # at a border
                    if analysis_list:
                        status_list.append(self.trend_analyzer(threshold, analysis_list))
                        analysis_list = []
                    border = border + resolution
            else:
                # looking at the last result
                created_at = datetime.strptime(results_list[index].get('created_at'), '%a, %d %b %Y %H:%M:%S %Z')
                if created_at <= border: # if last result is in the same time resolution as the previous
                    analysis_list.append(results_list[index].get('status'))
                    status_list.append(self.trend_analyzer(threshold, analysis_list))
                else:
                    # analyse what you currently have and start over
                    status_list.append(self.trend_analyzer(threshold, analysis_list))
                    analysis_list = []
                    border = border + resolution
                    while True:
                        if created_at <= border:
                            analysis_list.append(results_list[index].get('status'))
                            status_list.append(self.trend_analyzer(threshold, analysis_list))
                            break
                        else:
                            border = border + resolution
                index += 1
        label = ["day1", "day2", "day3", "day4", "day5", "day6", "day7", "day8", "day9", "day10"]
        print "STATUS LIST IS"
        print status_list
        return status_list, label


    def trend_analyzer(self, threshold, results_list):
        passes = 0
        fails = 0
        for result in results_list:
            if result == 'pass':
                passes += 1
            else:
                fails += 1
        assert len(results_list) == (passes + fails)
        pass_percent = passes / len(results_list) * 100
        if pass_percent > float(threshold):
            return "green"
        else:
            return "red"


    class Example():
        def __init__(self, status, id):
            self.status = status
            self.id = id

        def __repr__(self):
            return "[id = %d, status = %s]" % (self.id, self.status)


    def time_conversion(self, time_value):
        value = time_value.split()
        if value[1] == "days":
            return timedelta(days=int(value[0]))
        elif value[1] == "hours":
            return timedelta(hours=int(value[0]))



