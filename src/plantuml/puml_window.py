#	Copyright (C) 2014 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gettext import gettext as _
from gi.repository import Gtk


class PlantUMLWindow(Gtk.Window):
	def __init__(self, in_on_close_callback):
		Gtk.Window.__init__(self)		

		self.hide()
		self.set_title(_("PlantUML Visualization"))
		self.set_default_size(400,300)
		
		icon = Gtk.Image.new_from_stock(Gtk.STOCK_PAGE_SETUP, Gtk.IconSize.MENU)
		self.set_icon( icon.get_pixbuf() )
		
		self.connect("delete_event", in_on_close_callback)
	
		
	def show_all(self):
		Gtk.Window.show_all(self)
		self.maximize()
