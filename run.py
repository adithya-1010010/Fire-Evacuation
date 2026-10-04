"""Start the program:  python run.py"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from fire_evacuation.main import main

main()
