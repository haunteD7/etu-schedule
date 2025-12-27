import json
import requests

class ScheduleClient:
    def __init__(self, base_url: str):
        self.__base_url: str = base_url

    def request_schedule_week(self, group: int) -> str:
        response = requests.get(self.__base_url + '/mobile/schedule', params={ 
            'groupNumber': group, 'joinWeeks': 'false' })

        # days = response.json()[str(group)]['days']

        # for i in range(6):
        #     day = days[str(i)]
        #     print(f'{day['name']}')
