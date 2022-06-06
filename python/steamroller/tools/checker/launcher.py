from steamroller.tools.checker import ui
import imp
imp.reload(ui)
    
try:
    CheckerUI.close() # pylint: disable=E0601
    CheckerUI.deleteLater()
except:
    pass

CheckerUI = ui.CheckerUI()
CheckerUI.show()
