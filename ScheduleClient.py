import requests
import logging

ERROR_MESSAGE = 'Произошла какая-то ошибка'
NOTHING_FOUND_MESSAGE = 'Для данной группы нет, либо не найдено расписания'

DELIM = '------------------------\n' 

def format_lesson_form(form: str) -> str:
    match form:
       case "standard":
           return "Обычно"
       case "distant":
           return "Дистанционно"
       case "online":
           return "Онлайн"
    return ''
def format_lesson_time(lesson) -> str:
    return f'{lesson['start_time']}-{lesson['end_time']}'
def format_lesson(lesson) -> str:
    teacher = ''
    if lesson['teacher']:
        teacher = 'Преподаватель: ' + lesson['teacher'] + '\n'
    room = ''
    if lesson['room']:
        room = 'Аудитория: ' + lesson['room'] + '\n'
    form = ''
    if lesson['form']:
        form = 'Тип: ' + format_lesson_form(lesson['form']) + '\n'
    return f'{DELIM}{format_lesson_time(lesson)}:\n{lesson['name']} ({lesson['subjectType']}):\n{teacher}{room}{form}{DELIM}'
logger = logging.getLogger(__name__)

class ScheduleClient:
    def __init__(self, base_url: str):
        self.__base_url: str = base_url

    def request_schedule_week(self, group: int, week_number: int) -> str:
        try:
            response = requests.get(self.__base_url + '/mobile/schedule', params = { 
                'groupNumber': group, 'joinWeeks': 'false' })
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error: {http_err}\nCode: {response.status_code}")
            return ERROR_MESSAGE 
        except requests.exceptions.ConnectionError as conn_err:
            logger.error(f"Connection error: {conn_err}")
            return ERROR_MESSAGE 
        except requests.exceptions.Timeout as timeout_err:
            logger.error(f"Request timeout: {timeout_err}")
            return ERROR_MESSAGE 
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Common request error: {req_err}")
            return ERROR_MESSAGE 
        except Exception as e:
            print(f"Unexpected error: {e}")
            return ERROR_MESSAGE 

        try:
            response_json = response.json()
        except ValueError as json_err:
            logger.error(f"JSON parsing error: {json_err}")
            return ERROR_MESSAGE 

        if response_json == {}:
            return NOTHING_FOUND_MESSAGE
        response_str = ''

        days = response_json[str(group)]['days']
        for i in range(6):
            day = days[str(i)]
            lessons = day['lessons']
            lessons_str = ''

            for j in range(len(lessons)):
                lesson = lessons[j]
                week = int(lesson['week'])
                if week_number == week:
                    lessons_str += format_lesson(lesson)

            response_str += f'{day['name']}\n{lessons_str}\n' 
        
        return response_str 