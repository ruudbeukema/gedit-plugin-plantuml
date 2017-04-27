#	Copyright (C) 2016 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gi.repository import GObject, Gedit
from plantuml.GeditInterfaceAdapter import GeditInterfaceAdapter


class PlantumlPlugin(GObject.Object, Gedit.WindowActivatable):
	"""	This class loads and unloads the PlantUML plugin for Gedit3 """
	__gtype_name__ = "PlantumlPlugin"
	window = GObject.property(type=Gedit.Window)

	def __init__(self):
		""" Constructs the PlantUML plugin """
		GObject.Object.__init__(self)

		# We use do_activate()/do_deactivate() as
		# constructor/destructor respectively
		self.gedit_interface = None

	def do_activate(self):
		""" Called when the plugin gets loaded """
		self.gedit_interface = GeditInterfaceAdapter(self.window)

	def do_deactivate(self):
		""" Called when the plugin gets unloaded """
		self.gedit_interface.cleanup()
		self.gedit_interface = None

	def do_update_state(self):
		""" Called when the Gedit window/tab/document changes state """
		pass
