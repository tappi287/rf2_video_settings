import eel
import sys
import argparse

from modules.web import *

# New change
eel.init('web')
eel.start('index.html', size=(600, 400))
