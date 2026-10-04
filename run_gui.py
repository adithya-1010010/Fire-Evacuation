"""Start the Pygame version:  python run_gui.py   (needs:  pip install pygame)"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

try:
    from fire_evacuation.gui import main
except ImportError:
    print("Pygame is not installed. Install it with:  pip install pygame")
    print("(The terminal version does not need it:  python run.py)")
    sys.exit(1)

main()
