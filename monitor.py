from src.tasks.monitor_task import MonitorTask
from src.utils.config_util import load_common_config

if __name__ == '__main__':
    conf = load_common_config("./configs")
    MT = MonitorTask(config=conf)
    MT.main()
