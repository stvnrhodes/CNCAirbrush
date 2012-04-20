#!/usr/bin/python

# del.py

import wx


class MainWindow(wx.Frame):
  """This is the primary window for the program"""

  def __init__(self, *args, **kwargs):
    """Create the primary window"""
    super(MainWindow, self).__init__(*args, **kwargs)
    self.timer = wx.Timer(self)
    self.timer.Start(500)
    self.Bind(wx.EVT_TIMER, self.update)

  def update(self, e):
    print heyooooo


if __name__ == '__main__':
  app = wx.App(False)
  frame = MainWindow(None)
  frame.Show()
  app.MainLoop()

