#	Copyright (C) 2014 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gettext import gettext as _
from gi.repository import GObject, Gtk, Gedit, Gdk

from .model import Model
from .viewer import Viewer
from .puml_window import PlantUMLWindow


# All UI-strings marked for translation are listed here for convenience
PANEL_MSG_PLANTUML_NOT_INSTALLED 	= _("PlantUML could not be found")
PANEL_MSG_SAVE_FILE_FIRST			= _("Please save the file first")
PANEL_MSG_FILE_NEEDS_EXTENSION		= _("(PlantUML files need to have an extension)")


class View_Manager():
	m_model = None
	m_puml_window = None
	m_viewer = None
	m_gedit_window = None	
	m_plantuml_found = False
	
	def __init__(self):
		self.m_model = Model()
		self.m_puml_window = PlantUMLWindow()
		self.m_viewer = Viewer()
		
		
	def __del__(self):
		del self.m_model
		del self.m_puml_window
		del self.m_viewer


	def activate(self, in_window):
		self.m_gedit_window = in_window
		self.m_puml_window.add(self.m_viewer)		

		in_window.connect('active-tab-changed', self.on_tab_changed)
		in_window.connect('active-tab-state-changed', self.on_tab_state_changed)
		in_window.connect('tab-removed', self.on_tab_removed)
		
		self.m_plantuml_found = self.m_model.plantuml_check_if_present()
		if not self.m_plantuml_found:
			self.m_puml_window.show_message( PANEL_MSG_PLANTUML_NOT_INSTALLED )


	def deactivate(self, in_window):
		pass


	def get_filepaths(self, in_document):
		filepath_in = ""
		filepath_out = ""

		if in_document:
			location = in_document.get_location()
			if location != None:
				path = location.get_path()
				if self.m_model.file_has_extension(path):
					filepath_in = path
					filepath_out = self.m_model.get_output_filepath(filepath_in)
		
		return (filepath_in, filepath_out)


	def on_tab_changed(self, in_window, in_tab, in_data=None):
		uml_filepath, img_filepath = self.get_filepaths( in_tab.get_document() )

		if uml_filepath != "":			
			self.m_viewer.uml_set_active( uml_filepath )
			self.m_puml_window.show_all()


	def on_tab_state_changed(self, in_window, in_data=None):
		document = in_window.get_active_document()
		uml_filepath, img_filepath = self.get_filepaths( document )

		if uml_filepath != "":
			if self.m_model.plantuml_run( uml_filepath, img_filepath ):
				if not self.m_viewer.uml_update( uml_filepath ):
					shortname = document.get_short_name_for_display()
					self.m_viewer.uml_add( uml_filepath, img_filepath, shortname )
					self.m_viewer.uml_set_active( uml_filepath )
					self.m_puml_window.show_all()


	def on_tab_removed(self, in_window, in_tab, in_data=None):
		uml_filepath, img_filepath = self.get_filepaths( in_tab.get_document() )
		if uml_filepath != "":
			self.m_viewer.uml_remove( uml_filepath )
			if self.m_viewer.uml_count() == 0:
				self.m_puml_window.hide()

			uml_filepath, img_filepath = self.get_filepaths( in_window.get_active_document() )
			if uml_filepath != "":	
				self.m_viewer.uml_set_active( uml_filepath )
