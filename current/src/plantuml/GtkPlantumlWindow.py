#	Copyright (C) 2014 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gettext import gettext as _
from gi.repository import Gtk

WINDOW_TITLE = _("PlantUML Viewer")


class GtkPlantumlWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self)		

		self.size = None
		self.position = None
		self.set_title( WINDOW_TITLE )
		
		icon = Gtk.Image.new_from_stock(Gtk.STOCK_PAGE_SETUP, Gtk.IconSize.DIALOG)
		self.set_icon(icon.get_pixbuf())
		
		self.connect("delete_event", self.__on_close_callback)
		self.connect("show", self.__on_show_callback)

	def __on_close_callback(self, widget, data=None):
		self.size = self.get_size()
		self.position = self.get_position()

		self.hide()

		# Fool the default handler so that window remains open until it is closed when Gedit is closed
		return True

	def __on_show_callback(self, widget, data=None):
		if self.size:
			self.resize(self.size[0], self.size[1])
			self.move(self.position[0], self.position[1])
		else:
			self.maximize()
