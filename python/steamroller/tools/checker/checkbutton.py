from PySide2 import QtWidgets

import imp

from steamroller.tools.checker import checker
imp.reload(checker)
check = checker.Checker()

from steamroller.tools.checker import addnewbutton
imp.reload( addnewbutton )


class ItemWidget( QtWidgets.QWidget ):
    
    def __init__(self, id_str="", args = None , mainTable = None, parent=None):

        super(ItemWidget, self).__init__(parent)

        self.id_str = id_str
        self.mainTable = mainTable
        self.args = args

        self._generateUI()

    def _generateUI(self):

        # Build 
        self.main_layout = QtWidgets.QHBoxLayout ()
        self.setLayout ( self.main_layout )
        
        self.pushButton_check = QtWidgets.QPushButton ( "Check" )

        # Layout 
        self.main_layout.addWidget ( self.pushButton_check )
        
        # Set 
        self.main_layout.setMargin ( 3 ) 

        # Connect 
        self.pushButton_check.clicked.connect ( self.assigneCheck )

    def assigneCheck(self):

        row = self.getRow()
        checkerName = self.getChecker( row = row )
        args = self.args

        self.runChecker( row = row, checkerName = checkerName, args = args )

    def getRow(self):
        """
        Query table row by text.
        """

        rows = self.mainTable.rowCount()

        for r in range( 0, rows) :
            if self.id_str == self.mainTable.item( r, 0 ).text():
                row = r
                break

        return row

    def getChecker(self, row = int ):
        """Query checker key name from main table.

        :param row: [int], row index from main table.
        :return: [ checker key name from main table column 0 ]
        :rtype: string[]
        """

        # Query item text from column 0
        checkerName = self.mainTable.item( row, 0 ).text()
        return checkerName

    def runChecker(self, row = int, checkerName = '', args = None ):

        # result = [ status  , note ]
        result = check.checkList( check = checkerName, args = args )

        keys = result.keys()

        # Set led color. 
        if 'state' in keys:
            self.ledColor(status = result[ 'state' ], row = row, table = self.mainTable )
        else:
            self.ledColor(status = None, row = row, table = self.mainTable )

        # Remove extra buttons if checker is correct 
        if result['state'] == 1:
            self.remvoeExtraButtons( row  = row )

        # Set note 
        if 'note' in keys:
            self.setNote( note = result[ 'note' ], row = row, table = self.mainTable )

        # Fix Btn
        if 'fixBtn' in keys:
            if result['fixBtn']:
                if result['state'] == 2 or result['state'] == 3:
                    self.addFixBtn( row = row, checkSufix = '_fix', label = 'Fix' )

        # Fix Btn
        if 'extraBtn' in keys:
            if result['extraBtn'][0]:
                self.addFixBtn( row = row, checkSufix = '_extra', label = result['extraBtn'][1] )
 
    def remvoeExtraButtons( self, row = int ):

        childrens = self.mainTable.cellWidget( row, 2 ).children()
        for c in childrens:
            try:
                btnLabel = c._label()
                if btnLabel != 'Check':
                    c._remove_btn()
            except:
                pass

    def addFixBtn(self, row = int, checkSufix = '', label = '' ):

        # 
        try:
            self.fixBtn._remove_btn()
        except:
            pass

        # Get widget 
        widget = self.mainTable.cellWidget( row, 2 ).layout()
  
        childrens = self.mainTable.cellWidget( row, 2 ).children()
        for c in childrens:
            try:
                btnLabel = c._label()
                if btnLabel == label:
                    c._remove_btn()
            except:
                pass

        fixBtn = addnewbutton.AddBtn( id_str = self.id_str + checkSufix, label = label, args = self.args)

        widget.addWidget ( fixBtn )

    def setNote(self, note = None, row = int, table = None ):
        """
        Set table note

        :param note: (str) text note to display in interface column.
        :param row: (int) row index.
        :param table: QtableWidget.
        """
        item = QtWidgets.QTableWidgetItem( note )
        table.setItem( row, 3, item)
        
    def ledColor(self, status = None , row = int, table = None ):
        """
        Set color code icon and add it to the cell.

        :param status: (int) 1 green ok, 2 red error, 3 orange warning 
        :param row: (int) row index.
        :param table: QtableWidget.
        """
        
        # to do get previous item and delete
        dot = QtWidgets.QLabel()

        if status == 1:
            dot.setStyleSheet("QLabel"
                    "{"
                    "margin-left: 8px;"
                    "margin-top: 5px;"
                    "border-color : black;" 
                    "border-width : 1px;" 
                    "border-style : solid;" 
                    "border-radius : 8px;" 
                    "max-width : 16px;"
                    "max-height: 16px;"
                    "background-color : green;"
                    "}"
                    )

        elif status == 2:
            dot.setStyleSheet("QLabel"
                    "{"
                    "margin-left: 8px;"
                    "margin-top: 5px;"
                    "border-color : black;" 
                    "border-width : 1px;" 
                    "border-style : solid;" 
                    "border-radius : 8px;" 
                    "max-width : 16px;"
                    "max-height: 16px;"
                    "background-color : red;"
                    "}"
                    )

        elif status == 3:
            dot.setStyleSheet("QLabel"
                    "{"
                    "margin-left: 8px;"
                    "margin-top: 5px;"
                    "border-color : black;" 
                    "border-width : 1px;" 
                    "border-style : solid;" 
                    "border-radius : 8px;" 
                    "max-width : 16px;"
                    "max-height: 16px;"
                    "background-color : orange;"
                    "}"
                    )

        else:
            dot.setStyleSheet("QLabel"
                    "{"
                    "margin-left: 8px;"
                    "margin-top: 5px;"
                    "border-color : black;" 
                    "border-width : 1px;" 
                    "border-style : solid;" 
                    "border-radius : 8px;" 
                    "max-width : 16px;"
                    "max-height: 16px;"
                    "background-color : gray;"
                    "}"
                    )


        table.setCellWidget ( row, 1, dot)