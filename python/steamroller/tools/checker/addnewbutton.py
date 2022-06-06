from PySide2 import QtWidgets

import imp
from steamroller.tools.checker import checker
imp.reload(checker)
check = checker.Checker()

class AddBtn( QtWidgets.QPushButton ):
    """
    This class create buttons that execute the different functions that exist in the checker class.
    """

    def __init__(self, id_str="", label = '', args = None, parent = None ):
        """
        :param id_str: ( str ) Id name is defined by the check key name in the project step dictionary.
        :param label: ( str ) button lable.
        :parm args: arguments required by the check function.
        :parent: widget parent.

        """


        super(AddBtn, self).__init__(parent)

        self.id_str = id_str
        self.label = label
        self.args = args 

        self._generateUI()

    def _generateUI(self):
        
        # Set
        self.setText ( self.label )
        # Connect 
        self.clicked.connect ( self.btnFunction )

    def _label(self):
        label = self.label
        return label

    def _remove_btn(self):
        self.deleteLater()

    def btnFunction(self):
        """
        Execute the checker function based on id_str key name and pass arguemtns.
        """
        check.checkList( check = self.id_str, args = self.args )
      