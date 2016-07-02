#	Copyright (C) 2014 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gettext import gettext as _
from gi.repository import Gtk

WINDOW_TITLE = _("PlantUML Output Visualization")


class PlantUMLWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self)		

		self.hide()
		self.set_title( WINDOW_TITLE )
		self.set_default_size(400,300)
		self.maximize()
		
		icon = Gtk.Image.new_from_stock(Gtk.STOCK_PAGE_SETUP, Gtk.IconSize.DIALOG)
		self.set_icon( icon.get_pixbuf() )
		
		self.connect("delete_event", self.on_close_callback)
			
		
	def show_msg(self, in_msg):
		# show message somehow
		pass
		
	def on_close_callback(self, in_widget, data=None):
		# Fool the default handler so that window 
		# remains open until we or gedit closes it
		return True
