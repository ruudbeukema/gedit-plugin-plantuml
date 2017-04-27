#	Copyright (C) 2016 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
from plantuml.GtkPlantumlWindow import GtkPlantumlWindow
from plantuml.GtkPlantumlWidget import GtkPlantumlWidget


class PlantumlViewer(object):
	def __init__(self):
		self.window = GtkPlantumlWindow()
		self.widget = GtkPlantumlWidget()
		self.window.add(self.widget)

	def cleanup(self):
		self.window.destroy()
		self.widget.destroy()
		self.window = self.widget = None

	def add_file(self, source_filepath):
		_, filename = os.path.split(source_filepath)
		self.widget.add_diagram(source_filepath, filename)
		self.window.show_all()

	def remove_file(self, source_filepath):
		self.widget.remove_diagram(source_filepath)

	def set_active(self, source_filepath):
		self.widget.set_active_diagram(source_filepath)

	# TODO: implement this
	def reorder_tabs(self, source_filepaths_ordered):
		pass

	def show_in_progress(self, source_filepath):
		self.widget.set_uml_generation_in_progress(source_filepath)

	def update_uml(self, source_filepath, output_filepath):
		self.widget.update_diagram(source_filepath, output_filepath)
