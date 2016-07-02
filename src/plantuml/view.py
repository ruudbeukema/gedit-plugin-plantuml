#	Copyright (C) 2014 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gettext import gettext as _
from gi.repository import GObject, Gtk, Gedit, Gdk
import cairo

from .model import Model
from .viewer import Viewer
from .puml_window import PlantUMLWindow
from .menu import Menu


# All UI-strings marked for translation are listed here for convenience
PANEL_MSG_DEFAULT 					= _("PlantUML visualization")
PANEL_MSG_PLANTUML_NOT_INSTALLED 	= _("PlantUML could not be found")
PANEL_MSG_SAVE_FILE_FIRST			= _("Please save the file first")
PANEL_MSG_FILE_NEEDS_EXTENSION		= _("(PlantUML files need to have an extension)")
PANEL_MSG_NO_VISUALIZATION			= _("No visualization for this file")
PANEL_MSG_IS_UNDOCKED				= _("Panel is undocked.")


class View_Manager():
	m_model = None
	m_puml_window = None
	m_viewer = None
	m_menu = None
	m_active_panel = None
	m_gedit_window = None
	m_gedit_bottom_panel = None
	m_gedit_side_panel = None
	
	m_plantuml_found = False
	
	m_is_docked = True
	m_dock_widget = None
	
	def __init__(self):
		self.m_model = Model()
		self.m_puml_window = PlantUMLWindow( self.on_window_close )
		self.m_viewer = Viewer( self.on_dock_toggle )
		self.m_menu = Menu( self.panel_switch )
		
		
	def __del__(self):
		del self.m_menu
		del self.m_model
		del self.m_puml_window
		del self.m_viewer


	def activate(self, in_window):
		self.m_gedit_window = in_window
		self.m_gedit_bottom_panel = in_window.get_bottom_panel()
		self.m_gedit_side_panel = in_window.get_side_panel()

		# By default, show docked in bottom panel
		self.m_active_panel = self.m_gedit_bottom_panel
		self.m_is_docked = True

		in_window.connect('active-tab-changed', self.on_tab_changed)
		in_window.connect('active-tab-state-changed', self.on_tab_state_changed)
		in_window.connect('tab-added', self.on_tab_added)
		in_window.connect('tab-removed', self.on_tab_removed)
		
		self.m_plantuml_found = self.m_model.plantuml_check_if_present()
		if self.m_plantuml_found:
			self.panel_add( Gtk.Label( PANEL_MSG_DEFAULT ) )
		else:
			self.panel_add( Gtk.Label( PANEL_MSG_PLANTUML_NOT_INSTALLED ) )

		self.m_menu.insert(in_window)


	def deactivate(self, in_window):
		self.m_menu.remove()
		self.panel_clear()


	def get_filepaths(self, in_document):
		filepath_in = ""
		filepath_out = ""

		if in_document:
			location = in_document.get_location()
			if location == None:
				self.panel_update( Gtk.Label( PANEL_MSG_SAVE_FILE_FIRST ) )
			else:
				path = location.get_path()
				if self.m_model.file_has_extension(path):
					filepath_in = path
					filepath_out = self.m_model.get_output_filepath(filepath_in)
				else:
					self.panel_update( Gtk.Label( PANEL_MSG_FILE_NEEDS_EXTENSION ) )		
		else:
			self.panel_update( Gtk.Label( PANEL_MSG_NO_VISUALIZATION ) )
		
		return (filepath_in, filepath_out)


	def panel_switch(self):
		self.dock()

		self.panel_clear()
		if self.m_active_panel == self.m_gedit_side_panel:
			self.m_active_panel = self.m_gedit_bottom_panel
		else:
			self.m_active_panel = self.m_gedit_side_panel
		self.panel_add(self.m_dock_widget)
		
		
	def panel_update(self, in_widget):
		if self.m_is_docked:
			if self.m_dock_widget != in_widget:				
				self.panel_clear()
				self.panel_add(in_widget)
						
			
	def panel_add(self, in_widget):		
		self.m_dock_widget = in_widget
		
		icon = Gtk.Image.new_from_stock(Gtk.STOCK_PAGE_SETUP, Gtk.IconSize.MENU)
		self.m_active_panel.add_item(self.m_dock_widget, "PUML_Panel", "PlantUML", icon)
		self.m_active_panel.activate_item(self.m_dock_widget)
		self.m_active_panel.show_all()

		
	def panel_clear(self):
		self.m_active_panel.remove_item(self.m_dock_widget)


	def on_tab_changed(self, in_window, in_tab, in_data=None):
		uml_filepath, img_filepath = self.get_filepaths( in_tab.get_document() )

		if uml_filepath != "":
			if self.m_viewer.uml_set_active( uml_filepath ):
				self.panel_update( self.m_viewer )
			else:
				self.panel_update( Gtk.Label( PANEL_MSG_NO_VISUALIZATION ) )


	def on_tab_state_changed(self, in_window, in_data=None):
		document = in_window.get_active_document()
		uml_filepath, img_filepath = self.get_filepaths( document )

		if uml_filepath != "":
			if self.m_viewer.uml_exists( uml_filepath ):
				if self.m_model.plantuml_run( uml_filepath, img_filepath ):
					self.m_viewer.uml_update( uml_filepath )
					self.panel_update(self.m_viewer)	
				else:
					self.panel_update( Gtk.Label( PANEL_MSG_NO_VISUALIZATION ) )


	def on_tab_added(self, in_window, in_tab, in_data=None):
		document = in_tab.get_document()
		uml_filepath, img_filepath = self.get_filepaths( document )

		if uml_filepath != "":
			if self.m_model.plantuml_run( uml_filepath, img_filepath ):
				shortname = document.get_short_name_for_display()
				self.m_viewer.uml_add( uml_filepath, img_filepath, shortname )
				self.panel_update(self.m_viewer)	
			else:
				self.panel_update( Gtk.Label( PANEL_MSG_NO_VISUALIZATION ) )


	def on_tab_removed(self, in_window, in_tab, in_data=None):
		uml_filepath, img_filepath = self.get_filepaths( in_tab.get_document() )
		if uml_filepath != "":
			self.m_viewer.uml_remove( uml_filepath )

			uml_filepath, img_filepath = self.get_filepaths( in_window.get_active_document() )
			if uml_filepath != "":	
				if self.m_viewer.uml_set_active( uml_filepath ):
					self.panel_update( self.m_viewer )
				else:
					self.panel_update( Gtk.Label( PANEL_MSG_NO_VISUALIZATION ) )

			
	def on_window_close(self, in_widget, data=None):
		self.dock()
		return True		# We don't want the default handler to be called
		
		
	def on_dock_toggle(self, in_widget):
		if self.m_is_docked:
			self.undock()
		else:
			self.dock()
		
		
	def dock(self):
		if not self.m_is_docked:
			self.m_puml_window.hide()			
			self.m_puml_window.remove(self.m_viewer)

			self.m_viewer.set_dock_state(True)
			self.m_is_docked = True

			document = self.m_gedit_window.get_active_document()
			uml_filepath, img_filepath = self.get_filepaths(document)
			if uml_filepath != "":	
				if self.m_viewer.uml_set_active( uml_filepath ):
					self.panel_update( self.m_viewer )
				else:
					self.panel_update( Gtk.Label( PANEL_MSG_NO_VISUALIZATION ) )

		
	def undock(self):
		if self.m_is_docked:
			self.panel_update( Gtk.Label( PANEL_MSG_IS_UNDOCKED ) )

			self.m_viewer.set_dock_state(False)
			self.m_puml_window.add(self.m_viewer)

			self.m_puml_window.show_all()
			self.m_is_docked = False
