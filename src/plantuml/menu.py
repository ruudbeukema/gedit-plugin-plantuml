#	Copyright (C) 2014 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gettext import gettext as _
from gi.repository import GObject, Gtk, Gedit


# All UI-strings marked for translation are listed here for convenience
MENU_PLANTUML_LABEL			= _("_PlantUML docking location")
MENU_PLANTUML_TOOLTIP		= _("Select location for showing PlantUML visualization when docked")
ITEM_BOTTOMPANEL_LABEL  	= _("Dock in _bottom panel")
ITEM_BOTTOMPANEL_TOOLTIP	= _("Use bottom panel when docking PlantUML visualization")
ITEM_SIDEPANEL_LABEL  		= _("Dock in _side panel")
ITEM_SIDEPANEL_TOOLTIP		= _("Use side panel when docking PlantUML visualization")


# Menu item(s) are described as XML
UI_STR = """<ui>
<menubar name="MenuBar">
	<menu name="ToolsMenu" action="Tools">
		<placeholder name="PlantUML">
			<menu action="PlantUML">
				<menuitem name="PanelDockBottom" action="PanelDockBottom"/>
				<menuitem name="PanelDockSide" action="PanelDockSide"/>
			</menu>
		</placeholder>
	</menu>
</menubar>
</ui>
""" 


class Menu():
	m_action_group = None
	m_ui_id = None
	m_manager = None
	m_dock_location_toggle_cb = None


	def __init__(self, in_dock_location_toggle_cb):
		self.m_dock_location_toggle_cb = in_dock_location_toggle_cb

		self.m_action_group = Gtk.ActionGroup("PlantUMLPluginActions")
		self.m_action_group.add_actions([("PlantUML", None, MENU_PLANTUML_LABEL, "<Control>p", MENU_PLANTUML_TOOLTIP,
										self.on_menu_click)])

		self.m_action_group.add_radio_actions(	[('PanelDockBottom', None, ITEM_BOTTOMPANEL_LABEL, None, ITEM_BOTTOMPANEL_TOOLTIP, 0),
												('PanelDockSide', None, ITEM_SIDEPANEL_LABEL, None, ITEM_SIDEPANEL_TOOLTIP, 1)],
												0, self.on_dock_location_toggle)


	def insert(self, in_window):
		self.m_manager = in_window.get_ui_manager()
		self.m_manager.insert_action_group( self.m_action_group, -1 )
		self.m_ui_id = self.m_manager.add_ui_from_string(UI_STR)


	def remove(self):
		self.m_manager.remove_ui(self.m_ui_id)
		self.m_manager.remove_action_group(self.m_action_group)
		self.m_manager.ensure_update()


	def on_menu_click(self, in_action):
		pass


	def on_dock_location_toggle(self, in_action, in_current):
		self.m_dock_location_toggle_cb()
