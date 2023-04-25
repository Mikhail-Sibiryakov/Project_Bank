from PyQt5 import QtCore
from PyQt5.Qt import QComboBox


class ClickedComboBox(QComboBox):
    """Класс QComboBox на который можно навесить обработчик событий на нажатие
    на него"""

    popupAboutToBeShown = QtCore.pyqtSignal()

    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super(ClickedComboBox, self).showPopup()