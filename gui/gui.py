#!/usr/bin/python

# gui.py

import wx, wx.combo
from wx.lib.wordwrap import wordwrap
import os
import Image, ImageFilter
import mech

IMG_SIZE = 400


class MainWindow(wx.Frame):

  """This is the primary window for the program"""
  def __init__(self, *args, **kwargs):
    """Create the primary window"""
    super(MainWindow, self).__init__(*args, **kwargs)
    ib = wx.IconBundle()
    ib.AddIconFromFile("cal.ico", wx.BITMAP_TYPE_ANY)
    self.SetIcons(ib)
    self._init_menu_and_status()
    self.m = mech.Machine(self)
    self._init_ui()
    self.timer = wx.Timer(self)
    self.timer.Start(2000)
    self.Bind(wx.EVT_TIMER, self._check_ip)

  def _check_ip(self, e):
    self.m.com.check_ip()

  def _init_menu_and_status(self):
    """Initialize the menu bar and status bar"""
    menubar = wx.MenuBar()
    fileMenu = wx.Menu()
#    fshortcuts = fileMenu.Append(wx.ID_ANY, "S&hortcut List",
#                                 "Show a list of all the shortcut keys")
    fsettings = fileMenu.Append(wx.ID_ANY, "&Settings",
                                "Edit settings for the program")
    fabout = fileMenu.Append(wx.ID_ABOUT, "&About",
                             " Information about this program")
    fquit = fileMenu.Append(wx.ID_EXIT, "E&xit", " Quit Application")
    menubar.Append(fileMenu, "&File")

    self.SetMenuBar(menubar)

    self.sb = self.CreateStatusBar()
    self.sb.SetFieldsCount(2)
    self.sb.SetStatusWidths([-2,-1])
    self.sb.SetStatusText("No Communication", 1)

#    self.Bind(wx.EVT_MENU, self.OnShortcuts, fshortcuts)
    self.Bind(wx.EVT_MENU, self.OnSettings, fsettings)
    self.Bind(wx.EVT_MENU, self.OnAbout, fabout)
    self.Bind(wx.EVT_MENU, self.OnQuit, fquit)

  def _init_ui(self):
    """Initialize the primary window"""
    self.arrow_dial = ArrowDial(self)
    self.plane_points = PlanePoints(self)
    self.positions = Positions(self)
    self.pause_stop = PauseStop(self)
    top_horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
    top_horizontal_sizer.Add(XYPanel(self), 1, wx.EXPAND)
    bottom_horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
    bottom_horizontal_sizer.Add(self.plane_points, 0, wx.ALIGN_BOTTOM)
    bottom_horizontal_sizer.Add(wx.Size(), 1,  wx.EXPAND)
    mini_sizer = wx.BoxSizer(wx.VERTICAL)
    mini_sizer.Add(self.pause_stop)
    mini_sizer.Add(self.arrow_dial)
    bottom_horizontal_sizer.Add(mini_sizer, 0, wx.ALIGN_BOTTOM)
    bottom_horizontal_sizer.Add(self.positions, 0, wx.ALIGN_BOTTOM)
    self.main_sizer = wx.BoxSizer(wx.VERTICAL)
    self.main_sizer.Add(top_horizontal_sizer, 1, wx.EXPAND)
    self.main_sizer.Add(bottom_horizontal_sizer, 0, wx.EXPAND)
    self.SetSizer(self.main_sizer)
    self.SetBackgroundColour((230,230,230))
    self.SetTitle("ME102B Airbrush Program")
    self.SetSize((1024,750))
    self.Centre()
    #self.positions._goto_mode(None)

  def OnShortcuts(self, e):
    dlg = wx.MessageDialog(self, 'I haven\'t done this bit yet',
                           'TODO',
                           wx.OK | wx.ICON_QUESTION
                           )
    dlg.ShowModal()
    dlg.Destroy()

  def OnSettings(self, e):
    win = SettingsMenu(self)
    win.CenterOnParent(wx.BOTH)
    win.Show(True)

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


class AxisEdit(wx.Panel):
  """A single row in the Positions panel"""

  def __init__(self, parent, axis):
    wx.Panel.__init__(self, parent=parent)
    self.parent = parent
    self.m = parent.m
    self.axis = axis
    self.text = wx.StaticText(self, wx.ID_ANY, size = (25,-1),
                              label=(self.axis + ':'))
    self.num = wx.TextCtrl(self, wx.ID_ANY, '0', validator=NumValidator())
    self.num.Disable()
    s = wx.BoxSizer(wx.HORIZONTAL)
    s.Add(self.text, 0, flag = wx.ALIGN_CENTER_VERTICAL)
    s.Add(self.num, 0, flag = wx.ALIGN_CENTER_VERTICAL)
    self.SetSizer(s)
    self.mode = 'zero'

  def enable_goto(self, goto_flag):
    """Enable GoTo Ability"""
    if goto_flag and self.axis in 'XxYyZz':
      self.num.Enable()
      self.mode = 'goto'
    else:
      self.num.Disable()
      self.mode = 'zero'

  def get_num(self):
    """Get the number from the TextCtrl.  If it's not a number, return 0"""
    _val = self.num.GetValue()
    try:
      return float(_val)
    except ValueError:
      return 0

  def set_num(self, input):
    """Change the displayed number to the input"""
    if self.mode == 'zero':
      self.num.SetValue(repr(input))


class Positions(wx.Panel):
  """Array of motor positions"""

  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent)
    self.m = parent.m
    self.units = ["in", "mm", "mil", "step"]
    self.x = AxisEdit(self, 'X')
    self.y = AxisEdit(self, 'Y')
    self.z = AxisEdit(self, 'Z')
    self.pan = AxisEdit(self, 'Pan')
    self.tilt = AxisEdit(self, 'Tilt')
    pos_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY,
                                "Positions of Motors"), wx.VERTICAL)
    pos_sizer.Add(self.x)
    pos_sizer.Add(self.y)
    pos_sizer.Add(self.z)
    pos_sizer.Add(self.pan)
    pos_sizer.Add(self.tilt)
    self.goto_button = wx.ToggleButton(self, wx.ID_ANY, "Go to a Position")
    self.Bind(wx.EVT_TOGGLEBUTTON, self._goto_mode, self.goto_button)
    self.goto_unit_select = wx.Choice(self, wx.ID_ANY, (10000,1000),
                                    choices = self.units)
    self.goto_unit_select.SetSelection(0)
    self.Bind(wx.EVT_CHOICE, self._mech_unit_update, self.goto_unit_select)
    self.goto_unit_select.Disable()
    horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
    horizontal_sizer.AddMany([(self.goto_button, 0, wx.ALIGN_CENTER),
                    (wx.StaticText(self, wx.ID_ANY,
                    "Units:"), 0, wx.ALIGN_CENTER),
                    (self.goto_unit_select, 0, wx.ALIGN_CENTER)])

    vertical_sizer = wx.BoxSizer(wx.VERTICAL)
    vertical_sizer.Add(pos_sizer, 0, wx.ALIGN_RIGHT)
    vertical_sizer.Add(horizontal_sizer, 1, wx.ALIGN_CENTER)
    self.SetSizer(vertical_sizer)

  def _goto_mode(self, e):
    goto_flag = self.goto_button.Value
    if goto_flag:
      self.goto_button.SetLabel("Go!")
    else:
      self.m.move((self.x.get_num(), self.y.get_num(), self.z.get_num(),
                 self.pan.get_num(), self.tilt.get_num()))
      self.goto_button.SetLabel("Go to a Position")
    self.x.enable_goto(goto_flag)
    self.y.enable_goto(goto_flag)
    self.z.enable_goto(goto_flag)
    self.pan.enable_goto(goto_flag)
    self.tilt.enable_goto(goto_flag)

  def get_units(self):
    """Get the units we're currently using"""
    return self.goto_unit_select.GetStringSelection()

  def _mech_unit_update(self, e):
    self.m.set_units(self.get_units())
    pass

  def update(self, values):
    """Given all motor and servo positions, updates the displayed values"""
    self.x.set_num(values[0])
    self.y.set_num(values[1])
    self.z.set_num(values[2])
    self.pan.set_num(values[3])
    self.tilt.set_num(values[4])


class ArrowDial(wx.Panel):
  """A panel for all of the calibration arrows"""

  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent)
    self.m = parent.m
    self.units = ["in", "mm", "mil", "step"]
    self.xUp = self._get_arrow('bitmaps/uparrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('x', 1), self.xUp)
    self.xDown = self._get_arrow('bitmaps/downarrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('x', -1), self.xDown)
    xbagSizer = self._get_arrow_control(self.xUp, self.xDown, "X")
    self.yUp = self._get_arrow('bitmaps/uparrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('y', 1), self.yUp)
    self.yDown = self._get_arrow('bitmaps/downarrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('y', -1), self.yDown)
    ybagSizer = self._get_arrow_control(self.yUp, self.yDown, "Y")
    self.zUp = self._get_arrow('bitmaps/uparrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('z', 1), self.zUp)
    self.zDown = self._get_arrow('bitmaps/downarrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('z', -1), self.zDown)
    zbagSizer = self._get_arrow_control(self.zUp, self.zDown, "Z")
    self.panUp = self._get_arrow('bitmaps/uparrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('pan', 1), self.panUp)
    self.panDown = self._get_arrow('bitmaps/downarrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('pan', -1), self.panDown)
    panbagSizer = self._get_arrow_control(self.panUp, self.panDown, "Pan")
    self.tiltUp = self._get_arrow('bitmaps/uparrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('tilt', 1), self.tiltUp)
    self.tiltDown = self._get_arrow('bitmaps/downarrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('tilt', -1), self.tiltDown)
    tiltbagSizer = self._get_arrow_control(self.tiltUp, self.tiltDown, "Tilt")
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
    vs = wx.BoxSizer(wx.VERTICAL)
    vs.Add(trans_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)
    vs.Add(rot_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)
    gs = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Manual Jogging"),
                           wx.HORIZONTAL)
    gs.Add(xbagSizer, flag=wx.ALIGN_CENTER_VERTICAL)
    gs.Add(ybagSizer, flag=wx.ALIGN_CENTER_VERTICAL)
    gs.Add(zbagSizer, flag=wx.ALIGN_CENTER_VERTICAL)
    gs.Add(panbagSizer, flag=wx.ALIGN_CENTER_VERTICAL)
    gs.Add(tiltbagSizer, flag=wx.ALIGN_CENTER_VERTICAL)
    gs.AddSpacer(5)
    gs.Add(vs, flag=wx.ALIGN_CENTER_VERTICAL)

    self.SetSizer(gs)

  def _get_arrow_control(self, up, down, label):
    sizer = wx.BoxSizer(wx.VERTICAL)
    text = wx.StaticText(self, wx.ID_ANY, label)
    sizer.Add(up, flag = wx.ALIGN_CENTER_HORIZONTAL)
    sizer.Add(text, flag = wx.ALIGN_CENTER_HORIZONTAL)
    sizer.Add(down, flag = wx.ALIGN_CENTER_HORIZONTAL)
    return sizer

  def _get_arrow(self, filename):
    bmp = wx.EmptyBitmap(1,1)
    bmp.LoadFile(filename, wx.BITMAP_TYPE_ANY)
    mask = wx.MaskColour(bmp, wx.WHITE)
    bmp.SetMask(mask)
    return wx.BitmapButton(self, -1, bmp,
                           (bmp.GetWidth()+10, bmp.GetHeight()+10))

  def _jog(self, axis, direction):
    """Sends the jog command"""
    if axis in 'xXyYzZ':
      self.m.jog(axis, direction*self.trans_num.GetValue(),
                 self.trans_units.GetStringSelection())
    elif axis in 'PanpanTiltilt':
      self.m.jog(axis, direction*self.rot_num.GetValue())


class ChoosePoint(wx.Panel):
  """A panel for holding one of the three points defining the shape"""

  def __init__(self, parent, point):
    wx.Panel.__init__(self, parent=parent)
    self.point = point
    self.m = parent.m
    self.text = wx.StaticText(self, wx.ID_ANY, size = (-1,-1),
                              label=("Point " + point + ":"))
    self.x = wx.TextCtrl(self, wx.ID_ANY, validator=NumValidator())
    self.x.Disable()
    self.y = wx.TextCtrl(self, wx.ID_ANY, validator=NumValidator())
    self.y.Disable()
    self.z = wx.TextCtrl(self, wx.ID_ANY, validator=NumValidator())
    self.z.Disable()
    self.edit_button = wx.ToggleButton(self, size=(-1,-1), label="Edit")
    self.Bind(wx.EVT_TOGGLEBUTTON, self._edit_values, self.edit_button)
    self.set_button = wx.Button(self, size=(-1,-1), label="Set Current")
    self.Bind(wx.EVT_BUTTON, self._set_values, self.set_button)
    s = wx.BoxSizer(wx.HORIZONTAL)
    s.Add(self.text, 0, flag = wx.ALIGN_CENTER_VERTICAL)
    s.Add(self.x, 0, flag = wx.ALIGN_CENTER_VERTICAL)
    s.AddSpacer(5)
    s.Add(self.y, 0, flag = wx.ALIGN_CENTER_VERTICAL)
    s.AddSpacer(5)
    s.Add(self.z, 0, flag = wx.ALIGN_CENTER_VERTICAL)
    s.Add(self.edit_button, 0, flag = wx.ALIGN_CENTER_VERTICAL)
    s.Add(self.set_button, 0, flag = wx.ALIGN_CENTER_VERTICAL)
    self.SetSizer(s)

  def update_strings(self, xyz):
    """Change the TextCtrl.  Will NOT update machine"""
    self.x.SetValue(str(xyz[0]))
    self.y.SetValue(str(xyz[1]))
    self.z.SetValue(str(xyz[2]))

  def in_edit(self):
    return self.edit_button.GetValue()

  def _update_point(self, xyz):
    """Store the point in the machine and update the value"""
    self.update_strings(xyz)
    if self.point == 'A':
      self.m.set_points(p1=self._get_values())
    elif self.point == 'B':
      self.m.set_points(p2=self._get_values())
    elif self.point == 'C':
      self.m.set_points(p3=self._get_values())
    else:
      raise Exception("Invalid Point " + str(self.point))
    print 'Set Point at '  + str(xyz)

  def _edit_values(self, e):
    if e.GetEventObject().GetValue():
      self.x.Enable()
      self.y.Enable()
      self.z.Enable()
      self.edit_button.SetLabel("Done")
    else:
      self.x.Disable()
      self.y.Disable()
      self.z.Disable()
      self.edit_button.SetLabel("Edit")
      self._update_point((self._tofloat(self.x), self._tofloat(self.y),
                         self._tofloat(self.z)))

  def _set_values(self, e):
    xyz = self.m.xyz
    self._update_point(xyz)

  def _tofloat(self, text):
    """Get the number from the TextCtrl.  If it's not a number, make it 0.0"""
    _val = text.GetValue()
    try:
      return float(_val)
    except ValueError:
      return 0

  def _get_values(self):
    """Get the values of all the text controls as a tuple of floats"""
    return (self._tofloat(self.x), self._tofloat(self.y), self._tofloat(self.z))


class PlanePoints(wx.Panel):
  """For choosing the points to define the plane"""

  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent)
    self.m = parent.m
    self.point_a = ChoosePoint(self, 'A')
    self.point_b = ChoosePoint(self, 'B')
    self.point_c = ChoosePoint(self, 'C')
    point_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY,
                 "Points to define the drawing area"), wx.VERTICAL)
    point_sizer.Add(self.point_a, flag=wx.ALIGN_RIGHT)
    point_sizer.Add(self.point_b, flag=wx.ALIGN_RIGHT)
    point_sizer.Add(self.point_c, flag=wx.ALIGN_RIGHT)
    self.size_text = wx.StaticText(self, wx.ID_ANY, "Image Size is undefined")
    vertical_sizer = wx.BoxSizer(wx.VERTICAL)
    vertical_sizer.Add(point_sizer, 0)
    vertical_sizer.Add(self.size_text, 1, wx.ALIGN_CENTER)
    self.SetSizer(vertical_sizer)

  def in_edit(self):
    """Check to see if we are editing any of the ChoosePoints"""
    if self.point_a.in_edit() or self.point_b.in_edit() or self.point_c.in_edit():
      return True
    else:
      return False

  def update_size_text(self):
    """Tell the panel to poll the machine for size"""
    s = self.m.get_pic_size()
    if s:
      self.size_text.SetLabel("Image Size is %.2f %s by %.2f %s" %
                              (s[0], s[2], s[1], s[2]))
    else:
      self.size_text.SetLabel("Image Size is undefined")


class NumValidator(wx.PyValidator):
  """Only allow numbers to be entered in number fields"""

  def __init__(self, pyVar=None):
    wx.PyValidator.__init__(self)
    self.Bind(wx.EVT_CHAR, self.OnChar)

  def Clone(self):
    return NumValidator()

  def Validate(self, win):
    tc = self.GetWindow()
    try:
      float(tc.GetValue())
      return True
    except ValueError:
      return False

  def OnChar(self, event):
    key = event.GetKeyCode()
    if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
      event.Skip()
      return
    if chr(key) in '1234567890-.':
      event.Skip()
      return
    if not wx.Validator_IsSilent():
      wx.Bell()
    return


class PauseStop(wx.Panel):
  """A panel for telling the machine to stop or pause"""

  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent)
    self.parent = parent
    self.m = parent.m
    self.stop_button = wx.Button(self, wx.ID_ANY, "Stop!")
    self.stop_button.SetBackgroundColour('#ff0000')
   # self.stop_button.Disable()
    self.Bind(wx.EVT_BUTTON, self._on_stop, self.stop_button)
    self.pause_button = wx.Button(self, wx.ID_ANY, "Pause")
    self.pause_button.Disable()
    self.Bind(wx.EVT_BUTTON, self._on_pause, self.pause_button)
    self.pause_mode = 'pause'
    self.airbrush_change = wx.Button(self, wx.ID_ANY, "Change Airbrush")
    self.Bind(wx.EVT_BUTTON, self._on_airbrush_change, self.airbrush_change)
    self.solenoid_button = wx.ToggleButton(self, wx.ID_ANY, "Toggle Solenoid")
    self.Bind(wx.EVT_TOGGLEBUTTON, self._on_solenoid, self.solenoid_button)
    self.solenoid_on = False
    self.uhoh_button = wx.Button(self, wx.ID_ANY, "UhOh!")
    self.Bind(wx.EVT_BUTTON, self._uhoh, self.uhoh_button)
    topSizer = wx.BoxSizer(wx.HORIZONTAL)
    bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
    topSizer.Add(self.pause_button)
    topSizer.Add(self.stop_button)
    topSizer.Add(self.uhoh_button)
    bottomSizer.Add(self.airbrush_change)
    bottomSizer.Add(self.solenoid_button)
    mainSizer = wx.BoxSizer(wx.VERTICAL)
    mainSizer.Add(topSizer)
    mainSizer.Add(bottomSizer)
    self.SetSizer(mainSizer)

  def _uhoh(self, e):
    self.m.com.sending_command = False
    
  def _on_stop(self, e):
    self.m.stop()
    self.pause_mode = 'pause'
    self.pause_button.SetBackgroundColour('#ffff00')
    self.pause_button.SetLabel('Pause')
    
  def _on_pause(self, e):
    if 'pause' in self.pause_mode:
      self.pause_mode = 'resume'
      self.pause_button.SetBackgroundColour('#ff8800')
      self.pause_button.SetLabel('Resume')
    elif 'resume' in self.pause_mode:
      self.pause_mode = 'pause'
      self.pause_button.SetBackgroundColour('#ffff00')
      self.pause_button.SetLabel('Pause')
    self.m.pause()

  def _on_solenoid(self, e):
    self.m.run_solenoid(self.solenoid_button.Value)

  def _on_airbrush_change(self, e):
    self.m.goto_airbrush_change_position()
    
  def enable_stop(self, en):
    self.pause_button.SetLabel('Pause')
    if en:
  #    self.stop_button.Enable()
      self.stop_button.SetBackgroundColour('#ff0000')
      self.pause_button.Enable()
      self.pause_button.SetBackgroundColour('#ffff00')
      self.pause_mode = 'pause'
    else:
  #    self.stop_button.Disable()
 #     self.stop_button.SetBackgroundColour(wx.NullColor)
      self.pause_button.Disable()
      self.pause_button.SetBackgroundColour(wx.NullColor)


class XYPanel(wx.Panel):
  """The panel for plotting XY graphs"""

  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent)
    self.parent = parent
    self.m = parent.m
    self.img = None
    self.img_edit = None

    preview_button = wx.Button(self, wx.ID_ANY, "Preview")
    self.Bind(wx.EVT_BUTTON, self._on_preview, preview_button)

    save_button = wx.Button(self, wx.ID_ANY, "Save Image")
    self.Bind(wx.EVT_BUTTON, self._on_save, save_button)

    run_button = wx.Button(self, wx.ID_ANY, "Run", size=(120,60))
    run_button.SetBackgroundColour('#00ff00')
    self.Bind(wx.EVT_BUTTON, self._on_run, run_button)

    practice_run_button = wx.Button(self, wx.ID_ANY, "Run Without Painting")
    self.Bind(wx.EVT_BUTTON, self._on_fake_run, practice_run_button)

    self.fileselect = FileImageSelectorCombo(self, size=(150,-1))
    possibleColors = ["Greyscale", "Red", "Green", "Blue", "Final Image", "Edge Detection"]
    self.threshold_slider = wx.Slider(self, wx.ID_ANY, 127, 0, 255,
                                      size = (IMG_SIZE, -1))
    self.Bind(wx.EVT_SCROLL_CHANGED, self._draw_altered_image,
              self.threshold_slider)
    self.color_filter = wx.Choice(self, wx.ID_ANY, (100, 50),
                                  choices = possibleColors)
    self.Bind(wx.EVT_CHOICE, self._draw_altered_image, self.color_filter)
    self.color_filter.SetSelection(0)
    filter_sizer = wx.BoxSizer(wx.HORIZONTAL)
    filter_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Filter:"), 0,
                     wx.ALIGN_CENTER)
    filter_sizer.Add(self.color_filter)
    filter_sizer.Add(preview_button)
    filter_sizer.Add(save_button)
    self.orig_image_display = wx.StaticBitmap(self, wx.ID_ANY,
                                             wx.EmptyBitmap(IMG_SIZE, IMG_SIZE))
    dt = MyFileDropTarget(self.fileselect)
    self.orig_image_display.SetDropTarget(dt)

    left_sizer = wx.BoxSizer(wx.VERTICAL)
    left_sizer.AddSpacer(5)
    left_sizer.Add(self.orig_image_display, flag =
                   wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_TOP)
    left_sizer.Add(self.fileselect, flag =
                   wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_TOP)
    left_sizer.Add(run_button, flag =
                   wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_TOP)
    left_sizer.Add(practice_run_button, flag =
                   wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_TOP)

    self.wx_img = wx.EmptyBitmap(IMG_SIZE, IMG_SIZE)
    self.editImg = wx.StaticBitmap(self, wx.ID_ANY,
                   wx.EmptyBitmap(IMG_SIZE, IMG_SIZE))
    right_sizer = wx.BoxSizer(wx.VERTICAL)
    right_sizer.AddSpacer(5)
    right_sizer.Add(self.editImg, flag = wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_TOP)
    right_sizer.Add(self.threshold_slider, flag = wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_TOP)
    right_sizer.Add(filter_sizer, flag = wx.wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_TOP)

    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(left_sizer, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_TOP)
    sizer.Add(right_sizer, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_TOP)
    self.SetSizer(sizer)

  def _draw_altered_image(self, event = []):
    cutoff = self.threshold_slider.GetValue()
    x = self.color_filter.GetSelection()
    source = self.img.split()
    s = []
    if x == 0:
      bw = self.img.convert('L').point(lambda j:j > cutoff and 255)
      s = [bw, bw, bw]
    elif x == 1:
      bw = source[0].point(lambda j:j > cutoff and 255)
      s = [bw, bw, bw]
    elif x == 2:
      bw = source[1].point(lambda j:j > cutoff and 255)
      s = [bw, bw, bw]
    elif x == 3:
      bw = source[2].point(lambda j:j > cutoff and 255)
      s = [bw, bw, bw]
    elif x == 4:
      for i in range(3):
        s.append(source[i].point(lambda j:j > cutoff and 255))
    else:
      bw = self.img.convert('L').filter(ImageFilter.FIND_EDGES).point(lambda j:j < cutoff and 255)
      s = [bw, bw, bw]
    self.img_edit = Image.merge('RGB', (s[0],s[1],s[2]))
    myWxImage = wx.EmptyImage(IMG_SIZE, IMG_SIZE)
    myWxImage.SetData(self.img_edit.resize((IMG_SIZE,
                      IMG_SIZE)).convert('RGB').tostring())
    self.editImg.SetBitmap(myWxImage.ConvertToBitmap())

  def _on_preview(self, e):
    if self.parent.plane_points.in_edit():
      dlg = wx.MessageDialog(self, "You can\'t show a preview of the proper "
                             "size while editing the size of the drawing area "
                             "for the image. That doesn\'t make any sense at "
                             "all. It\'s just silly",
                             "Still Editing Drawing Area", wx.OK|wx.ICON_ERROR)
      dlg.ShowModal()
      dlg.Destroy()
    elif not self.m.all_points_defined():
      dlg = wx.MessageDialog(self, "You can\'t show a preview of the proper "
                                   "size if you haven't decided on its size. "
                                   "That doesn\'t make any "
                                   "sense at all.  It\'s just silly",
                                   "Undefined Points", wx.OK|wx.ICON_ERROR)
      dlg.ShowModal()
      dlg.Destroy()
    elif not self.img:
      dlg = wx.MessageDialog(self, "You can\'t show a preview of a picture if "
                                   "you haven't chosen the picture. "
                                   "That doesn\'t make any "
                                   "sense at all.  It\'s just silly",
                                   "Undefined Picture", wx.OK|wx.ICON_ERROR)
      dlg.ShowModal()
      dlg.Destroy()
    else:
      size = self.m.get_pic_pixel_count()
      win = SamplePic(self, "Preview", style=wx.DEFAULT_FRAME_STYLE |
                      wx.TINY_CAPTION_HORIZ, size=size, img=self.img_edit,
                      x=self.color_filter.GetSelection(),
                      cutoff=self.threshold_slider.GetValue())
      win.CenterOnParent(wx.BOTH)
      win.Show(True)

  def _on_fake_run(self, e):
    if self.parent.plane_points.in_edit():
      dlg = wx.MessageDialog(self, "You can\'t send the image to the machine "
                             "while still choosing where to place the image. "
                             "Stop being a dummy.",
                             "Still Editing Drawing Area", wx.OK|wx.ICON_ERROR)
      dlg.ShowModal()
      dlg.Destroy()
    elif not self.m.all_points_defined():
      dlg = wx.MessageDialog(self, "You can\'t print out an image if you "
                                   "haven't defined all of its points. Stop "
                                   "being a dummy.",
                                   "Undefined Points", wx.OK|wx.ICON_ERROR)
      dlg.ShowModal()
      dlg.Destroy()
    else:
      self.m.draw(use_solenoid=False)

  def _on_run(self, e):
    if self.parent.plane_points.in_edit():
      dlg = wx.MessageDialog(self, "You can\'t send the image to the machine "
                             "while still choosing where to place the image. "
                             "Stop being a dummy.",
                             "Still Editing Drawing Area", wx.OK|wx.ICON_ERROR)
      dlg.ShowModal()
      dlg.Destroy()
    elif not self.m.all_points_defined():
      dlg = wx.MessageDialog(self, "You can\'t print out an image if you "
                                   "haven't defined all of its points. Stop "
                                   "being a dummy.",
                                   "Undefined Points", wx.OK|wx.ICON_ERROR)
      dlg.ShowModal()
      dlg.Destroy()
    elif not self.img:
      dlg = wx.MessageDialog(self, "You can\'t print a picture if "
                                   "you haven't chosen the picture. "
                                   "Stop being a dummy.",
                                   "Undefined Picture", wx.OK|wx.ICON_ERROR)
      dlg.ShowModal()
      dlg.Destroy()
    else:
      self.m.draw(use_solenoid=True, img=self.img_edit)

  def _on_save(self, e):
    if self.img_edit != None:
      self.img_edit.convert('1').save('AlteredImage.bmp', 'bmp')


class FileImageSelectorCombo(wx.combo.ComboCtrl):

  def __init__(self, *args, **kw):
    wx.combo.ComboCtrl.__init__(self, *args, **kw)
    self.parent = args[0]
    bw, bh = 14, 16
    bmp = wx.EmptyBitmap(bw,bh)
    dc = wx.MemoryDC(bmp)
    bgcolor = wx.Colour(255,254,255)
    dc.SetBackground(wx.Brush(bgcolor))
    dc.Clear()
    label = "..."
    font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
    font.SetWeight(wx.FONTWEIGHT_BOLD)
    dc.SetFont(font)
    tw,th = dc.GetTextExtent(label)
    dc.DrawText(label, (bw-tw)/2, (bw-tw)/2)
    del dc
    bmp.SetMaskColour(bgcolor)
    self.SetButtonBitmaps(bmp, True)
    dt = MyFileDropTarget(self)
    self.SetDropTarget(dt)

  def OnButtonClick(self):
    path = ""
    name = ""
    if self.GetValue():
      path, name = os.path.split(self.GetValue())
    imageTypes = 'Image files (*.bmp;*.gif;*.jpeg;*.jpg;*.png;*.tiff)|' \
                 '*.bmp;*.gif;*.jpeg;*.jpg;*.png;*.tiff'
    dlg = wx.FileDialog(self, "Choose File", path, name,
                        imageTypes, wx.FD_OPEN)
    if dlg.ShowModal() == wx.ID_OK:
      self.SetImage(dlg.GetPath())
    dlg.Destroy()
    self.SetFocus()

  def SetImage(self, path):
    self.SetValue(os.path.basename(path))
    self.path = path
    self.parent.img = Image.open(path)
    myWxImage = wx.EmptyImage(IMG_SIZE, IMG_SIZE)
    myWxImage.SetData(self.parent.img.resize((IMG_SIZE,
                      IMG_SIZE)).convert('RGB').tostring())
    self.parent.orig_image_display.SetBitmap(myWxImage.ConvertToBitmap())
    self.parent._draw_altered_image()

  def DoSetPopupControl(self, popup):
    pass


class MyFileDropTarget(wx.FileDropTarget):
  """Augments File Selector Combo with Drag n Drop"""
  def __init__(self, target):
    wx.FileDropTarget.__init__(self)
    self.target = target

  def OnDropFiles(self, x, y, filenames):
    self.target.SetImage(filenames[0])


class SamplePic(wx.MiniFrame):

  def __init__(self, parent, title, img, x, cutoff, pos=wx.DefaultPosition,
               size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
    wx.MiniFrame.__init__(self, parent, wx.ID_ANY, title, pos,
                          (size[0] + 16, size[1] + 34), style)
    panel = wx.Panel(self, wx.ID_ANY)
    myWxImage = wx.EmptyImage(size[0], size[1])
    myWxImage.SetData(img.resize(size).convert('RGB').tostring())
    self.img = wx.StaticBitmap(self, wx.ID_ANY, myWxImage.ConvertToBitmap())
    self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

  def OnCloseWindow(self, event):
    self.Destroy()

    
class SettingsMenu(wx.MiniFrame):
  """The menu for adjusting several settings"""

  def __init__(self, parent, pos=wx.DefaultPosition,
               size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
    wx.MiniFrame.__init__(self, parent, wx.ID_ANY, "Settings", pos, size, style)
    self.m = parent.m
    sizer = wx.BoxSizer(wx.VERTICAL)
    self.steps_per_pixel = wx.SpinCtrl(self, wx.ID_ANY, "600", size = (60,-1))
    self.steps_per_pixel.SetRange(0, 10000)
    self.pixel_buffer = wx.SpinCtrl(self, wx.ID_ANY, "4", size = (60,-1))
    self.pixel_buffer.SetRange(0, 10000)
    self.feedrate = wx.SpinCtrl(self, wx.ID_ANY, "200", size = (60,-1))
    self.feedrate.SetRange(0, 10000)
    self.initial_delay = wx.SpinCtrl(self, wx.ID_ANY, "1200", size = (60,-1))
    self.initial_delay.SetRange(0, 10000)
    send_button = wx.Button(self, wx.ID_ANY, "Send to Machine")
    self.Bind(wx.EVT_BUTTON, self._on_send, send_button)
    close_button = wx.Button(self, wx.ID_EXIT, "Close")
    self.Bind(wx.EVT_BUTTON, self._on_close, close_button)

    grid = wx.GridSizer(5, 2, 2, 2)
    grid.Add(wx.StaticText(self, wx.ID_ANY, "Steps Per Pixel: "))
    grid.Add(self.steps_per_pixel)
    grid.Add(wx.StaticText(self, wx.ID_ANY, "Space between pixels: "))
    grid.Add(self.pixel_buffer)
    grid.Add(wx.StaticText(self, wx.ID_ANY, "Painting Feedrate: "))
    grid.Add(self.feedrate)
    grid.Add(wx.StaticText(self, wx.ID_ANY, "Initial Acceleration Delay: "))
    grid.Add(self.initial_delay)
    grid.Add(send_button)
    grid.Add(close_button)

    self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
    self.SetSizer(grid)
    self.SetBackgroundColour((230,230,230))
    self.SetTitle("Settings")
    self.Centre()

  def _on_send(self, e):
    self.m.send_settings(self.steps_per_pixel.GetValue(),
                         self.initial_delay.GetValue(),
                         self.pixel_buffer.GetValue(),
                         self.feedrate.GetValue())
                         
  def _on_close(self, e):
    self.Close()
    
  def OnCloseWindow(self, event):
    self.Destroy()
    
    
if __name__ == '__main__':
  app = wx.App(False)
  frame = MainWindow(None)
  frame.Show()
  app.MainLoop()

