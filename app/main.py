import wx
from dotenv import dotenv_values

from app.database import DataSource
from app.gui import MainFrame

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame(None, DataSource(dotenv_values()))
    frame.Show(True)
    frame.init_load()
    app.MainLoop()
