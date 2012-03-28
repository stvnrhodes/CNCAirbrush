import wx
import cube

class MeshPanel(wx.Panel):
  """The panel for doing the complex mapping"""
  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent)
    pb = wx.StaticBox(self, wx.ID_ANY, "Cube")
    pSizer = wx.StaticBoxSizer(pb, wx.VERTICAL)
    c = cube.CubeCanvas(self)
    c.SetSize((200, 200))    
    pSizer.Add(c, 0, wx.ALIGN_CENTER)
    self.SetSizer(pSizer)
