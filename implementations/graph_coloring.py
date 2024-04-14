
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.cm as cm

from ortools.sat.python import cp_model

MAX_TIME_SECONDS = 1500

def visualize_graph(graph, coloring):
    """
        Visualize the graph coloring solution
    :param graph: The input graph
    :param coloring: The coloring for each node
    """
    nx_graph = nx.Graph()
    nx_graph.add_nodes_from(graph.keys())
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            if (neighbor, node) not in nx_graph.edges():  # Avoid adding duplicate edges
                nx_graph.add_edge(node, neighbor)

    # Define positions for the nodes (random positions for simplicity)
    pos = nx.spring_layout(nx_graph)

    # Calculate the number of colors used
    num_colors = len(set(coloring))

    # Create a list of colors for each node based on the coloring
    color_map = cm.get_cmap('rainbow', num_colors)
    colors = [color_map(color / (num_colors - 1)) for color in coloring]

    # Draw the graph
    nx.draw(nx_graph, pos, with_labels=True, node_color=colors, cmap=cm.rainbow)

    # Show the plot
    plt.show()

def cp_algorithm(graph):
    """
        The constraint programming algorithm
    :param graph: The input graph
    """
    model = cp_model.CpModel()
    num_nodes = len(graph)
    max_degree = max(len(neighbors) for neighbors in graph.values())

    # Define variables for node colors
    node_colors = [model.NewIntVar(0, max_degree, f'node_{i}') for i in range(num_nodes)]

    # Add constraints to ensure no adjacent nodes have the same color
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            model.Add(node_colors[node] != node_colors[neighbor])

    # Define the objective to minimize the maximum color
    max_color = model.NewIntVar(0, max_degree, 'max_color')
    model.AddMaxEquality(max_color, node_colors)
    model.Minimize(max_color)

    # Create solver and solve the model
    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = False  # Enable logging for debugging
    # Set search strategy
    solver.parameters.search_branching = cp_model.FIXED_SEARCH

    # Set time limit (in seconds)
    solver.parameters.max_time_in_seconds = MAX_TIME_SECONDS

    # Set solution limit
    solver.parameters.enumerate_all_solutions = False
    solver.Solve(model)
    return [solver.Value(node_colors[i]) for i in range(num_nodes)]

def solve_it(input_data):
    lines = input_data.strip().split('\n')
    node_count, edge_count = map(int, lines[0].split())

    # Build the adjacency list representation of the graph
    graph = {i: [] for i in range(node_count)}
    for line in lines[1:]:
        u, v = map(int, line.split())
        graph[u].append(v)
        graph[v].append(u)

    # Perform graph coloring using constraint programming
    coloring = cp_algorithm(graph)

    visualize_graph(graph, coloring)

    return format_output(coloring)

def format_output(coloring):
    num_colors = max(coloring) + 1
    output_data = f"{num_colors} {0}\n"
    output_data += ' '.join(map(str, coloring))
    return output_data


if __name__ == '__main__':
    file_location = f'../data/gc_X_X'
    with open(file_location, 'r') as input_data_file:
        coloring_input = input_data_file.read()
    print(solve_it(coloring_input))
