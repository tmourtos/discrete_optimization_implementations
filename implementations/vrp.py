
import matplotlib.pyplot as plt

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

MAX_TIME_SECONDS = 7200

class Customer:
    def __init__(self, index, demand, x, y):
        self.index = index
        self.demand = demand
        self.x = x
        self.y = y


def visualize_routes(input_data, solution):
    """
        Visualize the graph coloring solution
    :param input_data: The input data
    :param solution: The selected solution
    """
    lines = input_data.split('\n')
    parts = lines[0].split()
    customer_count = int(parts[0])
    locations = list()
    for i in range(1, customer_count + 1):
        line = lines[i]
        parts = line.split()
        locations.append((float(parts[1]), float(parts[2])))
    depot = locations[0]

    # Extract routes from the solution
    routes = list()
    for route_str in solution.split('\n'):
        route = list(map(int, route_str.split()))
        if len(route) > 2:
            routes.append([locations[i] for i in route])

    # Plot the routes
    plt.figure(figsize=(10, 7))
    plt.scatter(*zip(*locations), color='blue', label='Locations')
    plt.scatter(*depot, color='red', label='Depot', marker='s', s=100)
    for i, route in enumerate(routes):
        route = list(zip(*route))
        plt.plot(*route, marker='o', label=f'Vehicle {i+1}')
    plt.title('Vehicle Routing Problem Solution')
    plt.xlabel('X-coordinate')
    plt.ylabel('Y-coordinate')
    plt.legend()
    plt.grid(True)
    plt.show()

def create_data_model(locations, vehicle_capacity, vehicle_count):
    """
        Extract the route from the solution
    :param locations: The input locations
    :param vehicle_capacity: The vehicle capacity
    :param vehicle_count: The vehicle count
    """
    data = dict()
    data['distance_matrix'] = [
        [
            length(location1, location2) for location2 in locations
        ] for location1 in locations
    ]
    data['num_vehicles'] = vehicle_count
    data['depot'] = 0
    data['demands'] = [location.demand for location in locations]
    data['vehicle_capacities'] = [vehicle_capacity] * vehicle_count
    return data

def length(location1, location2):
    return ((location1.x - location2.x) ** 2 + (location1.y - location2.y) ** 2) ** 0.5


def solve_it(input_data):

    lines = input_data.split('\n')
    parts = lines[0].split()
    customer_count = int(parts[0])
    vehicle_count = int(parts[1])
    vehicle_capacity = int(parts[2])

    customers = list()
    for i in range(1, customer_count + 1):
        line = lines[i]
        parts = line.split()
        customers.append(Customer(i - 1, int(parts[0]), float(parts[1]), float(parts[2])))
    data = create_data_model(customers, vehicle_capacity, vehicle_count)
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Adjust solver parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = MAX_TIME_SECONDS

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        # Calculate the total distance traveled by all vehicles
        total_distance = 0
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            vehicle_route_distance = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                next_index = solution.Value(routing.NextVar(index))
                vehicle_route_distance += distance_callback(index, next_index)
                index = next_index
            total_distance += vehicle_route_distance

        output_data = "{:.2f} {}\n".format(total_distance, 0)
        visualization_input = ''
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route = list()
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route.append(node_index)
                index = solution.Value(routing.NextVar(index))
            route.append(manager.IndexToNode(index))
            output_data += " ".join(map(str, route)) + "\n"
            visualization_input += " ".join(map(str, route)) + "\n"

        visualize_routes(input_data, visualization_input)

        return output_data
    else:
        return 'No solution found within the time limit.'


if __name__ == '__main__':
    file_location = f'../data/vrp_X_X_X'
    with open(file_location, 'r') as input_data_file:
        vrp_input = input_data_file.read()
    print(solve_it(vrp_input))
