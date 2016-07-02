#	Copyright (C) 2014 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gi.repository import Gtk
from .painting import Painting


class Gallery(Gtk.Notebook):
	def __init__(self):
		Gtk.Notebook.__init__(self)
		self.set_show_tabs(False)
		self.set_scrollable(False)

		self.connect('size-allocate', self.on_resize)


	def set_dock_state(self, in_is_docked):
		if in_is_docked:
			self.set_show_tabs(False)
		else:
			self.set_show_tabs(True)
			
		self.painting_refresh()
		
	
	def painting_add(self, in_painting, in_title):
		uml_filepath = in_painting.get_uml_filepath()
		reference = self.painting_exists(uml_filepath)
		if reference < 0:			
			label = Gtk.Label(in_title)
			label.set_tooltip_text(uml_filepath)
			
			self.append_page(in_painting, label)			
			self.show_all()
			return True
		else:
			return False


	def painting_remove(self, in_uml_filepath):		
		reference = self.painting_exists(in_uml_filepath)
		if reference >= 0:
			self.remove_page(reference)
			return True
		else:
			return False
			
			
	def painting_update(self, in_uml_filepath):
		reference = self.painting_exists(in_uml_filepath)
		if reference >= 0:
			self.get_nth_page(reference).update()
			self.set_current_page(reference)
			return True
		else:
			return False


	def painting_get_active(self):
		reference = self.get_current_page()
		if reference >= 0:
			return self.get_nth_page( reference )
		else:
			return None
		

	def painting_set_active(self, in_uml_filepath):		
		reference = self.painting_exists(in_uml_filepath)
		if reference >= 0:
			self.set_current_page(reference)
			self.show_all()
			return True
		else:
			return False


	def painting_exists(self, in_uml_filepath):
		reference = -1
		for i in range(self.get_n_pages()):
			item = self.get_nth_page(i)
			if in_uml_filepath == item.get_uml_filepath():
				reference = i
			
		return reference
		
		
	def painting_refresh(self):
		reference = self.get_current_page()
		if reference >= 0:
			self.get_nth_page(reference).refresh_image()		


	def on_resize(self, in_widget, in_data):
		self.painting_refresh()
