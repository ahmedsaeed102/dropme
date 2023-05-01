# custom URL parameter converters for handling float url paramaters
class FloatUrlParameterConverter:
    regex = '[0-9]+\.?[0-9]+'

    def to_python(self, value):
        return float(value)

    def to_url(self, value):
        return str(value)