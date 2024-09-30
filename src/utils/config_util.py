import os
import yaml


def load_common_config(configs_path):
    env = os.getenv("ENV", "dev")
    config_path = os.path.join(configs_path, f"{env}.yaml")
    # conf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "configs/" + config_name)
    with open(config_path, 'r') as f:
        conf = yaml.safe_load(f)
        print(conf, config_path)

    for k1, v1 in conf.items():
        if isinstance(v1, dict):
            for k2, v2 in v1.items():
                key = f"{k1}_{k2}"
                conf[k1][k2] = os.getenv(key, v2)

    return conf


# common_config = load_common_config("./configs")

if __name__ == '__main__':
    common_config = load_common_config("../../configs")
    print(f"common_config: {common_config}")
