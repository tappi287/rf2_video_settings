import re


def create_file_safe_name(filename: str) -> str:
    """ Replace any non alphanumeric characters from a string expect minus/underscore/period """
    return re.sub('[^\\w\\-_\\.]', '_', filename)


class JsonRepr:
    def to_js_object(self):
        js_dict = dict()
        for k, v in self.__dict__.items():
            if k[:2] == '__' or callable(v):
                continue
            js_dict[k] = v
        return js_dict

    def from_js_dict(self, json_dict):
        for k, v in json_dict.items():
            setattr(self, k, v)