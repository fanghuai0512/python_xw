import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] %(message)s')


class GetTaskException(Exception):
    pass


def get_task(token):
    # "974591bc2cbe41ca85ecc784ec09d341"
    task_url = "http://121.37.97.10:9000/collectTask/getUserCollectTask"
    headers = {
        "accept": "*/*",
        "Authorization": token
    }
    data = ""
    try:
        response = requests.post(task_url, headers=headers, data=data)
        data = response.json()
        if data['code'] != 200:
            raise GetTaskException(f"Request task failed, code: {data['code']}")
        task_data = data['data']
        return task_data
    except Exception as e:
        logging.info(f"Get task error;msg: {e}")
        return


if __name__ == '__main__':
    print(get_task('974591bc2cbe41ca85ecc784ec09d341'))
