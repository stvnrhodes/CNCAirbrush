import wx, os
import Image, ImageFilter

IMG_SIZE = 150

class XYPanel(wx.Panel):
  """The panel for plotting XY graphs"""
  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent)
    self.parent = parent
    
    self.fileselect = FileImageSelectorCombo(self, size=(150,-1))
    possibleColors = ["Black", "Red", "Blue", "Green", "Final Image"]
    self.ch = wx.Choice(self, wx.ID_ANY, (100, 50), choices = possibleColors)
    self.Bind(wx.EVT_CHOICE, self.ColorChange, self.ch)
    self.ch.SetSelection(0)
    self.wxImg = wx.StaticBitmap(self, wx.ID_ANY,
                                 wx.EmptyBitmap(IMG_SIZE, IMG_SIZE))
    leftSizer = wx.BoxSizer(wx.VERTICAL)
    leftSizer.Add(self.wxImg, flag = wx.ALIGN_CENTER)
    leftSizer.Add(self.fileselect, flag = wx.ALIGN_CENTER)
    
    self.editImg = wx.StaticBitmap(self, wx.ID_ANY,
                                 wx.EmptyBitmap(IMG_SIZE, IMG_SIZE))
    rightSizer = wx.BoxSizer(wx.VERTICAL)
    rightSizer.Add(self.editImg, flag = wx.ALIGN_CENTER)
    rightSizer.Add(self.ch, flag = wx.ALIGN_CENTER)
    
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(leftSizer, 1, wx.ALIGN_CENTER)
    sizer.Add(rightSizer, 1, wx.ALIGN_CENTER)
    self.SetSizer(sizer)

  def ColorChange(self, e):
    self.parent.sb.SetStatusText(e.GetString(), 1)
    cutoff = 127
    """
    palr = []
    palg = []
    palb = []
    for i in range(cutoff):
      palr.extend((0,0,0))
      palg.extend((0,0,0))
      palb.extend((0,0,0))
    for i in range(cutoff,256):
      palr.extend((0xff,0,0))
      palg.extend((0,0xff,0))
      palb.extend((0,0,0xff))

    imgEdit = self.img.split()
    imgEdit[0].
    if e.GetString() == "Black":
      num = 0
      for i in range(cutoff):
       pal.extend((0,0,0))
      for i in range(cutoff,256):
       pal.extend((0xff,0xff,0xff))
    if e.GetString() == "Red":
      num = 0
      for i in range(cutoff):
       pal.extend((0,0,0))
      for i in range(cutoff,256):
       pal.extend((0xff,0,0))
    if e.GetString() == "Green":
      num = 1
      for i in range(cutoff):
       pal.extend((0,0,0))
      for i in range(cutoff,256):
       pal.extend((0,0xff,0))
    if e.GetString() == "Blue":
      num = 2    
      for i in range(cutoff):
       pal.extend((0,0,0))
      for i in range(cutoff,256):
       pal.extend((0,0,0xff))
    imgEdit = self.img.split()[num]
    imgEdit.putpalette(pal)
    """
    source = self.img.split()
    s = [1, 2, 3]
    for i in range(3):
      s[i] = source[i].point(lambda j:j > cutoff and 255)
    imgEdit = Image.merge('RGB', (s[0],s[1],s[2]))
    myWxImage = wx.EmptyImage(IMG_SIZE, IMG_SIZE)
    myWxImage.SetData(imgEdit.resize((IMG_SIZE, IMG_SIZE)).convert('RGB').tostring())
    self.editImg.SetBitmap(myWxImage.ConvertToBitmap())

class FileImageSelectorCombo(wx.combo.ComboCtrl):
  def __init__(self, *args, **kw):
    wx.combo.ComboCtrl.__init__(self, *args, **kw)
    self.parent = args[0]
    
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
    myWxImage.SetData(self.parent.img.resize((IMG_SIZE, IMG_SIZE)).convert('RGB').tostring())
    self.parent.wxImg.SetBitmap(myWxImage.ConvertToBitmap())

    imgEdit = self.parent.img.split()[2]
    myWxImage = wx.EmptyImage(IMG_SIZE, IMG_SIZE)
    myWxImage.SetData(imgEdit.resize((IMG_SIZE, IMG_SIZE)).convert('RGB').tostring())
    self.parent.editImg.SetBitmap(myWxImage.ConvertToBitmap())
  
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
