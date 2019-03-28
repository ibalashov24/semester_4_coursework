# -*- coding: utf-8 -*-
import xml.etree.ElementTree as xml
import uuid
import random
import math
import argparse
import sys

class TRIKMapWrapper():
	''' Instantiates the representation of the TRIK Studio 2D simulator world 
	designed for solving localization problem '''

	CELL_WIDTH = 200
	CELL_HEIGHT = 200
	MAP_SIZE = 8 # cells
	SOLVING_TIME_LIMIT = 360000 # ms
	
	LEFT_INFARED_SENSOR_PORT_NUMBER = "1" # Ax
	RIGHT_INFARED_SENSOR_PORT_NUMBER = "2" # Ay
	SONAR_SENSOR_PORT_NUMBER = "1" # Dx
	LEFT_WHEEL_PORT_NUMBER = "1" # Mx
	RIGHT_WHEEL_PORT_NUMBER = "2" # My
	
	def _init_map_structure(self):
		''' Initializes empty map file '''
		
		map = xml.Element("root")
		
		xml.SubElement(map, "world")
		xml.SubElement(map, "robots")
		xml.SubElement(map, "constraints")
		
		return map
		
	def _init_world_block(self):
		''' Initializes block /root/world in map xml structure '''
		
		world = self._map.find("world")
		
		xml.SubElement(world, "background", { "backgroundRect": "0:0:0:0" })
		xml.SubElement(world, "colorFields")
		xml.SubElement(world, "images")
		xml.SubElement(world, "walls")
		xml.SubElement(world, "regions")
		
	def _init_sensors(self, sensors_block):
		''' Initializes /root/robots/robot/sensors xml block '''
	
		sensors = [	
					("-90", "A{0}".format(self.LEFT_INFARED_SENSOR_PORT_NUMBER), "TrikInfraredSensor"),
					("90", "A{0}".format(self.RIGHT_INFARED_SENSOR_PORT_NUMBER), "TrikInfraredSensor"),
					("0", "D{0}".format(self.SONAR_SENSOR_PORT_NUMBER), "TrikSonarSensor")]
	
		for direction, port, sensorType in sensors:
			xml.SubElement(sensors_block, "sensor",
					{
						"direction": direction,
						"type": "trik::robotModel::parts::{0}".format(sensorType),
						"position": "25:25",
						"port": "{0}###input######sensor{0}".format(port)
					})
		
	def _init_robots_block(self):
		''' Initializes /root/robots xml block '''
		
		robots = self._map.find("robots")
		robot = xml.SubElement(robots, "robot")
		
		# Initial position is (0, 0) on the grid
		robot.set("position", "{0}:{1}".format(self.CELL_WIDTH // 2 - 25, self.CELL_HEIGHT // 2 - 25))
		robot.set("direction", "0")
		robot.set("id", "trikRobot")
		
		xml.SubElement(
			robot, 
			"wheels", 
			{ 	
				"left": "M{0}###output###лю{0}###".format(self.LEFT_WHEEL_PORT_NUMBER),
				"right": "M{0}###output###лю{0}###".format(self.RIGHT_WHEEL_PORT_NUMBER) 
			})
		
		xml.SubElement(robot, "startPosition", 
						{ 
							"direction": "0", 
							"y": "{0}".format(self.CELL_HEIGHT // 2),
							"x": "{0}".format(self.CELL_WIDTH // 2),
							"id": "{{{0}}}".format(uuid.uuid1())
						})
						
		sensors = xml.SubElement(robot, "sensors")
		self._init_sensors(sensors)
		
	def _add_sensor_conformity_constraint(self, constraint_block):
		''' Initializes constraint which checks that 
			there is no excess sensors on the robot '''
			
		sensor_conformity = xml.SubElement(constraint_block, "constraint",
			{
				"checkOnce": "true",
				"failMessage": "У робота не должно быть лишних датчиков!"
			})
		conditions = xml.SubElement(sensor_conformity, "conditions", { "glue": "and" })
		
		for port in range(1, 7):
			if (str(port) != self.LEFT_INFARED_SENSOR_PORT_NUMBER) and \
					(str(port) != self.RIGHT_INFARED_SENSOR_PORT_NUMBER):
				equal = xml.SubElement(conditions, "equal")
				xml.SubElement(equal, "typeOf", { "objectId": "robot1.A{0}".format(port) })
				xml.SubElement(equal, "string", { "value": "undefined" })

		not_used_port = "2" if self.SONAR_SENSOR_PORT_NUMBER == "1" else "1"			
		equal = xml.SubElement(conditions, "equal")
		xml.SubElement(equal, "typeOf", { "objectId": "robot1.D{0}".format(not_used_port) })
		xml.SubElement(equal, "string", { "value": "undefined" })
			
	def _add_start_position_constraint(self, constraint_block):
		''' Initializes constraint which checks that
			the robot is in the start position at the beginning '''
			
		start_position_constraint = xml.SubElement(constraint_block, "constraint",
			{
				"checkOnce": "true",
				"failMessage": "Робот должен находиться в зоне старта перед запуском!"
			})
		xml.SubElement(start_position_constraint, "inside",
			{
				"objectId": "robot1",
				"regionId": "start"
			})
			
	def _add_cheating_constraint(self, constraint_block, x, y):
		''' Add constraint which checks that 
			the robot does not display the position in which it is not itself '''
			
		cheating_event = xml.SubElement(constraint_block, "event", { "settedUpInitially": "true" })
		
		cheating_trigger = xml.SubElement(cheating_event, "trigger")
		xml.SubElement(cheating_trigger, "fail", { "message" : "Обнаружено читерство!" })
		
		cheating_conditions = xml.SubElement(cheating_event, "conditions", { "glue": "and" })
		xml.SubElement(cheating_conditions, "inside",
			{
				"objectId": "robot1",
				"regionId": "({0},{1})".format(x, y)
			})
			
		greater_condition = xml.SubElement(cheating_conditions, "greater")
		xml.SubElement(greater_condition, "objectState", { "object": "robot1.display.labels.size" })
		xml.SubElement(greater_condition, "int", { "value": "0" })
		
		not_condition = xml.SubElement(cheating_conditions, "not")
		equals_condition = xml.SubElement(not_condition, "equals")
		xml.SubElement(equals_condition, "objectState", { "object": "robot1.display.labels.first.text" })
		xml.SubElement(equals_condition, "string", { "value": "({0},{1})".format(x, y) })
		
	def _add_success_constraint(self, constraint_block, x, y):
		''' Add constraint which checks that 
			robot displayed correct coordinates '''
			
		success_event = xml.SubElement(constraint_block, "event", { "settedUpInitially": "true" })
		
		success_trigger = xml.SubElement(success_event, "trigger")
		xml.SubElement(success_trigger, "success")
		
		success_conditions = xml.SubElement(success_event, "conditions", { "glue": "and" })
		xml.SubElement(success_conditions, "inside",
			{
				"objectId": "robot1",
				"regionId": "({0},{1})".format(x, y)
			})
			
		greater_condition = xml.SubElement(success_conditions, "greater")
		xml.SubElement(greater_condition, "objectState", { "object": "robot1.display.labels.size" })
		xml.SubElement(greater_condition, "int", { "value": "0" })
		
		equals_condition = xml.SubElement(success_conditions, "equals")
		xml.SubElement(equals_condition, "objectState", { "object": "robot1.display.labels.first.text" })
		xml.SubElement(equals_condition, "string", { "value": "({0},{1})".format(x, y) })
		
	def _add_solution_check_constraint(self, constraint_block):
		''' Generates constraints for the constraints xml block '''
		
		for i in range(self.MAP_SIZE):
			for j in range(self.MAP_SIZE):
				self._add_cheating_constraint(constraint_block, j, i)
				self._add_success_constraint(constraint_block, j, i)
				
	def _init_constraints_block(self):
		''' Initializes /root/constraints xml block '''
		
		constraints = self._map.find("constraints")
		
		xml.SubElement(constraints, "timelimit", { "value": str(self.SOLVING_TIME_LIMIT) })
		
		self._add_sensor_conformity_constraint(constraints)
		self._add_start_position_constraint(constraints)
		self._add_solution_check_constraint(constraints)		
		
	def _init_regions(self):
		''' Initializes /root/world/regions xml block '''
		
		regions = self._map.find("world/regions")
		
		for i in range(8):
			for j in range(8):
				xml.SubElement(regions, "region",
					{ 
						"type": "rectangle",
						"x": str(j * self.CELL_WIDTH),
						"y": str(i * self.CELL_HEIGHT),
						"id": "({0},{1})".format(j, i),
						"text": "({0},{1})".format(j, i),
						"visible": "false",
						"width" : str(self.CELL_WIDTH),
						"height": str(self.CELL_HEIGHT)
					})
					
		# Temporary start point
		xml.SubElement(regions, "region",
			{
				"type": "rectangle", 
				"x": "0", 
				"y": "0", 
				"id": "start",
				"text": "start", 
				"visible": "true", 
				"width" : str(self.CELL_WIDTH),
				"height": str(self.CELL_HEIGHT), 
				"filled": "true", 
				"color": "#0000ff"
			})
		
	def __init__(self): 
		''' Initializes the new instance of TRIKMapWrapper '''
		
		self._map = self._init_map_structure()
		
		self._init_world_block()
		self._init_robots_block()
		self._init_constraints_block()
		
		self._init_regions()

	def add_wall(self, start_point, end_point):
		''' Adds new wall with start_point=(x1, y1) and
			end_point=(x2, y2) on the grid to the map '''
			
		walls_block = self._map.find("world/walls")
		xml.SubElement(walls_block, "wall",
			{
				"begin": "{0}:{1}".format(start_point[0], start_point[1]),
				"end": "{0}:{1}".format(end_point[0], end_point[1]),
				"id": "{{{0}}}".format(str(uuid.uuid1()))
			})
		
	def set_start_point(self, point, direction):
		''' Sets new start point for the robot
			with given grid coordinate point=(x, y) and given direction '''
	
		coordinate_x = self.CELL_WIDTH * point[0]
		coordinate_y = self.CELL_HEIGHT * point[1]
	
		start_point = self._map.find("world/regions/region[@id='start']")
		start_point.set("x", str(coordinate_x))
		start_point.set("y", str(coordinate_y))
		
		robot = self._map.find("robots/robot")
		robot.set("direction", str(direction))
		# 25 is some kind of magic used in original maps from TRIK devs
		robot.set("position", "{0}:{1}".format(coordinate_x - 25, coordinate_y - 25))
		
		start_position = robot.find("startPosition")
		start_position.set("direction", str(direction))
		start_position.set("x", str(coordinate_x))
		start_position.set("y", str(coordinate_y))
		
	def save_world(self, savePath):
		''' Writes map to the file '''
		
		xml.ElementTree(self._map).write(savePath, encoding="utf8", xml_declaration=False)
		
class ConnectivityComponent():
	''' Represents connectivity component in the graph '''
	
	def __init__(self, id):
		self._border_connection_prohibited = False
		self.set_component_id(id)

	def get_component_id(self):
		return self._id
		
	def set_component_id(self, id):
		self._id = id
	
	def is_border_connection_prohibited(self):
		return self._is_border_connection_prohibited
		
	def prohibit_border_connection(self):
		self._is_border_connection_prohibited = True
				
class MapGenerator():
	MIN_RACK_NUMBER = 7
	MAX_RACK_NUMBER = 15

	MIN_WALLS_NUMBER = 30
	MAX_WALLS_NUMBER = 45
	
	MAP_SIZE = 8 # cells
	START_POINT_NUMBER = 30
	
	def _arrange_racks(self, grid, rack_number, component_number):
		rack_set = set()
		# Choosing rack left-top angle position
		while (len(rack_set) < rack_number):
			new_rack = (random.randint(0, self.MAP_SIZE - 1), random.randint(0, self.MAP_SIZE - 1))
			rack_set.add(new_rack)
			
		racks = list(rack_set)
		self._prohibited_start_points = set(racks)
		
		connectivity_components = [ConnectivityComponent(i) for i in range(1, rack_number + 1)]
		# Reducing actual component number in order to make it equal to chosen component_number
		actual_component_number = rack_number
		while actual_component_number != component_number:
			first_component_to_unite = random.randint(0, rack_number - 1)
			second_component_to_unite = random.randint(0, rack_number - 1)
			
			if connectivity_components[first_component_to_unite].get_component_id() != \
				connectivity_components[second_component_to_unite].get_component_id():
				
				--actual_component_number
				connectivity_components[first_component_to_unite] = connectivity_components[second_component_to_unite]
				
		# Filling grid
		for i in range(rack_number):
			rack_component = connectivity_components[i]
			rack = racks[i]
			
			grid[rack[1]][rack[0]] = rack_component
			grid[rack[1] + 1][rack[0]] = rack_component
			grid[rack[1]][rack[0] + 1] = rack_component
			grid[rack[1] + 1][rack[0] + 1] = rack_component			
			
			# In order not to create closed area
			if rack[0] == self.MAP_SIZE - 1 or rack[0] == 0 or rack[1] == self.MAP_SIZE - 1 or rack[1] == 0:
				rack_component.prohibit_border_connection()	
				
		# Prohibiting wall connection for some connectivity components
		# in order to create cyclic structures
		for component in set(connectivity_components):
			if not component.is_border_connection_prohibited() and random.random() == 1:
				component.prohibit_border_connection()
				
		
	def _generate_walls(self, grid, wall_number):
		components = defaultdict(list)
		for i in range(self.MAP_SIZE):
			for j in range(self.MAP_SIZE):
				component_id = grid[i][j].get_component_id()
				if component_id != 0:
					components[component_id].append((i, j))
					
		# Generating walls
		walls = set()
		for i in range(wall_number):
			is_wall_built = False
			while not is_wall_built:		
				connectivity_component_cells = random.choise(components.values())
				cell = random.choise(connectivity_component_cells)
				
				if cell[1] != self.MAP_SIZE and cell[1] != 0 and cell[0] != self.MAP_SIZE and cell[0] != 0:
					candidates = \
						[
							(cell[0] + 1, cell[1]), 
							(cell[0] - 1, cell[1]), 
							(cell[0], cell[1] + 1), 
							(cell[0], cell[1] - 1)
						]
					new_cell = random.choise(candidates)
					
					if (grid[new_cell[1]][new_cell[0]].get_component_id() == 0) and \
							not ((cell[1] in (self.MAP_SIZE, 0) or cell[0] in (self.MAP_SIZE, 0)) and \
							grid[cell[1]][cell[0]].is_border_connection_prohibited()):
							
						grid[new_cell[1]][new_cell[0]] = grid[new_cell[1]][new_cell[0]]
						connectivity_component_cells.append(new_cell)
						
						walls.add((cell, new_cell))
						
						# In order to prevent closed areas creation
						if cell[1] in (self.MAP_SIZE, 0) or cell[0] in (self.MAP_SIZE, 0):
							grid[new_cell[1]][new_cell[0]].prohibit_border_connection()
							
						is_wall_built = True
				
		# Adding borders
		for i in range(self.MAP_SIZE):
			walls.add( ((i, 0), (i + 1, 0)) )
			walls.add( ((i, self.MAP_SIZE), (i + 1, self.MAP_SIZE)) )
			walls.add( ((0, i), (0, i + 1)) )
			walls.add( ((self.MAP_SIZE, i), (self.MAP_SIZE, i + 1)) )
			
		self._walls = list(walls)

	def _choose_start_points(self, grid):
		start_points = set()
		for i in range(self.START_POINT_NUMBER):
			cell_x = random.randint(self.MAP_SIZE)
			cell_y = random.randint(self.MAP_SIZE)
			direction = random.choise((0, 90, -90, 180))
			
			if not cell in self._prohibited_start_points:
				start_points.add((cell_x, cell_y, direction))
				
		self._start_points = list(start_points)
				
	def _init_grid(self):
		grid = []
		for i in range(self.MAP_SIZE):
			for j in range(self.MAP_SIZE):
				grid.append(ConnectivityComponent(0))
				
		return grid
	
	def _generate_map(self, rack_number, component_number, wall_number):
		grid = self._init_grid()
		
		self._arrange_racks(grid, rack_number, component_number)
		self._generate_walls(grid, wall_number)
		
		self._choose_start_points(grid)	

	def __init__(self):
		self._walls = []
		self._start_points = []
		self._prohibited_start_points = set()
		
		rack_number = random.randint(self.MIN_RACK_NUMBER, self.MAX_RACK_NUMBER)
		connectivity_component_number = random.randint(self.MIN_RACK_NUMBER, rack_number)
		wall_number = random.randint(self.MIN_WALLS_NUMBER, self.MAX_WALLS_NUMBER)
		
		self._generate_map(rack_number, connectivity_component_number, wall_number)

	def get_walls(self):
		for wall in self._walls:
			yield wall		

	def get_new_start_point(self):
		for point in self._start_points:
			yield point

'''map = TRIKMapWrapper()
map.set_start_point((1, 2), 90)
map.save_world("testMap.xml")'''

class Program():
	def _init_help(self):
		parser = argparse.ArgumentParser(description="Generates TRIK Studio fields for the localization problem")
		parser.add_argument("--single", action="store_true", help="if set, generates only 1 field (30 by default)")
		
		# argv[1] is the path
		return parser.parse_args(' '.join(sys.argv[2:]))

	def __init__(self):
		self._parsed_arguments = self._init_help()
		
	def _is_multiple_start_point_requested():
		return not self._parsed_arguments.single
		
	def _get_save_folder(self):
		return sys.argv[1]
		
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
				++field_number
		else:
			wrapper.set_start_point((point[0], point[1]), point[2])
			wrapper.save_world("{0}/field.xml".format(self._get_save_folder()))
			
generator = Program()
generator.run()
	
	
	
	
	
	
	
	
		
		