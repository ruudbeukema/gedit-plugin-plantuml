#	Copyright (C) 2014 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gi.repository import GObject, Gedit
from plantuml import view
		
class Gedit3_Plugin(GObject.Object, Gedit.WindowActivatable):
	__gtype_name__ = "Gedit3_Plugin"
    
	window = GObject.property(type=Gedit.Window)
	m_view = None

	def __init__(self):
		GObject.Object.__init__(self)
		self.m_view = view.View_Manager()


	def __del__(self):
		del self.m_view

		
	def do_activate(self):
		self.m_view.activate(self.window)


	def do_deactivate(self):
		self.m_view.deactivate(self.window)


	def do_update_state(self):		
		pass
