# -*- coding: utf-8 -*-
from generator_module import *

class Program():
	def _init_help(self):
		parser = argparse.ArgumentParser(description="Generates TRIK Studio fields for the localization problem")
		
		parser.add_argument("path", nargs="?", default=".", metavar="PATH", help="save path")
		parser.add_argument("--single", default=False, action="store_true", help="if set, generates only 1 field (30 by default)")
		
		return parser.parse_args(sys.argv[1:])
		

	def __init__(self):
		self._parsed_arguments = self._init_help()
		
		
	def _is_multiple_start_point_requested(self):
		return not self._parsed_arguments.single
		
		
	def _get_save_folder(self):
		return self._parsed_arguments.path
		
		
	def run(self):
		generator = MapGenerator()
		wrapper = TRIKMapWrapper()
		
		for wall in generator.get_walls():
			wrapper.add_wall(wall[0], wall[1])
			
		if self._is_multiple_start_point_requested():
			field_number = 0
			for point in generator.get_new_start_point():
				wrapper.set_start_point((point[0], point[1]), point[2])
				wrapper.save_world("{0}/field_{1}.xml".format(self._get_save_folder(), field_number))
				field_number += 1
		else:
			point = next(generator.get_new_start_point())
			wrapper.set_start_point((point[0], point[1]), point[2])
			wrapper.save_world("{0}/field.xml".format(self._get_save_folder()))
			
			
generator = Program()
generator.run()
	
	
	
	
	
	
	
	
		
		