#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2019 kbwbe                                              *
#*                                                                         *
#*   Portions of code based on hamish's assembly 2                         *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************

### lutz_dd, 2025_12_12 ... start
import importlib
import a2p_helper
importlib.reload(a2p_helper)
a2p_helper.pp_module(__file__)
mydebug=42
import a2p_MuxAssembly
### lutz_dd, 2025_12_12 ... end

import FreeCAD
import FreeCADGui
import Part
import os
import time
import copy
import numpy
from FreeCAD import  Base
from PySide import QtGui
from a2p_translateUtils import *
import a2plib
import traceback
import pdb

#==============================================================================
class Proxy_importPart:
    """The a2p importPart object."""

    def __init__(self,obj):
#HACK lutz_dd
        FreeCAD.Console.PrintMessage("Proxy_importPart::__init__\n")
        obj.Proxy = self
        Proxy_importPart.setProperties(self,obj)
        self.type = "a2p_importPart"

    def setProperties(self,obj):
#HACK lutz_dd
        FreeCAD.Console.PrintMessage("Proxy_importPart::setProperties\n")
        propList = obj.PropertiesList

        if not "objectType" in propList:
            obj.addProperty("App::PropertyString", "objectType", "importPart")
            obj.objectType = 'a2pPart'
        if not "a2p_Version" in propList:
            obj.addProperty("App::PropertyString", "a2p_Version", "importPart")
            obj.a2p_Version = a2plib.getA2pVersion()
        if not "sourceFile" in propList:
            obj.addProperty("App::PropertyFile", "sourceFile", "importPart")
        if not "sourcePart" in propList:
            obj.addProperty("App::PropertyString", "sourcePart", "importPart")
        if not "localSourceObject" in propList:
            obj.addProperty("App::PropertyString", "localSourceObject", "importPart")
        if not "muxInfo" in propList:
            obj.addProperty("App::PropertyStringList","muxInfo","importPart")
        if not "timeLastImport" in propList:
            obj.addProperty("App::PropertyFloat", "timeLastImport","importPart")
        if not "fixedPosition" in propList:
            obj.addProperty("App::PropertyBool","fixedPosition","importPart")
        if not "subassemblyImport" in propList:
            obj.addProperty("App::PropertyBool","subassemblyImport","importPart")
            obj.subassemblyImport = False
        if not "updateColors" in propList:
            obj.addProperty("App::PropertyBool","updateColors","importPart")
            obj.updateColors = True
        if a2plib.GRAPHICALDEBUG == True and not "debugmode" in propList:
            obj.addProperty("App::PropertyBool","debugmode","importPart")
            obj.debugmode = False
        if a2plib.GRAPHICALDEBUG == False and "debugmode" in propList:
            obj.removeProperty("debugmode")

        self.type = "a2p_importPart"

    def onDocumentRestored(self,obj):
        Proxy_importPart.setProperties(self,obj)

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def dumps(self):
        return None

    def loads(self, state):
        return None

    def execute(self, obj):
        # if a group containing LCS's exists, then move it
        # according to the imported part
        if hasattr(obj,"lcsLink"):
            if len(obj.lcsLink) > 0:
                lcsGroup = obj.lcsLink[0]
                lcsGroup.Placement = obj.Placement
                lcsGroup.purgeTouched() #untouch the lcsGroup, otherwise it stays touched.

### lutz_dd, 2025_12_12 ... start
    def onChanged(self, fp, prop):
        a2p_helper.pp("Proxy_importPart::onChanged ... \t fp:%r \t prop:%r" % (fp.Label, prop))
        # Nur reagieren, wenn es ein Instanz-Parameter ist
        if prop in fp.PropertiesList and prop not in [
            "Proxy", "Label", "Placement", "Shape"
            # HACK ... lutz_dd ... Umstellen auf Suche nach "par_" am Anfang von prop
            , "sourceFile"
            , "timeLastImport", "fixedPosition", "subassemblyImport", "muxInfo"
        ]:
            try:
                # Child-Dokument öffnen oder referenzieren
                importDoc = None
                if "sourceFile" in dir(fp):
                  if (os.path.isfile(fp.sourceFile) and fp.sourceFile.lower().endswith(".fcstd")):
                    for d in FreeCAD.listDocuments().values():
                        if os.path.normpath(d.FileName) == os.path.normpath(fp.sourceFile):
                            importDoc = d
                            break
                    if importDoc is None:
                        importDoc = FreeCAD.openDocument(fp.sourceFile)

                # Spreadsheet "Parameters" im Child aktualisieren
                if importDoc:
                    sheet = None
                    for o in importDoc.Objects:
                        if o.TypeId == "Spreadsheet::Sheet" and o.Label == "Parameters":
                            sheet = o
                            break
                    if sheet:
                        # Beruecksichtigen, das 'par_' beim Platzieren hinzugefuegt wurde.
                        subprop=prop.replace("par_","")
                        sheet.set(subprop, str(getattr(fp, prop)))
                        importDoc.recompute()
                        FreeCAD.Console.PrintMessage(
                            f"[A2plus] {subprop} aktualisiert: {getattr(fp, prop)}\n"
                        )
                        # HACK ... einfach die aktuelle Zeit verwendet
#                        fp.setEditorMode("timeLastImport",1)
#                        fp.timeLastImport=time.time()

                    a2p_helper.pp("-"*22)
                    a2p_helper.pp(__file__,"importDoc",importDoc)
                    a2p_helper.pp(__file__,"importDoc.Name",importDoc.Name)
                    a2p_helper.pp("x"*22)
                    fp.muxInfo, fp.Shape, fp.ViewObject.DiffuseColor, fp.ViewObject.Transparency = \
                         a2p_MuxAssembly.muxAssemblyWithTopoNames(importDoc)
                    a2p_helper.pp("_"*22)
#                    fp.Document.recompute()
#                    if importToCache: # this import is used to update already imported parts
#                      objectCache.add(cacheKey, fp)

                global mydebug
                mydebug=fp
                
            except Exception as e:
                FreeCAD.Console.PrintError(traceback.format_exc())
                FreeCAD.Console.PrintError(f"[A2plus] Fehler beim Aktualisieren von {prop}: {e}\n")


    if 1==0:
      def onChanged(self, fp, prop):
          if prop in ["CubeSize", "ww"]:
              try:
                  # Child-Dokument öffnen oder referenzieren
                  importDoc = None
                  if os.path.isfile(fp.sourceFile) and fp.sourceFile.lower().endswith(".fcstd"):
                      for d in FreeCAD.listDocuments().values():
                          if os.path.normpath(d.FileName) == os.path.normpath(fp.sourceFile):
                              importDoc = d
                              break
                      if importDoc is None:
                          importDoc = FreeCAD.openDocument(fp.sourceFile)

                  # Spreadsheet "Parameters" im Child aktualisieren
                  if importDoc:
                      sheet = None
                      for o in importDoc.Objects:
                          if o.TypeId == "Spreadsheet::Sheet" and o.Label == "Parameters":
                              sheet = o
                              break
                      if sheet:
                          sheet.set(prop, str(getattr(fp, prop)))
                          importDoc.recompute()
                          FreeCAD.Console.PrintMessage(
                              f"[A2plus] {prop} aktualisiert: {getattr(fp, prop)}\n"
                          )
              except Exception as e:
                  FreeCAD.Console.PrintError(f"[A2plus] Fehler beim Aktualisieren von {prop}: {e}\n")

    if 1==0:
      def onChanged(self, fp, prop):
          if prop == "instanceParameters":
              try:
                  # Spreadsheet im importierten Dokument aktualisieren
                  importDoc = FreeCAD.openDocument(fp.sourceFile)
                  sheet = None
                  for o in importDoc.Objects:
                      if o.TypeId == "Spreadsheet::Sheet" and o.Label == "Parameters":
                          sheet = o
                          break
                  if sheet:
                      for k, v in fp.instanceParameters.items():
                          sheet.set(k, str(v))
                      importDoc.recompute()
                      FreeCAD.Console.PrintMessage(
                          f"[A2plus] Aktualisiert: {fp.Label}.instanceParameters → {fp.instanceParameters}\n"
                      )
              except Exception as e:
                  FreeCAD.Console.PrintError(f"[A2plus] Fehler beim Aktualisieren: {e}\n")

### lutz_dd, 2025_12_12 ... end



#==============================================================================
class ImportedPartViewProviderProxy:
    """A ViewProvider for the a2p importPart object."""

    def __init__(self,vobj):
        vobj.Proxy = self

    def claimChildren(self):
        if hasattr(self,'Object'):
            try:
                children = list()
                for obj in self.Object.InList:
                    if a2plib.isA2pObject(obj):
                        children.append(obj)
                if hasattr(self.Object,'lcsLink'):
                    for obj in self.Object.lcsLink:
                        children.append(obj)
                return children
            except:
                # FreeCAD has already deleted self.Object !!
                return[]
        else:
            return []

    def onDelete(self, viewObject, subelements):  # subelements is a tuple of strings
        if FreeCAD.activeDocument() != viewObject.Object.Document:
            return False  # only delete objects in the active Document anytime !!
        obj = viewObject.Object
        doc = obj.Document

        deleteList = []
        for c in doc.Objects:
            if 'ConstraintInfo' in c.Content:  # a related Constraint
                if obj.Name in [ c.Object1, c.Object2 ]:
                    deleteList.append(c)
        if len(deleteList) > 0:
            for c in deleteList:
                a2plib.removeConstraint(c)  # also deletes the mirrors...

        if hasattr(obj,"lcsLink"):
            if len(obj.lcsLink)>0:
                lscGroup = doc.getObject(obj.lcsLink[0].Name)
                lscGroup.deleteContent(doc)
                doc.removeObject(lscGroup.Name)

        return True  # If False is returned the object won't be deleted

    def getIcon(self):
        if hasattr(self,"Object"):
            if a2plib.isA2pSketch(self.Object):
                return a2plib.get_module_path()+'/icons/a2p_SketchReference.svg'
            if hasattr(self.Object,"sourceFile") and hasattr(self.Object,"sourcePart"):
                if self.Object.sourcePart is not None and self.Object.sourcePart !='':
                    return a2plib.get_module_path()+'/icons/a2p_ObjReference.svg'
            if hasattr(self.Object,"subassemblyImport"):
                if self.Object.subassemblyImport:
                    return ":/icons/a2p_Asm.svg"
            if hasattr(self.Object,"sourceFile"):
                if self.Object.sourceFile == 'converted':
                    return ":/icons/a2p_ConvertPart.svg"
        return ":/icons/a2p_Obj.svg"

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def dumps(self):
        return None

    def loads(self, state):
        return None

    def attach(self, vobj):
        self.object_Name = vobj.Object.Name
        self.Object = vobj.Object

    def setupContextMenu(self, ViewObject, popup_menu):
        pass

#==============================================================================
class Proxy_muxAssemblyObj(Proxy_importPart):
    """
    A wrapper for compatibility reasons...
    """
    pass
#==============================================================================
class Proxy_convertPart(Proxy_importPart):
    """
    A wrapper for compatibility reasons...
    """
    pass
#==============================================================================
