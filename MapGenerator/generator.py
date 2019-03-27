# -*- coding: utf-8 -*-
import xml.etree.ElementTree as xml
import uuid

class TRIKMapWrapper():
	''' Instantiates the representation of the TRIK Studio 2D simulator world 
	designed for solving localization problem '''

	CELL_WIDTH = 200
	CELL_HEIGHT = 200
	MAP_SIZE = 8 # cells
	SOLVING_TIME_LIMIT = 360000
	
	LEFT_INFARED_SENSOR_PORT_NUMBER = "1" # Ax
	RIGHT_INFARED_SENSOR_PORT_NUMBER = "2" # Ay
	SONAR_SENSOR_PORT_NUMBER = "1" # Dx
	LEFT_WHEEL_PORT_NUMBER = "1" # Mx
	RIGHT_WHEEL_PORT_NUMBER = "2" # My
	
	def _init_map_structure(self):
		map = xml.Element("root")
		
		xml.SubElement(map, "world")
		xml.SubElement(map, "robots")
		xml.SubElement(map, "constraints")
		
		return map
		
	def _init_world_block(self):
		world = self._map.find("world")
		
		xml.SubElement(world, "background", { "backgroundRect": "0:0:0:0" })
		xml.SubElement(world, "colorFields")
		xml.SubElement(world, "images")
		xml.SubElement(world, "walls")
		xml.SubElement(world, "regions")
		
	def _init_sensors(self, sensors_block):
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
		sensors_conformity = xml.SubElement(constraint_block, "constraint",
			{
				"checkOnce": "true",
				"failMessage": "У робота не должно быть лишних датчиков!"
			})
		conditions = xml.SubElement(sensor_conformity, "conditions", { "glue": "and" })
		
		for port in range(1, 7):
			if (str(port) != self.LEFT_INRARED_SENSOR_PORT_NUMBER) and
					(str(port) != self.RIGHT_INRARED_SENSOR_PORT_NUMBER):
				equal = xml.SubElement(conditions, "equal")
				xml.SubElement(equal, "typeOf", { "objectId": "robot1.A{0}".format(port) }
				xml.SubElement(equal, "string", { "value": "undefined" }

		not_used_port = "2" if self.SONAR_SENSOR_PORT_NUMBER == "1" else "1"			
		equal = xml.SubElement(conditions, "equal")
		xml.SubElement(equal, "typeOf", { "objectId": "robot1.D{0}".format(not_used_port) }
		xml.SubElement(equal, "string", { "value": "undefined" }
			
	def _add_start_position_constraint(self, constraint_block):
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
		success_event = xml.SubElement(constraint_block, "event", { "settedUpInitially": "true" })
		
		success_trigger = xml.SubElement(cheating_event, "trigger")
		xml.SubElement(success_trigger, "success")
		
		success_conditions = xml.SubElement(cheating_event, "conditions", { "glue": "and" })
		xml.SubElement(cheating_conditions, "inside",
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
		
	def _add_solution_check_constaint(self, constraint_block):
		for i in range(self.MAP_SIZE):
			for j in range(self.MAP_SIZE):
				self._add_cheating_constraint(constraint_block, j, i)
				self._add_success_constraint(constraint_block, j, i)
				
	def _init_constraints_block(self):
		constraints = self._map.find("constraints")
		
		xml.SubElement(constraints, "timelimit", { "value": str(self.SOLVING_TIME_LIMIT) })
		
		self._add_sensor_conformity_constraint(constraints)
		self._add_start_position_constraint(constraints)
		self._add_solution_check_constraint(constraints)		
		
	def _init_regions(self):
		regions = self._map.find("world/regions")
		
		for i in range(0, 7):
			for j in range(0, 7):
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
		self._map = self._init_map_structure()
		
		self._init_world_block()
		self._init_robots_block()
		self._init_constraints_block()
		
		self._init_regions()

	def add_wall(self, start_point, end_point):
		walls_block = self._map.find("world/walls")
		
		xml.SubElement(walls_block, "wall",
			{
				"begin": "{0}:{1}".format(start_point[0], start_point[1]),
				"end": "{0}:{1}".format(end_point[0], end_point[1]),
				"id": "{{{0}}}".format(str(uuid.uuid1()))
			}
		
	def set_start_point(self, point, direction):
		coordinate_x = self.CELL_WIDTH * point[0]
		coordinate_y = self.CELL_HEGHT * point[1]
	
		start_point = self._map.find('world/regions[@id="start"]')
		start_point.set("x", str(coordinate_x))
		start_point.set("y", str(coordinate_y))
		
		robot = self._map.find("world/robots/robot")
		robot.set("direction", str(direction))
		# 25 is some kind of magic used in original maps from TRIK devs
		robot.set("position", "{0}:{1}".format(coordinate_x - 25, coordinate_y - 25) 
		
		start_position = robot.find("startPosition")
		start_position.set("direction", str(direction))
		start_position.set("x", str(coordinate_x))
		start_position.set("y", str(coordinate_y))
		
	def save_world(self, savePath):
		xml.ElementTree(self._map).write(savePath, encoding="utf8", xml_declaration=False)
		
map = TRIKMapWrapper()
map.save_world("testMap.xml")
		
		