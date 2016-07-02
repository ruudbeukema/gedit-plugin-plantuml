#	Copyright (C) 2014 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from os.path import expanduser
import os
import subprocess
import shutil
import tempfile


DOT_PATH = "/plantuml/bin/plantuml.8022.jar"

class Model():
	m_output_folder = ""
	m_dot_cmd = ""

	def __init__(self):
		self.m_output_folder = tempfile.gettempdir()
		
		
	def plantuml_check_if_present(self):
		try:
			scriptdir = os.path.dirname(__file__)
			dot_path_abs = os.path.dirname(scriptdir) + DOT_PATH

			if self.file_exists(dot_path_abs):
				self.m_dot_cmd = dot_path_abs
				return True
			else:
				return False
		except:
			return False
		
		
	def plantuml_run(self, in_uml_filepath, in_img_filepath):
		try:
			args = [self.m_dot_cmd, "-quiet", "-output", self.m_output_folder, in_uml_filepath]
			subprocess.check_call(["java", "-jar"] + list(args))

			return self.file_exists(in_img_filepath)
		except:
			return False
			
	
	def get_output_filepath(self, in_path):
		file_name, file_extension = os.path.splitext(in_path)
		base_file_name = os.path.basename(file_name)
		output_file = self.m_output_folder + "/" + base_file_name + '.png'
		return output_file
		
	
	def file_has_extension(self, in_file):
		file_name, file_extension = os.path.splitext(in_file)
		if file_extension != "":
			return True
		else:			
			return False
			
		
	def file_exists(self, in_file):
		return os.path.isfile(in_file)
