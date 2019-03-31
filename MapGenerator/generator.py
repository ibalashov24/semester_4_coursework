# -*- coding: utf-8 -*-
import xml.etree.ElementTree as xml
import uuid
import random
import math
import argparse
import sys
import collections

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
				equal = xml.SubElement(conditions, "equals")
				xml.SubElement(equal, "typeOf", { "objectId": "robot1.A{0}".format(port) })
				xml.SubElement(equal, "string", { "value": "undefined" })

		not_used_port = "2" if self.SONAR_SENSOR_PORT_NUMBER == "1" else "1"			
		equal = xml.SubElement(conditions, "equals")
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
				"begin": "{0}:{1}".format(start_point[0] * self.CELL_HEIGHT, start_point[1] * self.CELL_WIDTH),
				"end": "{0}:{1}".format(end_point[0] * self.CELL_HEIGHT, end_point[1] * self.CELL_WIDTH),
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
		robot.set("position", "{0}:{1}".format( \
			coordinate_x + self.CELL_WIDTH // 2 - 25, coordinate_y + self.CELL_HEIGHT // 2 - 25))
		
		start_position = robot.find("startPosition")
		start_position.set("direction", str(direction))
		start_position.set("x", str(coordinate_x + self.CELL_WIDTH // 2))
		start_position.set("y", str(coordinate_y + self.CELL_HEIGHT // 2))
		
		
	def save_world(self, savePath):
		''' Writes map to the file '''
		
		xml.ElementTree(self._map).write(savePath, encoding="utf8", xml_declaration=False)
		
		
class ConnectivityComponent():
	''' Represents connectivity component in the graph '''
	
	def __init__(self, id):
		self._component_connection_prohibited = False
		self._id = id
		

	def get_component_id(self):
		return self._id
		
		
	def set_component_id(self, new_id):
		self._id = new_id
		
		
	def __hash__(self):
		return self._id
		
		
	def __eq__(self, other):
		return self._id == other._id
		
		
	def is_intercomponent_prohibited(self):
		return self._component_connection_prohibited
		
		
	def prohibit_connection_with_other_components(self):
		self._component_connection_prohibited = True
		
		
class MapRepresentation():
	''' Represents map used by the map generator '''
	
	EMPTY_CELL_COMPONENT_ID = -1
	
	
	def __init__(self, size):
		self.grid = []
		self.components = [ ConnectivityComponent(self.EMPTY_CELL_COMPONENT_ID) ]
		self.walls = set()
		
		for i in range(size + 1):
			self.grid.append([self.EMPTY_CELL_COMPONENT_ID for j in range(size + 1)])		
			
				
class MapGenerator():
	''' Instantiates the generator of the map for the localization problem '''

	MIN_RACK_NUMBER = 7
	MAX_RACK_NUMBER = 10

	MIN_WALLS_NUMBER = 45
	MAX_WALLS_NUMBER = 60
	
	MAP_SIZE = 8 # cells
	START_POINT_NUMBER = 30 # points
	
	CYCLIC_STRUCTURE_PROBABILITY = 0.3
	
	
	def _merge_components(self, board, destination_component_id, source_component_id):
		''' Merges 2 connectivity components '''
		
		for component in board.components:
			if component.get_component_id() == source_component_id:
				component.set_component_id(destination_component_id)
					
		return board
		
		
	def _merge_adjacent_components(self, board, racks):
		''' Uniting components which contains adjacent cells '''
		
		rack_set = set(racks)	
		for i in range(len(racks)):
			rack = racks[i]
			component = board.components[i].get_component_id()
			
			shifts = ((-1, 0), (0, -1), (-1, -1))
			for shift in shifts:
				adjacent_cell = (rack[0] + shift[0], rack[1] + shift[1])
				if adjacent_cell in rack_set:
					adj_cell_component = \
						board.components[racks.index(adjacent_cell)].get_component_id()
					self._merge_components(board, component, adj_cell_component)
		
		return board
		
		
	def _reduce_actual_components_number(self, board, racks, target_component_number):
		''' Reducing actual component number in order to 
			make it equal to chosen component_number '''
			
		actual_component_number = len(racks)
		while actual_component_number > target_component_number:
			first_component_to_unite = random.randint(0, len(racks) - 1)
			second_component_to_unite = random.randint(0, len(racks) - 1)
			
			old_component = board.components[first_component_to_unite].get_component_id()
			new_component = board.components[second_component_to_unite].get_component_id()	
			if old_component != new_component:
				actual_component_number -= 1
				self._merge_components(board, old_component, new_component)
				
		return board
		
		
	def _generate_racks_position(self, board, rack_number):
		''' Selects rack positions on the grid '''
	
		print("Generating {0} racks...".format(rack_number))
		
		rack_set = set()
		# Choosing left-top corner position of the rack
		while (len(rack_set) < rack_number):
			new_rack = (random.randint(0, self.MAP_SIZE - 1), random.randint(0, self.MAP_SIZE - 1))
			rack_set.add(new_rack)

		racks = list(rack_set)
		
		self._prohibited_start_points = rack_set
		
		return racks
		
		
	def _init_components(self, board, component_number):
		''' Initializes connectivity components '''
		
		print("Generating {0} connectivity components...".format(component_number))
		
		board.components = [ConnectivityComponent(i) for i in range(0, component_number)]
		# Component for the border
		board.components.append(ConnectivityComponent(component_number))
		
		return board
		
		
	def _ensure_existance_of_cyclic_structures(self, board, racks):
		''' Prohibiting connection with other components for some 
			connectivity components in order to create cyclic structures '''

		cyclic_structures_number = 0
		# Only components with id == index are independent 
		# due to generation algorithm 
		# "-1" is to prevent triggering for the border
		for i in range(len(board.components) - 1):
			if board.components[i].get_component_id() == i and \
					random.random() < self.CYCLIC_STRUCTURE_PROBABILITY:
					
				board.components[i].prohibit_connection_with_other_components()
				cyclic_structures_number += 1
				
		print("Generated {0} cyclic structures".format(cyclic_structures_number))
		
				
	def _generate_border(self, board, board_id):
		''' Generates border walls '''
	
		# Placing border
		for i in range(self.MAP_SIZE + 1):
			board.grid[0][i] = board_id
			board.grid[i][0] = board_id
			board.grid[self.MAP_SIZE][i] = board_id
			board.grid[i][self.MAP_SIZE] = board_id
			
		for i in range(self.MAP_SIZE):
			board.walls.add(((0, i), (0, i + 1)))
			board.walls.add(((i, 0), (i + 1, 0)))
			board.walls.add(((i, self.MAP_SIZE), (i + 1, self.MAP_SIZE)))
			board.walls.add(((self.MAP_SIZE, i), (self.MAP_SIZE, i + 1)))
			
		return board
		
		
	def _fill_grid_with_components(self, board, racks):
		''' Places connectivity components on the grid '''
		
		rack_number = len(racks)
		for i in range(rack_number):
			rack_component = board.components[i].get_component_id()
			rack = racks[i]
			
			# print("Placing rack {0}:{1} to component {2}".format(rack[1], rack[0], rack_component))
			
			shifts = ((0, 0), (1, 0), (0, 1), (1, 1))
			node_shifts = \
			(
				((0, 1), (1, 1)),
				((1, 0), (1, 1)),
				((0, 0), (0, 1)),
				((0, 0), (1, 0))
			)
			
			for i in range(len(shifts)):
				board.grid[rack[0] + shifts[i][0]][rack[1] + shifts[i][1]] = rack_component
				board.walls.add(( \
						(rack[0] + node_shifts[i][0][0], rack[1] + node_shifts[i][0][1]), \
						(rack[0] + node_shifts[i][1][0], rack[1] + node_shifts[i][1][1]) \
					))
		
		self._generate_border(board, rack_number)
			
		return board
		
					
	def _arrange_racks(self, board, rack_number, component_number):
		''' Arranges racks on the grid '''
	
		racks = self._generate_racks_position(board, rack_number)
		
		# Generating component for each cell at the beginning
		board = self._init_components(board, rack_number)
		
		self._merge_adjacent_components(board, racks)
		
		self._reduce_actual_components_number(board, racks, component_number)
		
		self._ensure_existance_of_cyclic_structures(board, racks)
		
		self._fill_grid_with_components(board, racks)
								
		return racks
		
		
	def _get_cells_by_components(self, board, rack_number):
		''' Generates the dictionary of cells for each 
			connectivity component (except empty cells and the border) '''
			
		components = collections.defaultdict(list)
		for i in range(1, self.MAP_SIZE):
			for j in range(1, self.MAP_SIZE):
				if board.grid[i][j] != rack_number and \
						board.grid[i][j] != MapRepresentation.EMPTY_CELL_COMPONENT_ID:
						
					components[board.grid[i][j]].append((i, j))
		
		return components
		
		
	def _count_free_points(self, board, used, start_y, start_x, new_wall):
		''' Counts the number of points which are reachable from given start point '''
		
		used[start_y][start_x] = True
		result = 1
		
		shifts = ((0, 1), (1, 0), (-1, 0), (0, -1))
		# Corresponding wall shifts
		node_shifts = \
			(
				((0, 1), (1, 1)),
				((1, 0), (1, 1)),
				((0, 0), (0, 1)),
				((0, 0), (1, 0))
			)
			
		for i in range(len(shifts)):
			coord_y = start_y + shifts[i][0]
			coord_x = start_x + shifts[i][1]
			
			wall = ( \
					(start_y + node_shifts[i][0][0], start_x + node_shifts[i][0][1]), \
					(start_y + node_shifts[i][1][0], start_x + node_shifts[i][1][1]) \
				   )
			reversed_wall = (wall[1], wall[0])
			
			if not wall in board.walls and \
					not reversed_wall in board.walls and \
					wall != new_wall and \
					reversed_wall != new_wall and \
					not used[coord_y][coord_x]:
				result += self._count_free_points(board, used, coord_y, coord_x, new_wall)
		
		return result
		
		
	def _are_closed_structures_exists(self, board, new_wall):
		''' Checks if there any closed wall structures on the board '''
	
		used = []
		start_point = (0, 0) # Cell coordinates
		for i in range(self.MAP_SIZE):
			used.append([])
			for j in range(self.MAP_SIZE):
				if not (i, j) in self._prohibited_start_points:
					start_point = (i, j)
					
				used[i].append(False)
				
		expected_free_points = \
			self.MAP_SIZE * self.MAP_SIZE - len(self._prohibited_start_points)
		free_points = self._count_free_points(
				board, 
				used, 
				start_point[0], 
				start_point[1], 
				new_wall)
		
		return expected_free_points != free_points
		
				
	def _generate_walls(self, board, wall_number, rack_number):
		''' Generates walls for the map with already
			generated racks and connectivity components '''
	
		print("Generating {0} walls...".format(wall_number))
	
		components = self._get_cells_by_components(board, rack_number)		
	
		# Generating new walls
		for i in range(wall_number):
			is_wall_built = False
			while not is_wall_built:		
				connectivity_component_cells = random.choice(list(components.values()))
				cell = random.choice(connectivity_component_cells)				
				candidates = \
					[
						(cell[0] + 1, cell[1]), 
						(cell[0] - 1, cell[1]), 
						(cell[0], cell[1] + 1), 
						(cell[0], cell[1] - 1)
					]
				cell_id = board.grid[cell[0]][cell[1]]
				
				new_cell = random.choice(candidates)
				
				new_cell_id = board.grid[new_cell[0]][new_cell[1]]
				new_wall = (cell, new_cell)
			
				if new_cell_id == MapRepresentation.EMPTY_CELL_COMPONENT_ID or \
						not board.components[new_cell_id].is_intercomponent_prohibited() and \
						not board.components[cell_id].is_intercomponent_prohibited() and \
						not self._are_closed_structures_exists(board, new_wall):
						
					if new_cell_id == MapRepresentation.EMPTY_CELL_COMPONENT_ID:
						board.grid[new_cell[0]][new_cell[1]] = board.grid[cell[0]][cell[1]]
						new_cell_id = board.grid[new_cell[0]][new_cell[1]]
						components[new_cell_id].append(new_cell)
						connectivity_component_cells.append(new_cell)

					board.walls.add(new_wall)
					is_wall_built = True
			
		self._walls = list(board.walls)
		

	def _choose_start_points(self, restricted_cells):
		''' Generates start points for the robot on the generated map '''
	
		print("Choosing start {0} points...".format(self.START_POINT_NUMBER))
	
		start_points = set()
		start_points_generated = 0
		while (start_points_generated < self.START_POINT_NUMBER):
			cell_x = random.randint(0, self.MAP_SIZE - 1)
			cell_y = random.randint(0, self.MAP_SIZE - 1)
			direction = random.choice((0, 90, -90, 180))
			
			if not (cell_x, cell_y) in restricted_cells:
				start_points.add((cell_x, cell_y, direction))
				start_points_generated += 1
				
		self._start_points = list(start_points)
		
				
	def _init_grid(self):
		''' Initializes empty grid describing corners '''
	
		return MapRepresentation(self.MAP_SIZE)
		
	
	def _generate_map(self, rack_number, component_number, wall_number):
		''' Generates the new map '''
	
		board = self._init_grid()
		
		racks = self._arrange_racks(board, rack_number, component_number)
		self._generate_walls(board, wall_number, rack_number)
		
		self._choose_start_points(set(racks))	
		

	def __init__(self):
		''' Initializes the map generator and generates map '''
	
		self._walls = []
		self._start_points = []
		self._prohibited_start_points = set()
		
		rack_number = random.randint(self.MIN_RACK_NUMBER, self.MAX_RACK_NUMBER)
		connectivity_component_number = random.randint(self.MIN_RACK_NUMBER, rack_number)
		wall_number = random.randint(self.MIN_WALLS_NUMBER, self.MAX_WALLS_NUMBER)
		
		self._generate_map(rack_number, connectivity_component_number, wall_number)
		

	def get_walls(self):
		''' Yields all walls on the generated map '''
		
		for wall in self._walls:
			yield wall		
			

	def get_new_start_point(self):
		''' Yields all start points on the generated map '''
	
		for point in self._start_points:
			yield point
			

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
	
	
	
	
	
	
	
	
		
		