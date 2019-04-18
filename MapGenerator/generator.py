# -*- coding: utf-8 -*-
from generator_module import *

class Program():
	def _init_help(self):
		parser = argparse.ArgumentParser(description="Generates TRIK Studio fields for the localization problem")
		
		parser.add_argument("path", nargs="?", default=".", metavar="PATH", help="save path")
		parser.add_argument("--single", default=False, action="store_true", help="if set, generates only 1 field (30 by default)")
		
		return parser.parse_args(sys.argv[1:])
		

	def __init__(self):
		'''
		Initializes new instance of Program()
		'''
		
		self._parsed_arguments = self._init_help()
		
		
	def _is_multiple_start_point_requested(self):
		'''
		Returns True if multiple point generation was required in the argument line
		'''
		
		return not self._parsed_arguments.single
		
		
	def _get_save_folder(self):
		'''
		Returns path to the result field folder
		'''
		
		return self._parsed_arguments.path
		
		
	def run(self):
		'''
		Launches generator
		'''
		
		generator = MapGenerator()
		wrapper = TRIKMapWrapper()
		
		for wall in generator.get_walls():
			wrapper.add_wall(*wall)
			
		if self._is_multiple_start_point_requested():
			field_number = 0
			for directed_point in generator.get_new_start_point():
				wrapper.set_start_point(*directed_point)
				wrapper.save_world("{0}/field_{1}.xml".format(self._get_save_folder(), field_number))
				field_number += 1
		else:
			point = next(generator.get_new_start_point())
			wrapper.set_start_point(*directed_point)
			wrapper.save_world("{0}/field.xml".format(self._get_save_folder()))
			
			
generator = Program()
generator.run()
	
	
	
	
	
	
	
	
		
		