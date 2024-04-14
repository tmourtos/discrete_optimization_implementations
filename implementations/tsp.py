import matplotlib.pyplot as plt

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

MAX_TIME_SECONDS = 7200

def visualize_tsp_solution(locations, route):
    """
        Visualize the graph coloring solution
    :param locations: The input locations
    :param route: The selected route
    """
    # Extract coordinates of locations
    x = [city[0] for city in locations]
    y = [city[1] for city in locations]

    # Plot locations
    plt.scatter(x, y, color='blue')

    # Plot connections between locations in the route
    for i in range(len(route) - 1):
        city1 = route[i]
        city2 = route[i + 1]
        plt.plot([locations[city1][0], locations[city2][0]], [locations[city1][1], locations[city2][1]], color='red')

    # Set plot title
    plt.title('TSP Solution Visualization')

    # Show plot
    plt.show()


def extract_route_from_solution(solution, manager, routing):
    """
        Extract the route from the solution
    :param solution: The input locations
    :param manager: The RoutingIndexManager
    :param routing: The selected routing
    """
    index = routing.Start(0)
    route = list()
    while not routing.IsEnd(index):
        node_index = manager.IndexToNode(index)
        route.append(node_index)
        index = solution.Value(routing.NextVar(index))
    return route


def create_data_model(input_data):
    """
        Extract the route from the solution
    :param input_data: The input data
    """
    lines = input_data.split('\n')
    node_count = int(lines[0])

    data = dict()
    data['points'] = list()
    for i in range(1, node_count + 1):
        line = lines[i]
        parts = line.split()
        data['points'].append((float(parts[0]), float(parts[1])))

    data['distance_matrix'] = [
        [0] * node_count for _ in range(node_count)]
    for from_node in range(node_count):
        for to_node in range(node_count):
            x1 = data['points'][from_node][0]
            y1 = data['points'][from_node][1]
            x2 = data['points'][to_node][0]
            y2 = data['points'][to_node][1]
            data['distance_matrix'][from_node][to_node] = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    data['num_vehicles'] = 1
    data['depot'] = 0
    return data


def solve_it(input_data):
    data = create_data_model(tsp_input)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']), data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        # Returns the distance between the two nodes.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Set First Solution Strategy
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES)

    # Set Local Search Metaheuristic
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH)

    search_parameters.time_limit.seconds = MAX_TIME_SECONDS

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    route = extract_route_from_solution(solution, manager, routing)
    total_distance = 0
    for i in range(len(route) - 1):
        total_distance += data['distance_matrix'][route[i]][route[i + 1]]

    if solution:
        # Format the solution
        formatted_solution = "{:.2f} {}\n".format(total_distance, 0)
        formatted_solution += ' '.join(map(str, route))

        visualize_tsp_solution(data['points'], route)
        return formatted_solution


if __name__ == '__main__':
    file_location = f'../data/tsp_X_X'
    with open(file_location, 'r') as input_data_file:
        tsp_input = input_data_file.read()
    print(solve_it(tsp_input))
