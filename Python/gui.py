#!/usr/bin/python

# gui.py

import wx

app = wx.App()
frame = wx.frame(None, -1, 'CNC Airbrush Machine')
frame.Show()
app.MainLoop()