# Warum auch immer ... 
###    a2p_helper.neu_helper();a2p_helper.neu()
# ist 2x auszufuehren.
# Die Anwort ist vielleicht
# https://stackoverflow.com/questions/5516783/how-to-reload-python-module-imported-using-from-module-import#comment140636199_11724550
# oder auch nicht :-(, da niemand auf "... Any suggestions?" geantwortet hat.

import os
import sys
import importlib
import pdb
import traceback
import FreeCAD
from PySide import QtGui
import a2p_importpart
#import a2p_importedPart_class

# Zugriff erfolgt auf TopLevel mit  a2p.mydebug
# Zugriff im Module erfolgt durch einfache Anweisung, zB.  mydebug=556655
# Zugriff in Module-Funktion benoetigt   global mydebug + mydebug=556655
try: mydebug==24
except: mydebug=42

def pp(*args):
  str1=""
  for arg in args:
    str1+=str(arg)+"  "
  FreeCAD.Console.PrintMessage(str1+"\n")

def pp_module(fname_module=""):
  pp(" ")
  if fname_module: pp("fname : %r" % fname_module)
  pp("mtime : %d" % os.path.getmtime(__file__))
  pp(" ")

pp_module()

def neu_helper():
  import a2p_helper
  importlib.reload(a2p_helper)

def neu():
  for name, doc in FreeCAD.listDocuments().items():
    try:
      FreeCAD.closeDocument(name)
    except:
      pp("WARNING ... could not close {name}")
#  try: FreeCAD.closeDocument(doc.Name)
#  except: pp("Nothing to close ... 'doc.Name'")
#  try: FreeCAD.closeDocument("hier_level_2")
#  except: pp("Nothing to close ... %r" % "hier_level_2")
  
  mw=FreeCAD.Gui.getMainWindow()
  global mydebug
  mydebug=mw
  mw.findChild(QtGui.QPlainTextEdit, "Python console").clear()
  mw.findChild(QtGui.QTextEdit, "Report view").clear()

  import a2p_helper
  importlib.reload(a2p_helper)
  import a2p_importpart
  importlib.reload(a2p_importpart)
  import a2p_importedPart_class
  importlib.reload(a2p_importedPart_class)
  import a2p_MuxAssembly
  importlib.reload(a2p_MuxAssembly)

  FreeCAD.newDocument()
  doc=FreeCAD.activeDocument()
  
  dirName='C:/Users/lud/Desktop/DESKTOP_ROOMING/FreeCAD/A2P_HIER_PARAMETER/'
#  a2p_importpart.importPartFromFile(
#    doc, dirName+'hier_level_2.FCStd', instanceParameters={"ww":44, "ll":22, "hh":33}
#  )
  a2p_importpart.importPartFromFile(
    doc, dirName+'hier_level_2.FCStd'
  )

  FreeCAD.Gui.SendMsgToActiveView("ViewFit")
  FreeCAD.Gui.activeDocument().activeView().viewIsometric()



# file = a2p_helper.py
import pdb
import ctypes
# Ensure a console exists
ctypes.windll.kernel32.AllocConsole()
class QtPdb(pdb.Pdb):
  def __init__(self):
    super().__init__(
      stdin=open('CONIN$', 'r'),
      stdout=open('CONOUT$', 'w')
  )

