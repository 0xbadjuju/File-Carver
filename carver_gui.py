import wx
import re
import os
import sys
import wx.lib.mixins.listctrl as listctrl_mixin

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
		
		self.image = "demo.dd"
        
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

		self.Bind(wx.EVT_MENU, self.CarveFiles, id=ID_MENU_CARVE_FILES)
		
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

		self.overview = ListWidthCtrl(panel, style=wx.LC_REPORT)
		self.overview.InsertColumn(0,'No.',width=35)
		self.overview.InsertColumn(1,'Name')
		grid.Add(self.overview, pos=(1, 0), flag=wx.LEFT|wx.EXPAND, border=10)

		self.selection = ListWidthCtrl(panel, style=wx.LC_REPORT|wx.LC_NO_HEADER)
		self.selection.InsertColumn(0,'Field', width=100)
		self.selection.InsertColumn(1,'Data')
		grid.Add(self.selection, pos=(1, 1), flag=wx.RIGHT|wx.EXPAND, border=10)
		
		grid.AddGrowableRow(1)

		self.details = ListWidthCtrl(panel, style=wx.LC_REPORT|wx.LC_NO_HEADER)
		self.details.InsertColumn(0,'Details')
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
		self.file = self.overview.GetItem(index, 1).GetText()
		db_query = "SELECT * FROM files WHERE name LIKE ?"
		self.db_info["db_cursor"].execute(db_query, ('%'+self.file+'%',))
		self.selection.DeleteAllItems()
		file = self.db_info["db_cursor"].fetchone()
		index = self.selection.InsertStringItem(sys.maxint, "Inode:")
		self.selection.SetStringItem(index,1,str(file[1]))
		index = self.selection.InsertStringItem(sys.maxint, "Disk Offset: ")
		self.selection.SetStringItem(index,1,str(file[3]))
		index = self.selection.InsertStringItem(sys.maxint, "File Size: ")
		self.selection.SetStringItem(index,1,str(round(file[4]/1024.0,2))+" KB")

	def CarveFiles(self, e):
		db_query = "SELECT * FROM files WHERE name LIKE ?"
		self.db_info["db_cursor"].execute(db_query,('%'+self.file+'%',))
		tempfile = re.sub("/","-",self.file)
		new_directory = self.image+"_"+tempfile+"_"+str(carver_common.get_time(self.image))
		carver_common.make_directory(new_directory)
		log = open(os.getcwd()+"/"+new_directory+"/log","a")
		while True:
			carve = self.db_info["db_cursor"].fetchone()
			if carve != None:
				if re.match('.*/', carve[0]):
					out_file = re.sub('.*/','',carve[0])
				else:
					out_file = carve[0]
				pathless_image = re.sub(".*/","",self.image)
				icat = "icat -o "+str(carve[3])+" "+self.image+" "+str(carve[1])+" > "+new_directory+"/"+out_file
				carver_common.ipc_shell(icat)
				hash = carver_common.hash_file(new_directory+"/"+out_file)
				index = self.details.InsertStringItem(sys.maxint, "File duplicated to "+os.getcwd()+"/"+new_directory+"/"+out_file)
				index = self.details.InsertStringItem(sys.maxint, "\t MD5:  "+hash[0])
				index = self.details.InsertStringItem(sys.maxint, "\t SHA1: "+hash[1]+"\n")
				try:
					log.write(out_file+"\n\tMD5:  "+hash[0]+"\n\tSHA1: "+hash[1]+"\n")
				except OSError:
					pass
			else:
				break
		log.close()
		return;

################################################################################
#Column Size Control
################################################################################
class ListWidthCtrl(wx.ListCtrl, listctrl_mixin.ListCtrlAutoWidthMixin):
	def __init__(self, *args, **kwargs):
		wx.ListCtrl.__init__(self, *args, **kwargs)
		listctrl_mixin.ListCtrlAutoWidthMixin.__init__(self)

def main():

    ex = wx.App()
    GUI(None)
    ex.MainLoop()    

if __name__ == '__main__':
    main()