#!/usr/bin/python

# gui.py

import wx
import wx.combo
import os
import Image
import socket

class MainWindow(wx.Frame):
  """This is the primary window for the program"""
  def __init__(self, *args, **kwargs):
    """Create the primary window"""
    super(MainWindow, self).__init__(*args, **kwargs)
    self.InitUI()

  def InitMenuAndStatus(self):
    """Initialize the menu bar and status bar"""
    menubar = wx.MenuBar()
    fileMenu = wx.Menu()
    fabout = fileMenu.Append(wx.ID_ABOUT, "&About",
                             " Information about this program")
    fquit = fileMenu.Append(wx.ID_EXIT, "E&xit", " Quit Application")
    menubar.Append(fileMenu, "&File")
    
    viewMenu = wx.Menu()
    fxyplot= viewMenu.AppendRadioItem(wx.ID_ANY, "XY Plot", " Do an XY Plot on the machine")
    fcalib = viewMenu.AppendRadioItem(wx.ID_ANY, "Calibrate", " Calibrate the machine")
    menubar.Append(viewMenu, "&Window")

    self.SetMenuBar(menubar)
    
    self.sb = self.CreateStatusBar()
    self.sb.SetFieldsCount(2)
    self.sb.SetStatusWidths([-5,-2])
    self.sb.SetStatusText('Hello, World!', 1);
    
    self.Bind(wx.EVT_MENU, self.OnAbout, fabout)
    self.Bind(wx.EVT_MENU, self.OnQuit, fquit)
    self.Bind(wx.EVT_MENU, self.OnXYPlot, fxyplot)
    self.Bind(wx.EVT_MENU, self.OnCalibrate, fcalib)
    
    
  def InitUI(self):
    """Initialize the primary window"""
    self.InitMenuAndStatus()

    self.xypanel = XYPanel(self)
    self.xypanel.Show()
    self.calibratepanel = CalibratePanel(self)
    self.calibratepanel.Hide()
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.sizer.Add(self.xypanel, 1, wx.EXPAND)
    self.sizer.Add(self.calibratepanel, 1, wx.EXPAND)
    self.SetSizer(self.sizer)
    self.SetTitle("XY Plot")    
    self.Centre()
  
  def OnXYPlot(self, e):
    self.SetTitle("XY Plot")
    self.xypanel.Show()
    self.calibratepanel.Hide()
    self.Layout()
  
  def OnCalibrate(self, e):
    self.SetTitle("Calibrate")
    self.xypanel.Hide()
    self.calibratepanel.Show()
    self.Layout()
  
  def OnAbout(self, e):
    dlg = wx.MessageDialog(self, "Interface for 102B", "About 102B", wx.OK)
    dlg.ShowModal()
    dlg.Destroy()
  
  def OnQuit(self, e):
    """Quit the program"""
    self.Close()

class XYPanel(wx.Panel):
  """The panel for plotting XY graphs"""
  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent)
    self.db = wx.Button(self, 10, "A Button!", (20, 20))


class CalibratePanel(wx.Panel):
  """The panel for calibrating the machine"""
  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent)
    self.parent = parent
    self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
    
    self.db = wx.Button(self, 10, "Default Button", (20, 20))
    self.picture = PictureChooser(self)

    self.fileselect = FileSelectorCombo(self, size=(250,-1))
    
    self.b = wx.Button(self, -1, "Create and Show an ImageDialog", (50,50))
    self.Bind(wx.EVT_BUTTON, self.OnButton, self.b)

    self.vertSizer = wx.BoxSizer(wx.VERTICAL)
    self.horizSizer = wx.BoxSizer(wx.HORIZONTAL)
    self.horizSizer.Add(self.db, 1, wx.EXPAND)
    self.horizSizer.Add(self.b, 1, wx.EXPAND)
    self.horizSizer.Add(self.fileselect, 1, wx.EXPAND)
    self.vertSizer.Add(self.horizSizer, 1, wx.EXPAND)
    self.vertSizer.Add(self.control, 1, wx.EXPAND)
    self.SetSizer(self.vertSizer)
    self.vertSizer.Fit(self)
    
  def OnButton(self, e):
    self.parent.Close()
  
class PictureChooser(wx.Panel):
  """Panel for displaying the picture you wish to paint"""
  def __init__(self, window):
    self.window = window
#    fileselect = FileSelectorCombo(self.window, size=(250,-1))

    
class FileSelectorCombo(wx.combo.ComboCtrl):
  def __init__(self, *args, **kw):
    wx.combo.ComboCtrl.__init__(self, *args, **kw)

    # make a custom bitmap showing "..."
    bw, bh = 14, 16
    bmp = wx.EmptyBitmap(bw,bh)
    dc = wx.MemoryDC(bmp)

 #   # clear to a specific background colour
    bgcolor = wx.Colour(255,254,255)
    dc.SetBackground(wx.Brush(bgcolor))
    dc.Clear()

    # draw the label onto the bitmap
    label = "..."
    font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
    font.SetWeight(wx.FONTWEIGHT_BOLD)
    dc.SetFont(font)
    tw,th = dc.GetTextExtent(label)
    dc.DrawText(label, (bw-tw)/2, (bw-tw)/2)
    del dc

    # now apply a mask using the bgcolor
    bmp.SetMaskColour(bgcolor)

    # and tell the ComboCtrl to use it
    self.SetButtonBitmaps(bmp, True)

    # Enable Drag and Drop
    dt = MyFileDropTarget(self)
    self.SetDropTarget(dt)
        

  # Overridden from ComboCtrl, called when the combo button is clicked
  def OnButtonClick(self):
    path = ""
    name = ""
    if self.GetValue():
      path, name = os.path.split(self.GetValue())
        
    dlg = wx.FileDialog(self, "Choose File", path, name,
                        "BMP files (*.bmp)|*.bmp", wx.FD_OPEN)
    if dlg.ShowModal() == wx.ID_OK:
      self.SetImage(dlg.GetPath())
    dlg.Destroy()
    self.SetFocus()

  def SetImage(self, path):
    if os.path.splitext(path)[1] == '.bmp':
      self.SetValue(os.path.basename(path))
  
  # Overridden from ComboCtrl to avoid assert since there is no ComboPopup
  def DoSetPopupControl(self, popup):
    pass
    
class MyFileDropTarget(wx.FileDropTarget):
  """Augments File Selector Combo with Drag n Drop"""
  def __init__(self, target):
    wx.FileDropTarget.__init__(self)
    self.target = target

  def OnDropFiles(self, x, y, filenames):
    #self.target.SetInsertionPointEnd()
    self.target.SetImage(filenames[0])
#    self.window.WriteText("\n%d file(s) dropped at %d,%d:\n" %
#                          (len(filenames), x, y))

#    for file in filenames:
#      self.window.WriteText(file + '\n')
    
 
if __name__ == '__main__':
  app = wx.App(False)
  frame = MainWindow(None)
  frame.Show()
  app.MainLoop()
