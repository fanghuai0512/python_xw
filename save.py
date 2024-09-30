from src.utils.config_util import load_common_config
from src.tasks.data_holder import DataHolder

if __name__ == '__main__':
    conf = load_common_config("./configs")
    rstm = DataHolder(conf)
    rstm.main()