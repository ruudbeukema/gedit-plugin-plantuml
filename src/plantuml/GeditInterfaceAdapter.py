#	Copyright (C) 2016 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
from gi.repository import GLib

from plantuml.PlantumlControl import PlantumlControl

SUPPORTED_SOURCE_FILE_EXTENSIONS = [".puml", ".plantuml", ".uml"]


class GeditInterfaceAdapter(object):
	""" 
	This class provide the logic to adapt the Gedit plugin-interface into something
	that is useful for driving PlantumlControl.
	"""

	def __init__(self, window):
		""" 
		Creates a GeditInterfaceAdapter instance
		
		:param window: Gedit window instance 
		"""
		docking_locations = self.__get_docking_locations(window)
		self.plantuml_ctrl = PlantumlControl(docking_locations)

		self.__track_tab_changes(window)
		for doc in window.get_documents():
			self.__track_document_changes(doc)

		self.glib_tag = None
		self.__on_ival_timer_timeout()

	def cleanup(self):
		""" Destroys all class instance variables """
		# Disable the asynchronous interval timer first
		if self.glib_tag:
			GLib.source_remove(self.glib_tag)
			self.glib_tag = None

		self.plantuml_ctrl.cleanup()
		self.plantuml_ctrl = None

	def __get_docking_locations(self, window):
		"""
		Obtains all possible docking locations from Gedit
		
		:param window: Gedit window instance 
		:return: references to the side and bottom docking locations (X and Y respectively) if any as:
		
		{
			'side-panel': X, 
			'bottom-panel': Y
		}
		"""
		docking_locations = {}

		try:
			docking_locations['side-panel'] = window.get_side_panel()
		except:
			docking_locations['side-panel'] = None

		try:
			docking_locations['bottom-panel'] = window.get_bottom_panel()
		except:
			docking_locations['bottom-panel'] = None

		return docking_locations

	def __track_tab_changes(self, window):
		"""
		Attaches to the right window-signals to track it for tab changes
		
		:param window: Gedit window instance
		"""
		window.connect("active-tab-changed", self.__on_active_tab_changed)
		window.connect("active-tab-state-changed", self.__on_active_tab_state_changed)
		window.connect("tab-removed", self.__on_tab_removed)
		window.connect("tabs-reordered", self.__on_tabs_reordered)

	def __track_document_changes(self, document):
		"""
		Attached to the right document-signal to track it for changes.
		
		:param document: Gedit document instance 
		"""
		document.connect("saved", self.__on_document_saved)

	def __on_ival_timer_timeout(self):
		"""
		This (asynchronous) GLib-timer callback takes care of periodically triggering PlantumlControl to process any 
		generated UML diagrams
		"""
		self.plantuml_ctrl.process_generated_uml()

		self.glib_tag = GLib.timeout_add(250, self.__on_ival_timer_timeout, priority=GLib.PRIORITY_LOW)

	def __on_active_tab_changed(self, window, tab):
		"""
		Takes care of notifying PlantumlControl about a changed active tab.
		
		:param window: Gedit window instance 
		:param tab: Gedit window tab
		"""
		path = tab.get_document().get_uri_for_display()
		if self.__get_is_puml(path):
			self.plantuml_ctrl.set_active_file(str(path))
		self.active_tab_state = tab.get_state()

	def __on_active_tab_state_changed(self, window):
		"""
		Takes care of adding new files to PlantumlControl and keeping track of their status.
		
		:param window: Gedit window instance
		"""
		# Enum Gedit.TabState not accessible, therefore hard-coding the required states as per C-API documentation:
		GEDIT_TAB_STATE_NORMAL = 0
		GEDIT_TAB_STATE_LOADING = 1

		# Newly opened documents are detected based on the tab state transition LOADING -> NORMAL
		tab = window.get_active_tab()
		new_tab_state = tab.get_state()
		if new_tab_state == GEDIT_TAB_STATE_NORMAL:
			if self.active_tab_state == GEDIT_TAB_STATE_LOADING:
				document = tab.get_document()
				path = document.get_uri_for_display()
				if self.__get_is_puml(path):
					self.plantuml_ctrl.add_file(str(path))
					self.__track_document_changes(document)
		self.active_tab_state = new_tab_state

	def __on_document_saved(self, document):
		""" 
		Notifies PlantumlControl about a saved document
		
		:param document: Gedit Document instance
		"""
		path = document.get_uri_for_display()
		if self.__get_is_puml(path):
			self.plantuml_ctrl.file_saved(path)

	def __on_tab_removed(self, window, tab):
		""" 
		Notifies PlantumlControl about a document being closed
		 
		:param window: Gedit window instance
		:param tab: Gedit Window's tab instance
		"""
		filepath = tab.get_document().get_uri_for_display()
		if self.__get_is_puml(filepath):
			self.plantuml_ctrl.remove_file(filepath)

	def __on_tabs_reordered(self, window):
		"""
		Notifies PlantumlControl about tabs being reordered. 
		:param window: Gedit window instance
		"""
		paths_list = []
		for doc in window.get_documents():
			if self.__get_is_puml(doc.get_uri_for_display()):
				paths_list.append(str(doc.get_location()))

		self.plantuml_ctrl.reorder_tabs(paths_list)

	def __get_is_puml(self, filepath):
		"""
		Determines if the given file is a valid PlantUML-file.
		 
		:param filepath: path to the file to check
		:return: True if file is a PlantUML, or False if not.
		"""
		if filepath is not None:
			_, file_extension = os.path.splitext(filepath)
			return file_extension in SUPPORTED_SOURCE_FILE_EXTENSIONS
		else:
			return False
