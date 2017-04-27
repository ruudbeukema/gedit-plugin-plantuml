#	Copyright (C) 2016 Ruud Beukema. All rights reserved
#
#	This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
#	distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import time
import subprocess
from multiprocessing import Process, Queue

PLANTUML_JAR_FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin/plantuml.jar")


class PlantumlDriver(object):
	"""
	Runs the PlantUML Java application for every source file in the in-queue asynchronous from its caller.
	"""

	def __init__(self, generated_uml_queue=None):
		"""
		Creates a PlantumlDriver instance
		
		:param generated_uml_queue: an output queue for generated UML (of type multiprocessing.Queue)
		"""
		if generated_uml_queue is None:
			raise TypeError("Argument 'generated_uml_queue' is not of type multiprocessing.Queue")

		self.function_queue = Queue()

		self.worker = PlantumlDriverWorker(self.function_queue, generated_uml_queue)
		self.worker_process = Process(name="PlantUML Driver", target=self.worker.run)
		self.worker_process.start()

	def cleanup(self):
		""" Destroys all class instance variables """
		self.worker_process.terminate()
		self.worker_process.join()
		self.worker_process = None
		self.function_queue.close()

	def generate_uml(self, source_filepath):
		"""
		Generates UML for the given source file
		
		:param source_filepath: path to the PlantUML source file
		"""
		self.__serialize_and_send_function('generate_uml', source_filepath)

	def __serialize_and_send_function(self, function_name, *function_args):
		"""
		Helper function to serialize the requested function and its arguments
		
		:param function_name: name of the requested function
		:param function_args: any arguments to pass to the requested function
		"""
		serialized_func = {
			'function_name': function_name,
			'function_args': function_args
		}

		self.function_queue.put(serialized_func)


class PlantumlDriverWorker(object):
	"""
	This class is the worker class for PlantumlDriver and is intended to be used to asynchronously run PlantUML 
	commands. 
	"""

	def __init__(self, plantuml_function_queue, plantuml_output_queue):
		"""
		Create a PlantumlDriverWorker class instance.
		
		:param plantuml_function_queue: queue for incoming PlantUML function requests 
		:param plantuml_output_queue: queue for outgoing PlantUML function answers
		"""
		self.function_queue = plantuml_function_queue
		self.output_queue = plantuml_output_queue
		
	def run(self):
		""" Represents the Process' run function and runs in an infinite loop. """
		while True:
			serialized_func = self.function_queue.get()

			function_name = serialized_func.get('function_name', None)
			function_args = serialized_func.get('function_args', None)

			if function_name == 'generate_uml':
				source_filepath = function_args[0]
				self.__generate_uml(source_filepath)
			else:
				raise ValueError("Illegal/unsupported command received")

			time.sleep(0.1)

	def __generate_uml(self, source_filepath):
		"""
		Instructs PlantUML to generate UML for the given source file. Its results will be put in the output queue.
		
		:param source_filepath: path to the PlantUML source file
		"""
		subprocess.check_output(["java", "-jar", PLANTUML_JAR_FILEPATH, "-tpng", "-quiet", "-nbthread auto",
		                         source_filepath])
		output_filepath = os.path.splitext(source_filepath)[0] + ".png"

		self.output_queue.put((source_filepath, output_filepath))
