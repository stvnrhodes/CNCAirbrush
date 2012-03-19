#!/usr/bin/python

# gui.py

import wx
import wx.combo
import calibratepanel as cp, xypanel as xp, meshpanel as mp
from wx.lib.wordwrap import wordwrap
import os
#import Image
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
    fcalib = viewMenu.AppendRadioItem(wx.ID_ANY, "Calibrate",
                                      " Calibrate the machine")
    fxyplot= viewMenu.AppendRadioItem(wx.ID_ANY, "XY Plot",
                                      " Do an XY Plot on the machine")
    fmesh = viewMenu.AppendRadioItem(wx.ID_ANY, "3-D Drawing",
                                     " Use all 5 dimensions to paint")
    menubar.Append(viewMenu, "&Window")

    self.SetMenuBar(menubar)
    
    self.sb = self.CreateStatusBar()
    self.sb.SetFieldsCount(2)
    self.sb.SetStatusWidths([-5,-2])
    self.sb.SetStatusText("No Communication", 1)
    
    self.Bind(wx.EVT_MENU, self.OnAbout, fabout)
    self.Bind(wx.EVT_MENU, self.OnQuit, fquit)
    self.Bind(wx.EVT_MENU, self.OnXYPlot, fxyplot)
    self.Bind(wx.EVT_MENU, self.OnCalibrate, fcalib)
    self.Bind(wx.EVT_MENU, self.OnMesh, fmesh)
    
    
  def InitUI(self):
    """Initialize the primary window"""
    self.InitMenuAndStatus()

    self.calibratepanel = cp.CalibratePanel(self)
    self.calibratepanel.Show()
    self.xypanel = xp.XYPanel(self)
    self.xypanel.Hide()
    self.meshpanel = mp.MeshPanel(self)
    self.meshpanel.Hide()
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.sizer.Add(self.calibratepanel, 1, wx.EXPAND)
    self.sizer.Add(self.xypanel, 1, wx.EXPAND)
    self.sizer.Add(self.meshpanel, 1, wx.EXPAND)
    self.SetSizer(self.sizer)
    self.SetTitle("XY Plot")    
    self.SetSize((420,300))
    self.Centre()
  
  def OnCalibrate(self, e):
    self.SetTitle("Calibrate")
    self.calibratepanel.Show()
    self.xypanel.Hide()
    self.meshpanel.Hide()
    self.calibratepanel.SetFocus()
    self.Layout()
    
  def OnXYPlot(self, e):
    self.SetTitle("XY Plot")
    self.calibratepanel.Hide()
    self.xypanel.Show()
    self.meshpanel.Hide()
    self.xypanel.SetFocus()
    self.Layout()
  
  def OnMesh(self, e):
    self.SetTitle("3-D Drawing")
    self.calibratepanel.Hide()
    self.xypanel.Hide()
    self.meshpanel.Show()
    self.meshpanel.SetFocus()
    self.Layout()
  
  def OnAbout(self, e):
    # First we create and fill the info object
    info = wx.AboutDialogInfo()
    info.Name = "CNC Airbrush Painter Interface Program"
    info.Version = "0.1"
    info.Copyright = "(C) 2012 UC Berkeley ME102B Group 13"
    info.Description = wordwrap(
      "This program is used to interface with the CNC Airbrush that Group "
      "13 is creating for ME102B at UC Berkeley.  It can be used from any "
      "computer to communicate with the device.  This program is written in "
      "python using wxPython and should be cross-platform, working on any "
      "computer that has wifi (basically all modern laptops).",
      350, wx.ClientDC(self))
    info.WebSite = ("http://sites.google.com/site/CNCAirbrushPainter",
                    "Project Website")
    info.Developers = [ "Electrical: Adam Resnick, "
                        "Software: Steven Rhodes,\n"
                        "Mechanical: Marc Russell, "
                        "Lead: Robin Young"]
                        
    info.License = wordwrap("We haven't bothered deciding on a licence yet",
                            500, wx.ClientDC(self))

    # Then we call wx.AboutBox giving it that info object
    wx.AboutBox(info)

  
  def OnQuit(self, e):
    """Quit the program"""
    self.Close()

class PictureChooser(wx.Panel):
  """Panel for displaying the picture you wish to paint"""
  def __init__(self, window):
    self.window = window
#    fileselect = FileSelectorCombo(self.window, size=(250,-1))

if __name__ == '__main__':
  app = wx.App()
  frame = MainWindow(None)
  frame.Show()
  app.MainLoop()
