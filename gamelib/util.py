import os.path

def data_file(filename):
    if os.path.exists(filename):
        return filename
    elif os.path.exists(os.path.join('../data/', filename)):
        return os.path.join('../data/', filename)
    elif os.path.exists(os.path.join('data/', filename)):
        return os.path.join('data/', filename)

