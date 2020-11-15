from modules.web import *


def start_eel():
    eel.init('web')
    eel.start('index.html', size=(960, 600))


if __name__ == '__main__':
    start_eel()
