import matplotlib.pyplot as plt
import numpy as np

from ortools.linear_solver import pywraplp

MAX_TIME_SECONDS = 7200


class Facility:
    def __init__(self, index, setup_cost, capacity, location):
        self.index = index
        self.setup_cost = setup_cost
        self.capacity = capacity
        self.location = location


class Customer:
    def __init__(self, index, demand, location):
        self.index = index
        self.demand = demand
        self.location = location


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def visualize_solution(facilities, locations, solution):
    """
        Visualize the graph coloring solution
    :param facilities: The input facilities
    :param locations: The input locations
    :param solution: The selected solution
    """
    # Extract facility locations
    facility_locations = [(facility[2], facility[3]) for facility in facilities]

    # Extract locations
    locations = [(location[1], location[2]) for location in locations]

    # Plot facilities
    used_facilities = list()
    unused_facilities = list()
    for i, facility_location in enumerate(facility_locations):
        if i in solution:
            used_facilities.append(facility_location)
        else:
            unused_facilities.append(facility_location)

    print(len(facility_locations), len(used_facilities), len(unused_facilities), len(locations))
    plt.plot([facility[0] for facility in used_facilities], [facility[1] for facility in used_facilities], 'gs',
             label='Utilized Facilities')
    plt.plot([facility[0] for facility in unused_facilities], [facility[1] for facility in unused_facilities], 'rs',
             label='Unutilized Facilities')

    # Plot locations and their assigned facilities
    for i, location in enumerate(locations):
        plt.plot(location[0], location[1], 'bo')
        facility_index = solution[i]  # Facility index assigned to the customer
        if facility_index != -1:
            # Location of the assigned facility
            facility_location = facility_locations[facility_index]
            # Black line connecting customer to facility
            plt.plot([location[0], facility_location[0]], [location[1], facility_location[1]],'k-')

    plt.xlabel('X-coordinate')
    plt.ylabel('Y-coordinate')
    plt.title('Facility Location Problem Solution')
    plt.legend()
    plt.grid(True)
    plt.show()


def distance(point1, point2):
    return np.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)


def solve_it(input_data):
    lines = input_data.split('\n')
    parts = lines[0].split()
    facility_count = int(parts[0])
    customer_count = int(parts[1])

    facilities = list()
    for i in range(1, facility_count + 1):
        parts = lines[i].split()
        facilities.append([float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])])

    customers = list()
    for i in range(facility_count + 1, facility_count + 1 + customer_count):
        parts = lines[i].split()
        customers.append([int(parts[0]), float(parts[1]), float(parts[2])])
    # Create a solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    solver.set_time_limit(MAX_TIME_SECONDS * 60000)

    # Define variables
    x = dict()
    for i in range(facility_count):
        x[i] = solver.BoolVar('x[%i]' % i)

    y = dict()
    for i in range(facility_count):
        for j in range(customer_count):
            y[i, j] = solver.BoolVar('y[%i,%i]' % (i, j))

    # Define constraints
    # Each customer is served by at least one facility
    for j in range(customer_count):
        solver.Add(sum(y[i, j] for i in range(facility_count)) >= 1)

    # Each customer is served by at most one facility
    for j in range(customer_count):
        solver.Add(sum(y[i, j] for i in range(facility_count)) <= 1)

    # Facilities can only serve if they are opened
    for i in range(facility_count):
        for j in range(customer_count):
            solver.Add(y[i, j] <= x[i])

    # Facility capacity constraints
    for i in range(facility_count):
        solver.Add(sum(customers[j][0] * y[i, j] for j in range(customer_count)) <= facilities[i][1])

    # Define objective function
    objective = solver.Objective()
    for i in range(facility_count):
        objective.SetCoefficient(x[i], facilities[i][0])
        for j in range(customer_count):
            objective.SetCoefficient(y[i, j], distance(Point(customers[j][1], customers[j][2]),
                                                       Point(facilities[i][2], facilities[i][3])))

    objective.SetMinimization()

    # Solve the problem
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        optimal = 1
    else:
        optimal = 0

    total_cost = solver.Objective().Value()
    solution = [-1] * customer_count
    for j in range(customer_count):
        for i in range(facility_count):
            if y[i, j].solution_value() == 1:
                solution[j] = i
                break

    # Prepare the solution in the specified output format
    output_data = '%.2f' % total_cost + ' ' + str(optimal) + '\n'
    output_data += ' '.join(map(str, solution))

    visualize_solution(facilities, customers, solution)

    return output_data


if __name__ == '__main__':
    file_location = f'../data/fl_X_X'
    with open(file_location, 'r') as input_data_file:
        facility_input = input_data_file.read()
    print(solve_it(facility_input))
