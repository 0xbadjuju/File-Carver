import wx

import carver_common

APP_EXIT = 1
ID_MENU_NEW = wx.NewId()
ID_MENU_OPEN = wx.NewId()

class GUI(wx.Frame):
    
	def __init__(self, *args, **kwargs):
		super(GUI, self).__init__(*args, **kwargs) 
		
		self.InitUI()
		self.SetSize((600, 400))
		self.SetTitle('CarveIT')
		self.Centre()
		self.Show(True)
        
	def InitUI(self):

		#menus
		menubar = wx.MenuBar()
		fileMenu = wx.Menu()
		
		fileMenu.Append(ID_MENU_NEW, '&New')
		fileMenu.Append(ID_MENU_OPEN, '&Open')

		fileMenu.AppendSeparator()

		quit_menu_item = wx.MenuItem(fileMenu, APP_EXIT, '&Quit\tCtrl+Q')
		fileMenu.AppendItem(quit_menu_item)

		menubar.Append(fileMenu, '&File')
		self.SetMenuBar(menubar)

		self.Bind(wx.EVT_MENU, self.AccessCarver, id=ID_MENU_NEW)
		self.Bind(wx.EVT_MENU, self.AccessCarver, id=ID_MENU_OPEN)
		self.Bind(wx.EVT_MENU, self.OnQuit, quit_menu_item)

		#panels
		panel = wx.Panel(self)
		panel.SetBackgroundColour('#4f5049')

		grid = wx.GridBagSizer(3, 2)

		overview_label = wx.StaticText(panel, label="Overview")
		overview_label.SetForegroundColour('#FF8000')
		grid.Add(overview_label, pos=(0, 0), flag=wx.ALL|wx.ALIGN_CENTER, border=5)

		grid.AddGrowableCol(0)

		selection_label = wx.StaticText(panel, label="Selection")
		selection_label.SetForegroundColour('#FF8000')
		grid.Add(selection_label, pos=(0, 1), flag=wx.ALL|wx.ALIGN_CENTER, border=5)

		grid.AddGrowableCol(1)

		options = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
		grid.Add(options, pos=(1, 0), flag=wx.LEFT|wx.EXPAND, border=10)

		selection = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
		grid.Add(selection, pos=(1, 1), flag=wx.RIGHT|wx.EXPAND, border=10)

		grid.AddGrowableRow(1)

		details = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
		grid.Add(details, pos=(2, 0), span=(1,2), flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.CENTER|wx.EXPAND, border=10)

		grid.AddGrowableRow(2)

		panel.SetSizer(grid)

	def AccessCarver(self, e):
		status_bar = self.GetStatusBar()
		event_ID = e.GetId()

		if event_ID == ID_MENU_OPEN:
			db_info = carver_common.open_db("test")
		elif event_ID == ID_MENU_NEW:
			db_info = carver_common.new_db("test")

	def OnQuit(self, e):
		self.Close()

def main():

    ex = wx.App()
    GUI(None)
    ex.MainLoop()    

if __name__ == '__main__':
    main()