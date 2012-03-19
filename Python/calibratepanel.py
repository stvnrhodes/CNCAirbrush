import wx

class CalibratePanel(wx.Panel):
  """The panel for calibrating the machine"""
  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent)
    self.parent = parent

    self.units = ["in", "mm", "mil"]
    
    positionSizer = self.LoadMotorPositions()    

    arrowSizer = self.LoadArrowKeys()
    
    self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
    self.mainSizer.Add(positionSizer, 0, wx.ALIGN_CENTER)
    self.mainSizer.Add(arrowSizer, 1, wx.ALIGN_CENTER)
    self.SetSizer(self.mainSizer)
    
  def LoadMotorPositions(self):
    pb = wx.StaticBox(self, wx.ID_ANY, "Positions of Motors")
    pSizer = wx.StaticBoxSizer(pb, wx.VERTICAL)
    pGrid = wx.GridBagSizer(5,3)
    self.xNum = wx.TextCtrl(self, wx.ID_ANY, "0.0")
    self.xBut = wx.Button(self, wx.ID_ANY, "Zero")
    self.yNum = wx.TextCtrl(self, wx.ID_ANY, "0.0")
    self.yBut = wx.Button(self, wx.ID_ANY, "Zero")
    self.zNum = wx.TextCtrl(self, wx.ID_ANY, "0.0")
    self.zBut = wx.Button(self, wx.ID_ANY, "Zero")
    self.panNum = wx.TextCtrl(self, wx.ID_ANY, "0.0")
    self.panBut = wx.Button(self, wx.ID_ANY, "Zero")
    self.tiltNum = wx.TextCtrl(self, wx.ID_ANY, "0.0")
    self.tiltBut = wx.Button(self, wx.ID_ANY, "Zero")
    pGrid.AddMany([(wx.StaticText(self, wx.ID_ANY, "X:"), (0,0)),
                   (self.xNum, (0,1)),
                   (self.xBut, (0,2)),
                   (wx.StaticText(self, wx.ID_ANY, "Y:"), (1,0)),
                   (self.yNum, (1,1)),
                   (self.yBut, (1,2)),
                   (wx.StaticText(self, wx.ID_ANY, "Z:"), (2,0)),
                   (self.zNum, (2,1)),
                   (self.zBut, (2,2)),
                   (wx.StaticText(self, wx.ID_ANY, "Pan:"), (3,0)),
                   (self.panNum, (3,1)),
                   (self.panBut, (3,2)),
                   (wx.StaticText(self, wx.ID_ANY, "Tilt:"), (4,0)),
                   (self.tiltNum, (4,1)),
                   (self.tiltBut, (4,2))])
    self.xNum.Enable(False)
    self.yNum.Enable(False)
    self.zNum.Enable(False)
    self.panNum.Enable(False)
    self.tiltNum.Enable(False)
    pSizer.Add(pGrid, 1, wx.EXPAND)
    
    self.gotoButton = wx.ToggleButton(self, wx.ID_ANY, "Go to a Position")
    self.Bind(wx.EVT_TOGGLEBUTTON, self.GoToMode, self.gotoButton)
    self.gotoUnitSelect = wx.Choice(self, wx.ID_ANY, (10000,1000),
                                    choices = self.units)
    self.gotoUnitSelect.SetSelection(0)

    hSizer = wx.BoxSizer(wx.HORIZONTAL)
    hSizer.AddMany([(self.gotoButton, 0, wx.ALIGN_CENTER),
                    (wx.StaticText(self, wx.ID_ANY, 
                    "            Units:"), 0, wx.ALIGN_CENTER),
                    (self.gotoUnitSelect, 0, wx.ALIGN_CENTER)])

    vSizer = wx.BoxSizer(wx.VERTICAL)
    vSizer.Add(pSizer, 0)
    vSizer.Add(hSizer, 1, wx.ALIGN_CENTER)
    
    return vSizer
  
  def GoToMode(self, e):
    if e.GetEventObject().GetValue():
      self.xNum.Enable(True)
      self.yNum.Enable(True)
      self.zNum.Enable(True)
      self.panNum.Enable(True)
      self.tiltNum.Enable(True)
      self.xBut.SetLabel("Go")
      self.yBut.SetLabel("Go")
      self.zBut.SetLabel("Go")
      self.panBut.SetLabel("Go")
      self.tiltBut.SetLabel("Go")
    else:
      self.xNum.Enable(False)
      self.yNum.Enable(False)
      self.zNum.Enable(False)
      self.panNum.Enable(False)
      self.tiltNum.Enable(False)
      self.xBut.SetLabel("Zero")
      self.yBut.SetLabel("Zero")
      self.zBut.SetLabel("Zero")
      self.panBut.SetLabel("Zero")
      self.tiltBut.SetLabel("Zero")
  
  def LoadArrowKeys(self):
    self.xUp = self.GetArrow('bitmaps/uparrow.bmp')
    self.xDown = self.GetArrow('bitmaps/downarrow.bmp')
    xBagSizer = self.GetArrowControl(self.xUp, self.xDown, "X:")

    self.yUp = self.GetArrow('bitmaps/uparrow.bmp')
    self.yDown = self.GetArrow('bitmaps/downarrow.bmp')
    yBagSizer = self.GetArrowControl(self.yUp, self.yDown, "Y:")

    self.zUp = self.GetArrow('bitmaps/uparrow.bmp')
    self.zDown = self.GetArrow('bitmaps/downarrow.bmp')
    zBagSizer = self.GetArrowControl(self.zUp, self.zDown, "Z:")

    self.panUp = self.GetArrow('bitmaps/uparrow.bmp')
    self.panDown = self.GetArrow('bitmaps/downarrow.bmp')
    panBagSizer = self.GetArrowControl(self.panUp, self.panDown, "Pan:")

    self.tiltUp = self.GetArrow('bitmaps/uparrow.bmp')
    self.tiltDown = self.GetArrow('bitmaps/downarrow.bmp')
    tiltBagSizer = self.GetArrowControl(self.tiltUp, self.tiltDown, "Tilt:")

    gs = wx.GridSizer(3,3,2,2)
    gs.AddMany([(xBagSizer, 1, wx.ALIGN_RIGHT),
                (yBagSizer, 1, wx.ALIGN_RIGHT),
                (zBagSizer, 1, wx.ALIGN_RIGHT),
                (panBagSizer, 1, wx.ALIGN_RIGHT),
                (tiltBagSizer, 1, wx.ALIGN_RIGHT),
                (wx.Size(), 1, wx.EXPAND)])
                
    transSizer = wx.BoxSizer(wx.HORIZONTAL)
    self.transNum = wx.SpinCtrl(self, wx.ID_ANY, "1", size = (60,-1))
    self.transNum.SetRange(0, 10000)
    self.transUnits = wx.Choice(self, wx.ID_ANY, choices = self.units,
                                size = (40,-1))
    self.transUnits.SetSelection(0)
    transSizer.AddMany([(wx.StaticText(self, wx.ID_ANY, "Move "),
                         0, wx.ALIGN_CENTER_VERTICAL),
                        (self.transNum),
                        (self.transUnits)])

    rotSizer = wx.BoxSizer(wx.HORIZONTAL)
    self.rotNum = wx.SpinCtrl(self, wx.ID_ANY, "10", size = (60,-1))
    self.rotNum.SetRange(0, 360)

    rotSizer.AddMany([(wx.StaticText(self, wx.ID_ANY, "Move "),
                         0, wx.ALIGN_CENTER_VERTICAL),
                        (self.rotNum),
                        (wx.StaticText(self, wx.ID_ANY, " degrees"),
                         0, wx.ALIGN_CENTER_VERTICAL)])
                
    vb = wx.StaticBox(self, wx.ID_ANY, "Manual Jogging")
    vSizer = wx.StaticBoxSizer(vb, wx.VERTICAL)
    vSizer.Add(transSizer, flag = wx.ALIGN_CENTER_HORIZONTAL)
    vSizer.Add(gs, 1, wx.EXPAND)
    vSizer.Add(rotSizer, flag = wx.ALIGN_CENTER_HORIZONTAL)
    return vSizer
  
  def GetArrowControl(self, up, down, label):
    bagSizer = wx.GridBagSizer(2, 2)
    text = wx.StaticText(self, wx.ID_ANY, label)
#    text.SetFont(wx.Font(18, wx.NORMAL, wx.NORMAL, wx.NORMAL))
    bagSizer.AddMany([(text, (0,0), (2,1), wx.ALIGN_CENTER),
                       (up, (0,1)),
                       (down, (1,1))])
    return bagSizer                       
  
  def GetArrow(self, filename):
  
    bmp = wx.EmptyBitmap(1,1)
    bmp.LoadFile(filename, wx.BITMAP_TYPE_ANY)
    mask = wx.MaskColour(bmp, wx.WHITE)
    bmp.SetMask(mask)
    return wx.BitmapButton(self, -1, bmp,
                              (bmp.GetWidth()+10, bmp.GetHeight()+10))
  
  def OnButton(self, e):
    self.parent.Close()
 
  def OnKeyDown(self, e):
    keycode = event.GetKeyCode()
    if keycode == wx.WXK_ESCAPE:
      ret  = wx.MessageBox("Are you sure to quit?", 'Question', 
		                       wx.YES_NO | wx.NO_DEFAULT, self)
      if ret == wx.YES:
         self.Close()
    event.Skip()

