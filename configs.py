import yaml

"""read data from a .yaml file"""


def read_yaml_file(file):
    with open(file) as file:
        # The FullLoader parameter handles the conversion from YAML
        list = yaml.load(file, Loader=yaml.FullLoader)
        return list
