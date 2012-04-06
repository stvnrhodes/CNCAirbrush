#!/usr/bin/python

# gui.py

import wx, wx.combo
from wx.lib.wordwrap import wordwrap
import os
import Image, ImageFilter
from threading import Timer
import settings
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
    fshortcuts = fileMenu.Append(wx.ID_ANY, "S&hortcut List",
                                 "Show a list of all the shortcut keys")
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

    self.Bind(wx.EVT_MENU, self.OnShortcuts, fshortcuts)
    self.Bind(wx.EVT_MENU, self.OnSettings, fsettings)
    self.Bind(wx.EVT_MENU, self.OnAbout, fabout)
    self.Bind(wx.EVT_MENU, self.OnQuit, fquit)

  def _init_ui(self):
    """Initialize the primary window"""
    self.arrow_dial = ArrowDial(self)
    self.plane_points = PlanePoints(self)
    self.positions = Positions(self)
    top_horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
    top_horizontal_sizer.Add(XYPanel(self), 1, wx.EXPAND)
   # top_horizontal_sizer.Add(self.positions, 0,
    #                         wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
    bottom_horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
    bottom_horizontal_sizer.Add(self.plane_points, 0, wx.ALIGN_BOTTOM)
    bottom_horizontal_sizer.Add(wx.Size(), 1,  wx.EXPAND)
    bottom_horizontal_sizer.Add(self.arrow_dial, 0, wx.ALIGN_BOTTOM)
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
    dlg = wx.MessageDialog(self, 'I haven\'t done this bit yet',
                           'TODO',
                           wx.OK | wx.ICON_QUESTION
                           )
    dlg.ShowModal()
    dlg.Destroy()

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
    self.axis = axis
    self.text = wx.StaticText(self, wx.ID_ANY, size = (25,-1),
                              label=(self.axis + ':'))
    self.num = wx.TextCtrl(self, wx.ID_ANY, validator=NumValidator())
    self.num.Disable()
    self.set_button = wx.Button(self, size=(-1,-1), label="Go")
    self.Bind(wx.EVT_BUTTON, self._set_values, self.set_button)
    s = wx.BoxSizer(wx.HORIZONTAL)
    s.Add(self.text, 0, flag = wx.ALIGN_CENTER_VERTICAL)
    s.Add(self.num, 0, flag = wx.ALIGN_CENTER_VERTICAL)
    s.Add(self.set_button, 0, flag = wx.ALIGN_CENTER_VERTICAL)
    self.SetSizer(s)
    self.mode = 'zero'

  def enable_goto(self, goto_flag):
    """Enable GoTo Ability"""
    if goto_flag:
      self.num.Enable()
      self._bon(self.set_button)
      self.mode = 'goto'
    else:
      self.num.Disable()
      self._boff(self.set_button)
      self.mode = 'zero'

  def _boff(self, a):
    if self.axis in 'XYZxyx':
      a.SetLabel("Zero")
    else:
      a.Hide()

  def _bon(self, a):
    if self.axis in 'XYZxyx':
      a.SetLabel("Go")
    else:
      a.Show()

  def _set_values(self, e):
    if self.mode == 'goto':
      num = self.get_num()
      if num == None:
        dlg = wx.MessageDialog(self, 'Now dat just ain\'t a proper number!',
                               'I\'m afraid I can\'t let you do that...',
                               wx.OK | wx.ICON_EXCLAMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()
      else:
        print 'goto ' + str(self.get_num()) + ' on ' + self.axis
      # TODO: make machine move
    else:
      print 'zero ' + self.axis
      # TODO: make machine zero

  def get_num(self):
    """Get the number from the TextCtrl.  If it's not a number, return none"""
    _val = self.num.GetValue()
    try:
      return float(_val)
    except ValueError:
      return None


class Positions(wx.Panel):
  """Array of motor positions"""

  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent)
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
    horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
    horizontal_sizer.AddMany([(self.goto_button, 0, wx.ALIGN_CENTER),
                    (wx.StaticText(self, wx.ID_ANY,
                    "            Units:"), 0, wx.ALIGN_CENTER),
                    (self.goto_unit_select, 0, wx.ALIGN_CENTER)])

    vertical_sizer = wx.BoxSizer(wx.VERTICAL)
    vertical_sizer.Add(pos_sizer, 0)
    vertical_sizer.Add(horizontal_sizer, 1, wx.ALIGN_CENTER)
    self.SetSizer(vertical_sizer)

  def _goto_mode(self, e):
    goto_flag = self.goto_button.Value
    self.x.enable_goto(goto_flag)
    self.y.enable_goto(goto_flag)
    self.z.enable_goto(goto_flag)
    self.pan.enable_goto(goto_flag)
    self.tilt.enable_goto(goto_flag)


class ArrowDial(wx.Panel):
  """A panel for all of the calibration arrows"""

  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent)
    self.units = ["in", "mm", "mil", "step"]
    self.xUp = self._get_arrow('bitmaps/uparrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('x', '+'), self.xUp)
    self.xDown = self._get_arrow('bitmaps/downarrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('x', '-'), self.xDown)
    xbagSizer = self._get_arrow_control(self.xUp, self.xDown, "X")
    self.yUp = self._get_arrow('bitmaps/uparrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('y', '+'), self.yUp)
    self.yDown = self._get_arrow('bitmaps/downarrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('y', '-'), self.yDown)
    ybagSizer = self._get_arrow_control(self.yUp, self.yDown, "Y")
    self.zUp = self._get_arrow('bitmaps/uparrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('z', '+'), self.zUp)
    self.zDown = self._get_arrow('bitmaps/downarrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('z', '-'), self.zDown)
    zbagSizer = self._get_arrow_control(self.zUp, self.zDown, "Z")
    self.panUp = self._get_arrow('bitmaps/uparrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('pan', '+'), self.panUp)
    self.panDown = self._get_arrow('bitmaps/downarrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('pan', '-'), self.panDown)
    panbagSizer = self._get_arrow_control(self.panUp, self.panDown, "Pan")
    self.tiltUp = self._get_arrow('bitmaps/uparrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('tilt', '+'), self.tiltUp)
    self.tiltDown = self._get_arrow('bitmaps/downarrow.bmp')
    self.Bind(wx.EVT_BUTTON, lambda event: self._jog('tilt', '-'), self.tiltDown)
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
    # TODO: Add Jog
    print 'Jog ' + axis + 'in' + str(direction)


class ChoosePoint(wx.Panel):
  """A panel for holding one of the three points defining the shape"""

  def __init__(self, parent, point):
    wx.Panel.__init__(self, parent=parent)
    self.point = point
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

  def _update_point(self, xyz):
    """Store the point in the machine and update the value"""
    self.update_strings(xyz)
    # TODO: Send Data
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
    self.update_point((0,0,0))
    # TODO: Get Data

  def _tofloat(self, text):
    """Get the number from the TextCtrl.  If it's not a number, make it 0.0"""
    _val = text.GetValue()
    try:
      return float(_val)
    except ValueError:
      return 0


class PlanePoints(wx.Panel):
  """For choosing the points to define the plane"""

  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent)
    self.point_a = ChoosePoint(self, 'A')
    self.point_b = ChoosePoint(self, 'B')
    self.point_c = ChoosePoint(self, 'C')
    vert_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY,
                 "Points to define the drawing area"), wx.VERTICAL)
    vert_sizer.Add(self.point_a, flag=wx.ALIGN_CENTER_HORIZONTAL)
    vert_sizer.Add(self.point_b, flag=wx.ALIGN_CENTER_HORIZONTAL)
    vert_sizer.Add(self.point_c, flag=wx.ALIGN_CENTER_HORIZONTAL)
    self.SetSizer(vert_sizer)


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


    settings.IMG_SIZE = 400


class XYPanel(wx.Panel):

  """The panel for plotting XY graphs"""
  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent)
    self.parent = parent

    preview_button = wx.Button(self, wx.ID_ANY, "Preview")
    self.Bind(wx.EVT_BUTTON, self._on_preview, preview_button)
    
    run_button = wx.Button(self, wx.ID_ANY, "Run", size=(120,60))
    run_button.SetBackgroundColour('#00ff00')
    self.Bind(wx.EVT_BUTTON, self._on_run, run_button)

    self.fileselect = FileImageSelectorCombo(self, size=(150,-1))
    possibleColors = ["Greyscale", "Red", "Green", "Blue", "Final Image"]
    self.threshold_slider = wx.Slider(self, wx.ID_ANY, 127, 0, 255,
                                      size = (settings.IMG_SIZE, -1))
    self.Bind(wx.EVT_SCROLL_CHANGED, self._draw_altered_image,
              self.threshold_slider)
    self.color_filter = wx.Choice(self, wx.ID_ANY, (100, 50),
                                  choices = possibleColors)
    self.Bind(wx.EVT_CHOICE, self._draw_altered_image, self.color_filter)
    self.color_filter.SetSelection(0)
    filter_sizer = wx.BoxSizer(wx.HORIZONTAL)
    filter_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Filter:"), 0,
                     wx.ALIGN_CENTER),
    filter_sizer.Add(self.color_filter)
    filter_sizer.Add(preview_button)
    self.orig_image_display = wx.StaticBitmap(self, wx.ID_ANY,
                                              wx.EmptyBitmap(settings.IMG_SIZE,
                                                             settings.IMG_SIZE))
    dt = MyFileDropTarget(self.fileselect)
    self.orig_image_display.SetDropTarget(dt)
    
    left_sizer = wx.BoxSizer(wx.VERTICAL)
    left_sizer.Add(self.orig_image_display, flag = wx.ALIGN_CENTER)
    left_sizer.Add(self.fileselect, flag = wx.ALIGN_CENTER)
    left_sizer.Add(run_button, flag = wx.ALIGN_CENTER)

    self.wx_img = wx.EmptyBitmap(settings.IMG_SIZE, settings.IMG_SIZE)
    self.editImg = wx.StaticBitmap(self, wx.ID_ANY,
                   wx.EmptyBitmap(settings.IMG_SIZE, settings.IMG_SIZE))
    right_sizer = wx.BoxSizer(wx.VERTICAL)
    right_sizer.Add(self.editImg, flag = wx.ALIGN_CENTER)
    right_sizer.Add(self.threshold_slider, flag = wx.ALIGN_CENTER)
    right_sizer.Add(filter_sizer, flag = wx.ALIGN_CENTER)

    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(left_sizer, 1, wx.ALIGN_CENTER)
    sizer.Add(right_sizer, 1, wx.ALIGN_CENTER)
    self.SetSizer(sizer)

  def set_image(self, img):
    """Sets the PIL data for the image"""
    self.img = img
    self.w = wx.EmptyImage(settings.IMG_SIZE, settings.IMG_SIZE)
    myWxImage.SetData(self.parent.img.resize((settings.IMG_SIZE,
                      settings.IMG_SIZE)).convert('RGB').tostring())

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
    else:
      for i in range(3):
        s.append(source[i].point(lambda j:j > cutoff and 255))
    imgEdit = Image.merge('RGB', (s[0],s[1],s[2]))
    myWxImage = wx.EmptyImage(settings.IMG_SIZE, settings.IMG_SIZE)
    myWxImage.SetData(imgEdit.resize((settings.IMG_SIZE,
              settings.IMG_SIZE)).convert('RGB').tostring())
    self.editImg.SetBitmap(myWxImage.ConvertToBitmap())

  def _on_preview(self, e):
    # TODO: Properly size preview window
    win = SamplePic(self, "Preview", style=wx.DEFAULT_FRAME_STYLE |
                    wx.TINY_CAPTION_HORIZ, size = (800, 800), img = self.img,
                    x = self.color_filter.GetSelection(),
                    cutoff = self.threshold_slider.GetValue())
    win.CenterOnParent(wx.BOTH)
    win.Show(True)
    
  def _on_run(self, e):
    dlg = wx.MessageDialog(self, 'I haven\'t done this bit yet',
                           'TODO',
                           wx.OK | wx.ICON_QUESTION
                           )
    dlg.ShowModal()
    dlg.Destroy()



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
    myWxImage = wx.EmptyImage(settings.IMG_SIZE, settings.IMG_SIZE)
    myWxImage.SetData(self.parent.img.resize((settings.IMG_SIZE,
              settings.IMG_SIZE)).convert('RGB').tostring())
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
    wx.MiniFrame.__init__(self, parent, wx.ID_ANY, title, pos, size, style)
    panel = wx.Panel(self, wx.ID_ANY)

    source = img.resize(size).split()
    s = []
    if x == 0:
      bw = img.resize(size).convert('L').point(lambda j:j > cutoff and 255)
      s = [bw, bw, bw]
    elif x == 1:
      bw = source[0].point(lambda j:j > cutoff and 255)
      s = [bw, bw, bw]
    elif x == 2:
      bw = source[1].point(lambda j:j > cutoff and 255)
      s = [bw, bw, bw]
    elif x == 3:
#      s.append(Image.new("L", self.img.size))
      bw = source[2].point(lambda j:j > cutoff and 255)
      s = [bw, bw, bw]
    else:
      for i in range(3):
        s.append(source[i].point(lambda j:j > cutoff and 255))
    imgEdit = Image.merge('RGB', (s[0],s[1],s[2]))

    myWxImage = wx.EmptyImage(size[0], size[1])
    myWxImage.SetData(imgEdit.convert('RGB').tostring())
    self.img = wx.StaticBitmap(self, wx.ID_ANY, myWxImage.ConvertToBitmap())
    self.Bind(wx.EVT_LEFT_DCLICK, self.OnCloseMe)
    self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

  def OnCloseMe(self, event):
    self.Close(True)

  def OnCloseWindow(self, event):
    print "OnCloseWindow"
    self.Destroy()


if __name__ == '__main__':
  app = wx.App(False)
  frame = MainWindow(None)
  frame.Show()
  app.MainLoop()

