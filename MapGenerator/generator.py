# -*- coding: utf-8 -*-
import xml.etree.ElementTree as xml
import uuid

class TRIKMapWrapper():
	''' Instantiates the representation of the TRIK Studio 2D simulator world 
	designed for solving localization problem '''

	CELL_WIDTH = 200
	CELL_HEIGHT = 200
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
		
	def _init_constraints_block(self):
		constraints = self._map.find("constraints")
		
		xml.SubElement(constraints, "timelimit", { "value": str(self.SOLVING_TIME_LIMIT) })
		
	def _init_regions(self):
		
		
	def __init__(self): 
		self._map = self._init_map_structure()
		
		self._init_world_block()
		self._init_robots_block()
		self._init_constraints_block()
		
		self._init_regions()

	def add_wall(self, start_point, end_point):
		pass
		
	def set_start_point(self, point):
		pass
		
	def set_expected_end_point(self, point):
		pass
		
	def save_world(self, savePath):
		xml.ElementTree(self._map).write(savePath, encoding="utf8", xml_declaration=False)
		
map = TRIKMapWrapper()
map.save_world("testMap.xml")
		
		