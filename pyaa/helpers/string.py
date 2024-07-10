import re


class StringHelper:
    @staticmethod
    def only_numbers(value):
        if value:
            data = re.sub("[^0-9]", "", value)
            return data
        else:
            return None
