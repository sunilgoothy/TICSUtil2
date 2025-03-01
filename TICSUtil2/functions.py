from datetime import datetime
import yaml, os, configparser, rsa, psutil
from base64 import b64decode


def log_time():
    """Returns date time with ms. Can be used for logging messages"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def read_yaml_config(filepath, suppress_msgs=False):
    filepath_split = filepath.rsplit(".", 1) or filepath
    filename = filepath_split[0]
    fileext = filepath_split[1]
    filepath_dev = filename + "_dev" + "." + fileext
    if os.path.isfile(filepath_dev):
        filepath = filepath_dev
        if not suppress_msgs:
            print(f"Dev config file exists. Using Dev config.")
    config = {}
    try:
        with open(filepath, "r") as cfg:
            config = yaml.safe_load(cfg)
    except Exception as e:
        raise
    if not suppress_msgs:
        print(f"Configuration read for {filepath} complete.")
    return config


def read_config_file(filename, section, key):
    key_val = None
    config = configparser.ConfigParser()
    try:
        config.read(filename, encoding="utf-8")
        key_val = config.get(section, key)
    except Exception as e:
        print(f"Error in reading Config File '{filename}'. Error: {e}")
    return key_val


def write_config_file(filename, section, key, value):
    config = configparser.ConfigParser()
    try:
        config.read(filename, encoding="utf-8")
        config.set(section, key, value)
        with open(filename, "w") as configfile:
            config.write(configfile)
        return True
    except Exception as e:
        print(f"Error in writing Config File '{filename}'. Error: {e}")
        return False


def get_mac_all(family):
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == family:
                yield snic.address


def check_license(license_file, application):
    status = 0
    if os.path.exists(license_file):
        config = configparser.ConfigParser()
        config.read(license_file, encoding="utf-8")
        if "license" in config:
            section = config["license"]
            if (
                "application" in section
                and "customer" in section
                and "reference" in section
                and "expire" in section
                and "key" in section
            ):
                pubkey = rsa.PublicKey(
                    7514513144282372129647063215394916456869398537697968821675421023637195249518021134485320680971729707960684956187071298549155245246725650219448549812838423,
                    65537,
                )
                addr = get_mac_all(psutil.AF_LINK)
                for mac in addr:
                    data = (
                        mac
                        + section["application"]
                        + section["customer"]
                        + section["reference"]
                        + section["expire"]
                    )
                    try:
                        rsa.verify(
                            data.encode("utf-8"),
                            b64decode(section["key"].encode()),
                            pubkey,
                        )
                    except Exception as e:
                        msg = str(e)
                    else:
                        status = 1
                        break
                if status < 1:
                    msg = f"This license is invalid for this machine"
                    return status, None, None, None, msg
                else:
                    if (
                        datetime.strptime(section["expire"], "%Y-%m-%d").date()
                        >= datetime.now().date()
                    ):
                        if application == section["application"]:
                            status = 1
                            msg = f"License key Registered to {section['customer']} for Application: {section['application']} valid till: {section['expire']}"
                            return (
                                status,
                                section["application"],
                                section["customer"],
                                section["expire"],
                                msg,
                            )
                        else:
                            status = 101
                            msg = f"License is not valid for the application"
                            return (
                                status,
                                section["application"],
                                section["customer"],
                                section["expire"],
                                msg,
                            )
                    else:
                        status = 102
                        msg = f"License expired on {section['expire']}"
                        return (
                            status,
                            section["application"],
                            section["customer"],
                            section["expire"],
                            msg,
                        )
            else:
                msg = f"Invalid license file"
                status = 103
                return status, None, None, None, msg
        else:
            msg = f"Invalid license file"
            status = 104
            return status, None, None, None, msg
    msg = f"License file not found"
    status = 6
    return status, None, None, None, msg
