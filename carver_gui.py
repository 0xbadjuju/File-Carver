import wx
import re
import sys

import carver_common
import carver_files
import carver_partitions

APP_EXIT = 1
ID_MENU_NEW = wx.NewId()
ID_MENU_OPEN = wx.NewId()
ID_MENU_CARVE_FILES = wx.NewId()
ID_MENU_CARVE_PARTITIONS = wx.NewId()
ID_MENU_SEARCH_FILES = wx.NewId()
ID_MENU_SEARCH_PARTITIONS = wx.NewId()

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
		searchMenu = wx.Menu()
		carveMenu = wx.Menu()
		
		fileMenu.Append(ID_MENU_NEW, '&New')
		fileMenu.Append(ID_MENU_OPEN, '&Open')
		fileMenu.AppendSeparator()
		quit_menu_item = wx.MenuItem(fileMenu, APP_EXIT, '&Quit\tCtrl+C')
		fileMenu.AppendItem(quit_menu_item)
		
		carveMenu.Append(ID_MENU_CARVE_FILES, '&Files')
		carveMenu.Append(ID_MENU_CARVE_PARTITIONS, '&Partitions')

		searchMenu.Append(ID_MENU_SEARCH_FILES, '&Search Files')
		searchMenu.Append(ID_MENU_SEARCH_PARTITIONS, '&Search Partitions')

		menubar.Append(fileMenu, '&File')
		menubar.Append(searchMenu, '&Search')
		menubar.Append(carveMenu, '&Carve')
		self.SetMenuBar(menubar)

		self.Bind(wx.EVT_MENU, self.OverviewSetup, id=ID_MENU_NEW)
		self.Bind(wx.EVT_MENU, self.OverviewSetup, id=ID_MENU_OPEN)
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

		self.overview = wx.ListCtrl(panel, style=wx.LC_REPORT)
		self.overview.InsertColumn(0,'No.',width=35)
		self.overview.InsertColumn(1,'Name',width=263)
		
		grid.Add(self.overview, pos=(1, 0), flag=wx.LEFT|wx.EXPAND, border=10)

		self.selection = wx.ListCtrl(panel, style=wx.LC_REPORT|wx.LC_NO_HEADER)
		grid.Add(self.selection, pos=(1, 1), flag=wx.RIGHT|wx.EXPAND, border=10)

		grid.AddGrowableRow(1)

		self.details = wx.ListCtrl(panel, style=wx.LC_REPORT|wx.LC_NO_HEADER)
		grid.Add(self.details, pos=(2, 0), span=(1,2), flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.CENTER|wx.EXPAND, border=10)

		grid.AddGrowableRow(2)

		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.GetDetails)

		panel.SetSizer(grid)

	def OverviewSetup(self, e):
		status_bar = self.GetStatusBar()
		event_ID = e.GetId()

		if event_ID == ID_MENU_OPEN:
			self.db_info = carver_common.open_db(re.sub(".db","",self.OpenFile(self)))
		elif event_ID == ID_MENU_NEW:
			self.db_info = carver_common.new_db(self.SaveFile(self))
			carver_common.insert_list_db(self.db_info)

		self.db_info["db_cursor"].execute("SELECT * FROM files")
		self.overview.DeleteAllItems()
		while True:
			file = self.db_info["db_cursor"].fetchone()
			if file == None:
	           		break
			index = self.overview.InsertStringItem(sys.maxint, str(file[2]))
			self.overview.SetStringItem(index,1,file[0])
			index += 1
		print "\n"
		return;

	def OnQuit(self, e):
		self.Close()

	def OpenFile(self, e):
		wildcard = "SQLite file (*.db)|*.db"
		dialog = wx.FileDialog	(	
								self, 
								message="Select File", 
								defaultFile="", wildcard=wildcard,
								style=wx.OPEN|wx.CHANGE_DIR
								)
		if dialog.ShowModal() == wx.ID_OK:
			path = dialog.GetPaths()
		dialog.Destroy()
		return path[0];

	def SaveFile(self, e):
		wildcard = "SQLite file (*.db)|*.db"
		dialog = wx.FileDialog	(	
								self, 
								message="Save File",
								defaultFile="", wildcard=wildcard, 
								style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT|wx.CHANGE_DIR
								)
		if dialog.ShowModal() == wx.ID_OK:
			path = dialog.GetPaths()
		elif dialog.ShowModal() == wx.ID_CANCEL:
			return
		dialog.Destroy()
		return path[0];

	def GetDetails(self, e):
		index = e.m_itemIndex
		file = self.overview.GetItemData(index)
		print file
		print index
		carver_files.query_name_db(self.db_info, file)

def main():

    ex = wx.App()
    GUI(None)
    ex.MainLoop()    

if __name__ == '__main__':
    main()