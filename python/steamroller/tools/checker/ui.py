import sys
import imp
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtUiTools

from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui


from steamroller.tools.checker import projectlist
imp.reload(projectlist)

from steamroller.tools.checker import checker
imp.reload(checker)
check = checker.Checker()

from steamroller.tools.checker import addnewbutton
imp.reload( addnewbutton )

from steamroller.tools.checker import checkbutton
imp.reload( checkbutton )


def _maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow ()
    if sys.version_info.major >= 3:
        return wrapInstance( int ( main_window_ptr ), QtWidgets.QWidget )
    else:
        return wrapInstance( long ( main_window_ptr ), QtWidgets.QWidget )



class CheckerUI( QtWidgets.QDialog ):

    def __init__ ( self, parent = _maya_main_window () ):
    # def __init__ ( self, parent = None ):
    
        
        super( CheckerUI, self ).__init__( parent )

        self.project = 'default'
        # self.step = 'lookDev'
        self.step = 'model'
        self.assetName = 'assetName'

        self.__build ()
        self.__layout ()
        self.__setup ()
        self.__connect ()
        self.__update ()
        self.show ()

    def __build( self ):

        # Main layout
        self.main_layout = QtWidgets.QVBoxLayout ()
        

       # Main table 
        self.mainTable = QtWidgets.QTableWidget(0,4)

        # Step selector 
        self.stepHLayout = QtWidgets.QHBoxLayout ()
        self.stepSelector = QtWidgets.QComboBox()

        # Run all.
        self.run_hLayout = QtWidgets.QHBoxLayout()
        self.pushButton_runAll = QtWidgets.QPushButton()

    def __layout( self ):
        
        self.layout = QtWidgets.QVBoxLayout ()
        # layout initialize
        self.setLayout ( self.main_layout  )

        self.main_layout.addLayout( self.stepHLayout )
        self.stepHLayout.addWidget( self.stepSelector )

        self.main_layout.addWidget  ( self.mainTable )

        self.main_layout.addLayout ( self.run_hLayout )
        self.run_hLayout.addWidget ( self.pushButton_runAll )

    def __setup ( self ):
        
        # Set window
        self.setWindowTitle ( 'Checker' )
        self.resize ( 400 , 600 )
        
        # Table 
        self.mainTable.setObjectName( 'MainTable' )
        self.mainTable.horizontalHeader().setVisible(False)
        self.mainTable.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)

        self.mainTable.verticalHeader().setVisible(False)

        self.mainTable.setColumnWidth(0, 120)
        self.mainTable.setColumnWidth(1, 12)
        self.mainTable.setColumnWidth(2, 120)
        self.mainTable.setColumnWidth(3, 220)

        # Run all 
        self.pushButton_runAll.setText( 'Check All' )

        # Step selector
        steps = ['model', 'lookDev', 'layout', 'animation']
        self.stepSelector.insertItems( 1, steps )

    def __connect ( self ):

        # Check all
        self.pushButton_runAll.clicked.connect ( self.checkAll )
         
        # Step selector update filter list
        self.stepSelector.currentTextChanged.connect ( self.updateStepFilters )

    def __update ( self ):
        
        # Load list
        self.updateFilters( self.step )

    def updateStepFilters( self ):

        step = self.stepSelector.currentText()
        self.updateFilters( step = step )
        

    def updateFilters( self, step = '' ):
        
        # Query Filters 
        checkPoints = projectlist.projectFilters( project = self.project, step = step )
        
        # Set table rows.
        self.mainTable.setRowCount ( len(checkPoints) )

        # Add filters row 
        row = 0
        for k in checkPoints:
            
            # Checker name, and priority level.
            currentChecker = k[0]
            priority = k[1]

            # Set column 0 with the checker name ( type ). 
            currentItem = QtWidgets.QTableWidgetItem( currentChecker )
            currentItem.setFlags(QtCore.Qt.ItemIsEnabled)
            self.mainTable.setItem ( row, 0, currentItem )

            # Set dot color code.
            dot = self.dotCheck()
            self.mainTable.setCellWidget ( row, 1, dot)

            # Add check button. 
            check = self.checkBtn( check = currentChecker, priority = priority )
            self.mainTable.setCellWidget ( row, 2, check ) 

            row = row + 1

    def dotCheck(self ):
        
        self.dot = QtWidgets.QLabel()

        self.dot.setStyleSheet("QLabel"
                            "{"
                            "margin-left: 8px;"
                            "margin-top: 5px;"
                            "background-color : gray;"
                            "border-color : black;" 
                            "border-width : 1px;" 
                            "border-style : solid;" 
                            "border-radius : 8px;" 
                            "max-width : 16px;"
                            "max-height: 16px;"
                            "}"
                            )

        return self.dot

    def getArgs( self, check = '' ):
        # Select step
        step = self.stepSelector.currentText()

        # checkersList = projectlist.projectFilters( project = self.project, step = self.step, assetName = self.assetName)
        checkersList = projectlist.projectFilters( project = self.project, step = step, assetName = self.assetName)
        
        args = []
        for x in checkersList:
            if check in x:
                args = x
        
        return args

    def checkBtn(self, check = '' , priority = int ):
        
        args = self.getArgs( check = check )
        newBtn = checkbutton.ItemWidget( id_str = check, mainTable = self.mainTable, args = args[1:])
        return newBtn

    def checkAll(self):
        
        # Select step
        step = self.stepSelector.currentText()

        rows = self.mainTable.rowCount()

        for row in range( 0 , rows ):
            checkName = self.mainTable.item( row, 0 ).text()

            # Query priority level. 
            priority = 1
            # projectCheckers = projectlist.projectFilters( project = self.project, step = self.step, assetName = self.assetName )
            projectCheckers = projectlist.projectFilters( project = self.project, step = step, assetName = self.assetName )


            for c in projectCheckers:
                if checkName in c:
                    priority = c[ -1 ]
                    break
            
            # Get arguments form projectlist 
            args = self.getArgs( check = checkName ) 

            result = check.checkList( check = checkName , args = args[1:] )

            keys = result.keys()

            # Set led color. 
            if 'state' in keys:
                ledColor(status = result['state'], row = row, table = self.mainTable )
            else:
                ledColor(status = None, row = row, table = self.mainTable )

            # Set note 
            if 'note' in keys:
                setNote( note = result['note'], row = row, table = self.mainTable )

            # Add fix btn
            if 'fixBtn' in keys:
                if result['fixBtn']:
                    if result['state'] == 2 or result['state'] == 3:
                        self.addFixBtn( row = row , checkName = checkName, checkSufix = '_fix', label = 'Fix')

            # Extra Btn
            if 'extraBtn' in keys:
                if result['extraBtn'][0]:
                    self.addFixBtn( row = row, checkName = checkName, checkSufix = '_extra', label = result['extraBtn'][1] )

    def addFixBtn(self, row = int, checkName = '', checkSufix = '', label = '' ):
    
        try:
            self.fixBtn._remove_btn()
        except:
            pass

        # Get widget layout.
        widget = self.mainTable.cellWidget( row, 2 ).layout()

        # If fix button already exist remove it and create a new one.
        childrens = self.mainTable.cellWidget( row, 2 ).children()
        for c in childrens:
            try:
                btnLabel = c._label()
                if btnLabel == label:
                    c._remove_btn()
            except:
                pass

        # Add button.
        fixBtn = addnewbutton.AddBtn( id_str = checkName + checkSufix, label = label )
        # Add button to layout.
        widget.addWidget ( fixBtn )



        
def ledColor(status = None , row = int, table = None ):
    
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

def setNote(note = None, row = int, table = None ):
    
    item = QtWidgets.QTableWidgetItem( note )
    item.setFlags(QtCore.Qt.ItemIsEnabled)
    table.setItem( row, 3, item)
    



