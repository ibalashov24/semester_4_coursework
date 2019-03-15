var __interpretation_started_timestamp__;
var pi = 3.1415926535897931;

// Robot parameters
var wheel_diameter = 56.0; // mm
var encoder_signals_per_turn = 630; // encoder signals
var base_delay = 20; // ms

// Map parameters
var cell_side = 400.0; // mm
var cell_count = 8;
var side_half_corridor_width = 33; // in infrared sensor points; might be rewritten!
var forward_half_corridor_width = 33; // in sonic sensor points; might be rewritten!

// Map
var input_map =
		[
			[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
			[1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
			[1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
			[1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1],
			[1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
			[1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
			[1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
			[1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
			[1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1],
			[1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
			[1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
			[1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		] // Map for Task_1_[0..29]
		
// Helpful aliases
var left_motor = M1;
var right_motor = M2;
var left_encoder = E1;
var right_encoder = E2;
var left_IR_sensor = A1;
var right_IR_sensor = A2;
var forward_sonic_sensor = D1;

// Structures 
const Direction = {
		LEFT : 1,
		RIGHT : 2,
		FORWARD : 3,
		BACKWARD : 4 };
		
const Cell_type = {
		EMPTY : 0,
		WALL : 1,
		UNKNOWN : -1 };
		

/***** Code *****/


/***** Movement *****/


// Returns yaw relative to calibration position
var get_current_angle = function()
{
	return brick.gyroscope().read()[6] / 1000;
}

// If left cell is occupied with wall, 
// returns distance to the wall; 0 else
var is_left_occupied = function()
{
	var left_distance = brick.sensor(left_IR_sensor).read();
	return (left_distance > 2 * side_half_corridor_width ? 0 : left_distance);
}

// If right cell is occupied with wall, 
// returns distance to the wall; 0 else
var is_right_occupied = function()
{
	var right_distance = brick.sensor(right_IR_sensor).read();
	return (right_distance > 2 * side_half_corridor_width ? 0 : right_distance);
}

// If forward cell is occupied with wall, 
// returns distance to the wall; 0 else
var is_straight_occupied = function()
{
	var forward_distance = brick.sensor(forward_sonic_sensor).read();
	return (forward_distance > cell_side / 10 ? 0 : forward_distance);
}

// Calculates coefficient for proportional controller which reflect IR sensors indication
var calc_alignment = function()
{
	// Empirically detected
	var k_alignment = 0.1;
	
	var left_distance = is_left_occupied();
	var right_distance = is_right_occupied();
	
	var alignement = 0;
	// Pushing off from one of the walls
	if (left_distance != 0 && left_distance < right_distance && left_distance < 2 * side_half_corridor_width)
	{
		alignement = -side_half_corridor_width + left_distance;
	}
	else if (right_distance != 0 && right_distance < left_distance && right_distance < 2 * side_half_corridor_width)
	{
		alignement = side_half_corridor_width - right_distance;
	}
	
	if (Math.abs(alignement) > 20)
	{
		alignement = (alignement < 0 ? 20 : -20);
	}
	
	return alignement * k_alignment;
}

// Calculates coefficient for proportional controller which reflect gyroscope indication
var calc_deflection = function(start_angle)
{
	var k_deflection = 0.1;
	var current_angle = get_current_angle();
	
	// Converting into new coordinate system centered at start_angle
	var deflect_angle = recalculate_angle(current_angle - start_angle);
	
	// Limits max effect
	if (Math.abs(deflect_angle) > 10)
	{
		deflect_angle = deflect_angle < 0 ? -10 : 10;
	}
	
	return k_deflection * deflect_angle;
}

// Stops robot's motors
var stop_robot = function()
{
	brick.motor(left_motor).setPower(0);
	brick.motor(right_motor).setPower(0);	
}

// Moves the robot one cell forward
var move_forward = function(start_angle)
{	
	// Empirically detected
	var k_turns_to_power = 3;
	var default_forward_speed = 15; // encoder signals per 1 iteration
	
	// Virtual wheels
	var virtual_encoder_left = 0;
	var virtual_encoder_right = 0;
	
	// Real wheels
	var encoder_left = 0;
	var encoder_right = 0;
	brick.encoder(left_encoder).reset();
	brick.encoder(right_encoder).reset();
	
	var path_to_go = encoder_signals_per_turn * cell_side / (pi * wheel_diameter);	
	
	print("Moving forward: " + path_to_go + " signals; direction: " + start_angle);
	
	while (brick.sensor(forward_sonic_sensor).read() > forward_half_corridor_width 
			&& (encoder_left + encoder_right) / 2 < path_to_go)
	{
		var deflection_coefficient = calc_deflection(start_angle);
		//print("Deflect: " + deflection_coefficient * 10);
		
		var alignment_coefficient = calc_alignment();
		//print("Alignment coefficient: " + alignment_coefficient);
		
		virtual_encoder_left += default_forward_speed - deflection_coefficient - alignment_coefficient;
		virtual_encoder_right += default_forward_speed + deflection_coefficient + alignment_coefficient;
		// print("Virtual wheel: " + virtual_encoder_left + " " + virtual_encoder_right);
		
		encoder_left = brick.encoder(left_encoder).read();
		encoder_right = brick.encoder(right_encoder).read();
		var left_motor_power = (virtual_encoder_left - encoder_left) * k_turns_to_power;
		var right_motor_power = (virtual_encoder_right - encoder_right) * k_turns_to_power;
		
		//print("Motor power: " + left_motor_power + " " + right_motor_power);
		
		brick.motor(left_motor).setPower(left_motor_power);
		brick.motor(right_motor).setPower(right_motor_power);
		
		script.wait(base_delay);
	}
}

// Puts given angle into [-180..180] range
var recalculate_angle = function(angle)
{
	if (angle > 180)
	{
		return angle - 360;
	} else if (angle < -180)
	{
		return angle + 360;
	}
	
	return angle;
}

// Turns the robot in place at a specified relative angle
var make_turn_in_place = function(angle, start_angle)
{
	var default_turn_speed = 10;	// percents of motor power
	var max_angle_deflect = 40;		// degrees
	var k_turn = 0.3;				// Empirically detected
	
	var target =  get_current_angle() + angle;
	var k = angle > 0 ? 1 : -1;	// Defines the direction of rotation
	
	print("Turn: start " + start_angle + "; target " + target + "; fact " + get_current_angle());
	
	var current_angle = get_current_angle();
	var last_angle = current_angle;
	
	// We are translating [-180..180] angle scale to [-inf..inf] scale
	// in order to avoid 180/-180 problem
	var converting_factor = 0;
	while (k * current_angle < k * target)
	{
		//print("Angle : " + current_angle);
		
		brick.motor(left_motor).setPower(k * default_turn_speed + k_turn * (target - current_angle));
		brick.motor(right_motor).setPower(-k * default_turn_speed - k_turn * (target - current_angle));
		
		script.wait(2 * base_delay);
		
		var real_current_angle = get_current_angle();
		var supposed_current_angle = real_current_angle + k * converting_factor * 360;
		if (Math.abs(supposed_current_angle - last_angle) > max_angle_deflect)
		{
			++converting_factor;
		}
		
		last_angle = current_angle;
		current_angle = real_current_angle + k * converting_factor * 360;
	}
	
	stop_robot();
	
	return angle;
}


/***** Localization *****/

// Reads map from some input (DUMMY)
var read_map = function()
{
	return input_map;
}

// Recalculates current position after forward 
// move in the position.angle direction
var reflect_forward_movement = function(position)
{
	var begin_position = { x : 0, y : 0, angle : 0 };
	
	var forward_wall = get_forward_cell_coordinate(begin_position, position);
	forward_wall.angle = position.angle;
	var forward_cell = get_forward_cell_coordinate(begin_position, forward_wall); 
	
	//print("forward_cell " + forward_cell.x + " " + forward_cell.y);
	
	return { x : forward_cell.x, y : forward_cell.y, angle : position.angle };
}

// Calculates absolute cell coordinates from relative ones
var get_current_cell_coordinate = function(origin, relative_position)
{
	var result = { x : origin.x, y : origin.y, angle : origin.angle };
	switch (origin.angle)
	{
		case 0:
			result.x += relative_position.x;
			result.y += relative_position.y;
			break;
		case 90:
			result.x -= relative_position.y;
			result.y += relative_position.x;
			break;
		case -90:
			result.x += relative_position.y;
			result.y -= relative_position.x;
			break;
		case 180:
		case -180:
			result.x -= relative_position.x;
			result.y -= relative_position.y;
			break;
	}
	
	return result;
}

// Calculates the coordinates of the cell in front of the robot
var get_forward_cell_coordinate = function(origin, relative_position)
{
	var new_relative_position = 
		{ 
			x : relative_position.x, y : relative_position.y, angle : relative_position.angle 
		};
	switch(relative_position.angle)
	{
		case 0:
			++new_relative_position.y;
			break;
		case -90:
			++new_relative_position.x;
			break;
		case 90:
			--new_relative_position.x;
			break;
		case 180:
		case -180:
			--new_relative_position.y;
			break;
	}
	
	return get_current_cell_coordinate(origin, new_relative_position);	
}

// Calculates the coordinates of the cell to the left of the robot.
var get_left_cell_coordinate = function(hypothesis, relative_position)
{
	var result = get_forward_cell_coordinate(hypothesis, 
		{ 
			x : relative_position.x, 
			y : relative_position.y, 
			angle : recalculate_angle(relative_position.angle - 90) 
		});
	return { x : result.x, y : result.y, angle : relative_position.angle };
}

// Calculates the coordinates of the cell to the right of the robot.
var get_right_cell_coordinate = function(hypothesis, relative_position)
{
	var result = get_forward_cell_coordinate(hypothesis, 
		{ 
			x : relative_position.x, 
			y : relative_position.y, 
			angle : recalculate_angle(relative_position.angle + 90) 
		});
	return { x : result.x, y : result.y, angle : recalculate_angle(result.angle - 90) };
}

// Checks if given coordinates belong to the map
var is_in_bounds = function(map, coordinates)
{
	return (coordinates.x >= 0 && coordinates.x < map[0].length &&
			coordinates.y >= 0 && coordinates.y < map.length);
}

// Cuts off wrong hyposheses about start cell location
var filter_hypotheses = function(map, hypotheses, position)
{
	var is_left_empty = !is_left_occupied();
	var is_right_empty = !is_right_occupied();
	var is_forward_empty = !is_straight_occupied();
	
	print("Relative coords: " + position.x + " " + position.y + " " + position.angle);
	
	var filtered = [];
	for (var i = 0; i < hypotheses.length; ++i)
	{
		//print("Hypo: " + hypotheses[i].x + " " + hypotheses[i].y + " " + hypotheses[i].angle);
		
		var left_cell = get_left_cell_coordinate(hypotheses[i], position);
		var right_cell = get_right_cell_coordinate(hypotheses[i], position);
		var forward_cell = get_forward_cell_coordinate(hypotheses[i], position);
		var current_cell = get_current_cell_coordinate(hypotheses[i], position);
		
		/*print("Calculated current: " + current_cell.x + " " + current_cell.y);
		print("Calculated left: " + left_cell.x + " " + left_cell.y);
		print();*/
		
		if (is_in_bounds(map, current_cell) && map[current_cell.y][current_cell.x] == Cell_type.EMPTY &&
			(map[left_cell.y][left_cell.x] == Cell_type.EMPTY) == is_left_empty &&
			(map[right_cell.y][right_cell.x] == Cell_type.EMPTY) == is_right_empty &&
			(map[forward_cell.y][forward_cell.x] == Cell_type.EMPTY) == is_forward_empty)
		{
			filtered.push(hypotheses[i]);
		}
	}
	
	return filtered;
}

// Returns initial set of hypotheses about start cell location
var init_hypotheses = function(map)
{
	// We hypothesize only cells that a robot can visit
	var result = [];
	for (var i = 1; i < map.length - 1; i += 2)
	{
		for (var j = 1; j < map[0].length - 1; j += 2)
		{
			if (map[i][j] == Cell_type.EMPTY)
			{
				result.push({ x : j, y : i, angle : 0});
				result.push({ x : j, y : i, angle : 90});
				result.push({ x : j, y : i, angle : -90});
				result.push({ x : j, y : i, angle : 180});
			}
		}
	}
	
	return result;
}

// Returns the position of the first occurrence
// sample_cells in robot_path from the end of the array
var get_nearest_cycle_distance = function(robot_path, sample_cells)
{
	for (var i = robot_path.length - sample_cells.length; i >= 0; --i)
	{
		var is_entry = true;
		for (var j = 0; j < sample_cells.length; ++j)
		{
			if (robot_path[i + j].x != sample_cells[j].x
				|| robot_path[i + j].y != sample_cells[j].y)
			{
				is_entry = false;
				break;
			}
		}
		
		if (is_entry)
		{
			return robot_path.length - i;
		}
	}
	
	return robot_path.length;
}

// Determines robot's next movement direction basing on the current position
var determine_direction = function(robot_path, position)
{
	var origin = { x : 0, y : 0, angle : 0};	// Relative origin
	// We should get next accesible cell (not the wall)
	var left_cell = get_left_cell_coordinate(origin, get_left_cell_coordinate(origin, position));
	var right_cell = get_right_cell_coordinate(origin, get_right_cell_coordinate(origin, position));
	var forward_cell = get_forward_cell_coordinate(origin, get_forward_cell_coordinate(origin, position));

	// Trying to avoid looping
	var left_cycle_distance = !is_left_occupied() ? get_nearest_cycle_distance(robot_path, [position, left_cell]) : 0;
	var right_cycle_distance = !is_right_occupied() ? get_nearest_cycle_distance(robot_path, [position, right_cell]) : 0;
	var forward_cycle_distance = !is_straight_occupied() ? get_nearest_cycle_distance(robot_path, [position, forward_cell]) : 0;
	
	// Looking for cycle which was visited the longest time ago
	var max_distance = Math.max(left_cycle_distance, right_cycle_distance, forward_cycle_distance);
	
	if (max_distance == 0)	// Walls everywhere
	{
		return Direction.BACKWARD;
	}
	else if (left_cycle_distance == max_distance)
	{
		return Direction.LEFT
	}
	else if (forward_cycle_distance == max_distance)
	{
		return Direction.FORWARD;
	}
	else
	{
		return Direction.RIGHT
	}
}

// Determines robot's next movement and executes it
var make_move = function(robot_path, position)
{
	var handle_forward_movement = function()
	{
		move_forward(position.angle);
		position = reflect_forward_movement(position)
		robot_path.push(position);
	}
	
	var handle_rotation = function(angle)
	{
		make_turn_in_place(angle, position.angle);
		position.angle = recalculate_angle(position.angle + angle);
	}
	
	var move_direction = determine_direction(robot_path, position);
	
	if (move_direction == Direction.BACKWARD)
	{
		handle_rotation(180);
	}
	else if (move_direction == Direction.LEFT)
	{			
		handle_rotation(-90);
		handle_forward_movement();
	}
	else if (move_direction == Direction.FORWARD)
	{
		handle_forward_movement();
	}
	else if (move_direction == Direction.RIGHT)
	{
		handle_rotation(90);
		handle_forward_movement();
	}
	
	return position;
}

// Goes through the labyrinth using left-hand rule
var solve_the_labyrinth = function()
{	
	var full_map = read_map();
	var hypotheses = init_hypotheses(full_map);
	var relative_position =
		{
			x : 0,
			y : 0,
			angle : 0
		};
		
	// Inititializing robot path
	var robot_path = [];
	robot_path.push(relative_position);
		
	// Main loop
	while (hypotheses.length != 1)
	{
		print("Remaining hypotheses count: " +  hypotheses.length);
		
		relative_position = make_move(robot_path, relative_position);
		hypotheses = filter_hypotheses(full_map, hypotheses, relative_position);
	}
	
	// Getting start cell coordinates
	var confirmed_hypothesis = hypotheses.pop();
	var absolute_coordinates = get_current_cell_coordinate(confirmed_hypothesis, { x : 0, y : 0, angle : 0 });
	
	var start_cell_x = Math.floor(absolute_coordinates.x / 2 + 1);
	var start_cell_y = Math.floor(absolute_coordinates.y / 2 + 1);
	print('Result: x = ' +  start_cell_x + ' y = ' + start_cell_y);
	/*brick.display().addLabel(start_cell_x + ' ' + start_cell_y, 1, 1);
	brick.display().redraw();
	script.wait(1000);*/
}


/***** Main code *****/


// Initializes algorithm
var init_robot = function()
{
	brick.gyroscope().calibrate(2000);
	script.wait(2500);
	
	var left_distance = brick.sensor(left_IR_sensor).read();
	var right_distance = brick.sensor(right_IR_sensor).read();
	var forward_distance = brick.sensor(forward_sonic_sensor).read();
	
	side_half_corridor_width = Math.min(left_distance, right_distance, side_half_corridor_width);
	forward_half_corridor_width = Math.min(forward_distance, forward_half_corridor_width);
}

var main = function()
{
	__interpretation_started_timestamp__ = Date.now();
	
	init_robot();
	
	solve_the_labyrinth();
	
	return;
}
