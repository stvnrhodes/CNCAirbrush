#!/usr/bin/python

# gui.py

import wx
from wx.lib.wordwrap import wordwrap
from threading import Timer
import xypanel
import meshpanel
from mech import Machine, Convert


m = Machine()


class MainWindow(wx.Frame):

  """This is the primary window for the program"""
  def __init__(self, *args, **kwargs):
    """Create the primary window"""
    super(MainWindow, self).__init__(*args, **kwargs)
    self._init_ui()
    self._init_menu_and_status()

  def _init_menu_and_status(self):
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
        
  def _init_ui(self):
    """Initialize the primary window"""
    self.calibratepanel = CalibratePanel(self)
    self.calibratepanel.Show()
    self.xypanel = xypanel.XYPanel(self)
    self.xypanel.Hide()
    self.meshpanel = meshpanel.MeshPanel(self)
    self.meshpanel.Hide()
    self.panels = []
    self.panels.append(self.calibratepanel)
    self.panels.append(self.xypanel)
    self.panels.append(self.meshpanel)      
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.sizer.Add(self.calibratepanel, 1, wx.EXPAND)
    self.sizer.Add(self.xypanel, 1, wx.EXPAND)
    self.sizer.Add(self.meshpanel, 1, wx.EXPAND)
    self.SetSizer(self.sizer)
    self.SetTitle("XY Plot")    
    self.SetSize((420,300))
    self.Centre()
  
  def OnCalibrate(self, e):
    """Change to the Calibrate Panel"""
    self.SetTitle("Calibrate")
    self.switch_panel('calibratepanel')
    
  def OnXYPlot(self, e):
    """Change to the XY Drawing Panel"""
    self.SetTitle("XY Plot")
    self.switch_panel('xypanel')
  
  def OnMesh(self, e):
    """Change to the 3-D Drawing Panel"""
    self.SetTitle("3-D Drawing")
    self.switch_panel('meshpanel')
    
  def switch_panel(self, panel):
    for x in self.panels:
      if x != self.__dict__[panel]:
        x.Hide()
    self.__dict__[panel].Show()
    self.__dict__[panel].SetFocus()
    self.Layout()
    
  def OnAbout(self, e):
    """Display the about dialog for the program."""
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
    info.Developers = [ "Electrical: Adam Resnick,\n"
                        "Software: Steven Rhodes,\n"
                        "Mechanical: Marc Russell,\n"
                        "Lead: Robin Young"]
    info.License = wordwrap("We haven't bothered deciding on a licence yet",
                            500, wx.ClientDC(self))
    wx.AboutBox(info)
  
  def OnQuit(self, e):
    """Quit the program"""
    self.Close()

    
class CalibratePanel(wx.Panel):
  """The panel for calibrating the machine"""

  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent)
    self.parent = parent
    self.units = ["in", "mm", "mil"]

    position_sizer = self._load_motor_positions()    

    arrow_sizer = self._load_arrow_keys()
    
    self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
    self.main_sizer.Add(position_sizer, 0, wx.ALIGN_CENTER)
    self.main_sizer.Add(arrow_sizer, 1, wx.ALIGN_CENTER)
    self.SetSizer(self.main_sizer)
    
  def _load_motor_positions(self):
    pb = wx.StaticBox(self, wx.ID_ANY, "Positions of Motors")
    p_sizer = wx.StaticBoxSizer(pb, wx.VERTICAL)
    p_grid = wx.GridBagSizer(5,3)
    self.x_num = wx.TextCtrl(self, wx.ID_ANY, "0.0")
    self.x_but = wx.Button(self, wx.ID_ANY, "Zero")
    self.y_num = wx.TextCtrl(self, wx.ID_ANY, "0.0")
    self.y_but = wx.Button(self, wx.ID_ANY, "Zero")
    self.z_num = wx.TextCtrl(self, wx.ID_ANY, "0.0")
    self.z_but = wx.Button(self, wx.ID_ANY, "Zero")
    self.pan_num = wx.TextCtrl(self, wx.ID_ANY, "0.0")
    self.pan_but = wx.Button(self, wx.ID_ANY, "Zero")
    self.tilt_num = wx.TextCtrl(self, wx.ID_ANY, "0.0")
    self.tilt_but = wx.Button(self, wx.ID_ANY, "Zero")
    p_grid.AddMany([(wx.StaticText(self, wx.ID_ANY, "X:"), (0,0)),
                   (self.x_num, (0,1)),
                   (self.x_but, (0,2)),
                   (wx.StaticText(self, wx.ID_ANY, "Y:"), (1,0)),
                   (self.y_num, (1,1)),
                   (self.y_but, (1,2)),
                   (wx.StaticText(self, wx.ID_ANY, "Z:"), (2,0)),
                   (self.z_num, (2,1)),
                   (self.z_but, (2,2)),
                   (wx.StaticText(self, wx.ID_ANY, "Pan:"), (3,0)),
                   (self.pan_num, (3,1)),
                   (self.pan_but, (3,2)),
                   (wx.StaticText(self, wx.ID_ANY, "Tilt:"), (4,0)),
                   (self.tilt_num, (4,1)),
                   (self.tilt_but, (4,2))])
    self.x_num.Enable(False)
    self.y_num.Enable(False)
    self.z_num.Enable(False)
    self.pan_num.Enable(False)
    self.tilt_num.Enable(False)
    p_sizer.Add(p_grid, 1, wx.EXPAND)
    
    self.goto_button = wx.ToggleButton(self, wx.ID_ANY, "Go to a Position")
    self.Bind(wx.EVT_TOGGLEBUTTON, self._go_to_mode, self.goto_button)
    self.goto_unit_select = wx.Choice(self, wx.ID_ANY, (10000,1000),
                                    choices = self.units)
    self.goto_unit_select.SetSelection(0)

    h_sizer = wx.BoxSizer(wx.HORIZONTAL)
    h_sizer.AddMany([(self.goto_button, 0, wx.ALIGN_CENTER),
                    (wx.StaticText(self, wx.ID_ANY, 
                    "            Units:"), 0, wx.ALIGN_CENTER),
                    (self.goto_unit_select, 0, wx.ALIGN_CENTER)])

    v_sizer = wx.BoxSizer(wx.VERTICAL)
    v_sizer.Add(p_sizer, 0)
    v_sizer.Add(h_sizer, 1, wx.ALIGN_CENTER)
    return v_sizer
  
  def _go_to_mode(self, e):
    if e.GetEventObject().GetValue():
      self.x_num.Enable(True)
      self.y_num.Enable(True)
      self.z_num.Enable(True)
      self.pan_num.Enable(True)
      self.tilt_num.Enable(True)
      self.x_but.SetLabel("Go")
      self.y_but.SetLabel("Go")
      self.z_but.SetLabel("Go")
      self.pan_but.SetLabel("Go")
      self.tilt_but.SetLabel("Go")
    else:
      self.x_num.Enable(False)
      self.y_num.Enable(False)
      self.z_num.Enable(False)
      self.pan_num.Enable(False)
      self.tilt_num.Enable(False)
      self.x_but.SetLabel("Zero")
      self.y_but.SetLabel("Zero")
      self.z_but.SetLabel("Zero")
      self.pan_but.SetLabel("Zero")
      self.tilt_but.SetLabel("Zero")
  
  def _load_arrow_keys(self):
    self.xUp = self._get_arrow('bitmaps/uparrow.bmp')
    self.xDown = self._get_arrow('bitmaps/downarrow.bmp')
    xbagSizer = self._get_arrow_control(self.xUp, self.xDown, "X:")

    self.yUp = self._get_arrow('bitmaps/uparrow.bmp')
    self.yDown = self._get_arrow('bitmaps/downarrow.bmp')
    ybagSizer = self._get_arrow_control(self.yUp, self.yDown, "Y:")

    self.zUp = self._get_arrow('bitmaps/uparrow.bmp')
    self.zDown = self._get_arrow('bitmaps/downarrow.bmp')
    zbagSizer = self._get_arrow_control(self.zUp, self.zDown, "Z:")

    self.panUp = self._get_arrow('bitmaps/uparrow.bmp')
    self.panDown = self._get_arrow('bitmaps/downarrow.bmp')
    panbagSizer = self._get_arrow_control(self.panUp, self.panDown, "Pan:")

    self.tiltUp = self._get_arrow('bitmaps/uparrow.bmp')
    self.tiltDown = self._get_arrow('bitmaps/downarrow.bmp')
    tiltbagSizer = self._get_arrow_control(self.tiltUp, self.tiltDown, "Tilt:")

    gs = wx.GridSizer(3,3,2,2)
    gs.AddMany([(xbagSizer, 1, wx.ALIGN_RIGHT),
                (ybagSizer, 1, wx.ALIGN_RIGHT),
                (zbagSizer, 1, wx.ALIGN_RIGHT),
                (panbagSizer, 1, wx.ALIGN_RIGHT),
                (tiltbagSizer, 1, wx.ALIGN_RIGHT),
                (wx.Size(), 1, wx.EXPAND)])
                
    trans_sizer = wx.BoxSizer(wx.HORIZONTAL)
    self.trans_num = wx.SpinCtrl(self, wx.ID_ANY, "1", size = (60,-1))
    self.trans_num.SetRange(0, 10000)
    self.trans_units = wx.Choice(self, wx.ID_ANY, choices = self.units,
                                size = (40,-1))
    self.trans_units.SetSelection(0)
    trans_sizer.AddMany([(wx.StaticText(self, wx.ID_ANY, "Move "),
                         0, wx.ALIGN_CENTER_VERTICAL),
                        (self.trans_num),
                        (self.trans_units)])

    rot_sizer = wx.BoxSizer(wx.HORIZONTAL)
    self.rot_num = wx.SpinCtrl(self, wx.ID_ANY, "10", size = (60,-1))
    self.rot_num.SetRange(0, 360)

    rot_sizer.AddMany([(wx.StaticText(self, wx.ID_ANY, "Move "),
                         0, wx.ALIGN_CENTER_VERTICAL),
                        (self.rot_num),
                        (wx.StaticText(self, wx.ID_ANY, " degrees"),
                         0, wx.ALIGN_CENTER_VERTICAL)])
                
    vb = wx.StaticBox(self, wx.ID_ANY, "Manual Jogging")
    v_sizer = wx.StaticBoxSizer(vb, wx.VERTICAL)
    v_sizer.Add(trans_sizer, flag = wx.ALIGN_CENTER_HORIZONTAL)
    v_sizer.Add(gs, 1, wx.EXPAND)
    v_sizer.Add(rot_sizer, flag = wx.ALIGN_CENTER_HORIZONTAL)
    return v_sizer
  
  def _get_arrow_control(self, up, down, label):
    bag_sizer = wx.GridBagSizer(2, 2)
    text = wx.StaticText(self, wx.ID_ANY, label)
#    text.SetFont(wx.Font(18, wx.NORMAL, wx.NORMAL, wx.NORMAL))
    bag_sizer.AddMany([(text, (0,0), (2,1), wx.ALIGN_CENTER),
                       (up, (0,1)),
                       (down, (1,1))])
    return bag_sizer                       
  
  def _get_arrow(self, filename):
    bmp = wx.EmptyBitmap(1,1)
    bmp.LoadFile(filename, wx.BITMAP_TYPE_ANY)
    mask = wx.MaskColour(bmp, wx.WHITE)
    bmp.SetMask(mask)
    return wx.BitmapButton(self, -1, bmp,
                           (bmp.GetWidth()+10, bmp.GetHeight()+10))

  def OnKeyDown(self, e):
    keycode = event.GetKeyCode()
    if keycode == wx.WXK_ESCAPE:
      ret  = wx.MessageBox("Are you sure to quit?", 'Question', 
		                       wx.YES_NO | wx.NO_DEFAULT, self)
      if ret == wx.YES:
         self.Close()
    event.Skip()
    
if __name__ == '__main__':
  app = wx.App(False)
  frame = MainWindow(None)
  frame.Show()
  app.MainLoop()

