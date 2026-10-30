import sys
from PyQt5.QtWidgets import QApplication
from engine import PetEngine

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = PetEngine()
    pet.show()
    sys.exit(app.exec_())