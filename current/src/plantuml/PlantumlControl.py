#	Copyright (C) 2016 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from multiprocessing import Queue

from plantuml.PlantumlDriver import PlantumlDriver
from plantuml.PlantumlViewer import PlantumlViewer


class PlantumlControl(object):
	"""
	This class is responsible for tying together the PlantumlViewer and the PlantumlDriver.
	"""

	def __init__(self, docking_locations={'side-panel': None, 'bottom-panel': None }):
		"""
		Creates a PlantumlControl instance

		:param docking_locations: a dict containing Gedit's available docking locations
		"""
		self.docking_locations = docking_locations
		self.viewer = PlantumlViewer()

		self.generated_uml_queue = Queue()
		self.driver = PlantumlDriver(self.generated_uml_queue)

		self.sources = []

	def cleanup(self):
		""" Destroys all class instance variables. """
		self.driver.cleanup()
		self.viewer.cleanup()

		self.driver = self.viewer = None

	def process_generated_uml(self):
		""" Polls the generated UML queue and updates the PlantumlViewer until the queue is empty. """
		while not self.generated_uml_queue.empty():
			source_filepath, output_filepath = self.generated_uml_queue.get_nowait()
			self.viewer.update_uml(source_filepath, output_filepath)

	def get_is_present(self, source_filepath):
		return source_filepath in self.sources

	def add_file(self, source_filepath):
		"""
		Adds the given file to PlantumlViewer and triggers the generation of the UML diagram by the PlantumlDriver.

		:param source_filepath: path to the PlantUML source file
		"""
		if source_filepath not in self.sources:
			self.sources.append(source_filepath)

			self.viewer.add_file(source_filepath)
			self.viewer.show_in_progress(source_filepath)
			self.driver.generate_uml(source_filepath)

	def remove_file(self, source_filepath):
		"""
		Removes the given file from the PlantumlViewer.

		:param source_filepath: path to the PlantUML source file
		"""
		if source_filepath in self.sources:
			self.sources.remove(source_filepath)
			self.viewer.remove_file(source_filepath)

	def set_active_file(self, source_filepath):
		"""
		Activates the given file in the PlantumlViewer.

		:param source_filepath: path to the PlantUML source file
		"""
		if source_filepath in self.sources:
			self.viewer.set_active(source_filepath)

	def file_saved(self, source_filepath):
		"""
		Triggers the (re-)generation of the UML diagram by the PlantumlDriver and notifies to the PlantumlViewer that
		UML generation is in progress.

		:param source_filepath: path to the PlantUML source file
		"""
		if source_filepath in self.sources:
			self.viewer.show_in_progress(source_filepath)
			self.driver.generate_uml(source_filepath)

	def reorder_tabs(self, source_filepaths_ordered):
		"""
		Instructs the PlantumlViewer to reorder its tabs.

		:param source_filepaths_ordered: ordered list of paths to PlantUML source files.
		"""
		if set(source_filepaths_ordered) == set(self.sources):
			self.viewer.reorder_tabs(source_filepaths_ordered)
