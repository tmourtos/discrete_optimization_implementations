import time
import matplotlib.pyplot as plt


class Item(object):
    def __init__(self, index, value, weight):
        self.index = index
        self.value = value
        self.weight = weight


def visualize_knapsack(input_data, taken):
    """
        Visualize the knapsack solution
    :param input_data: The input data
    :param taken: The taken items
    """
    lines = input_data.split('\n')

    first_line = lines[0].split()
    item_count = int(first_line[0])

    items = list()

    for i in range(1, item_count + 1):
        line = lines[i]
        parts = line.split()
        items.append((int(parts[0]), int(parts[1])))

    # Create lists to store item weights and values
    weights = [item[0] for item in items]
    values = [item[1] for item in items]

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(weights)), values, color='blue', alpha=0.5, label='Value')
    plt.bar(range(len(weights)), weights, color='green', alpha=0.5, label='Weight')

    # Highlight the items selected in the knapsack
    for i in range(len(taken)):
        if taken[i] == 1:
            plt.annotate('X', (i, values[i]), ha='center', va='bottom', color='red', fontsize=12)

    plt.xlabel('Item')
    plt.ylabel('Value / Weight')
    plt.title('Knapsack Visualization')
    plt.xticks(range(len(weights)), [f'Item {i + 1}' for i in range(len(weights))], rotation=90)
    plt.legend()
    plt.tight_layout()
    plt.show()


def solve_it(input_data):
    """
        Solve the knapsack problem
    :param input_data: The input data
    :return: The formatted solution
    """

    lines = input_data.split('\n')

    first_line = lines[0].split()
    item_count = int(first_line[0])
    total_capacity = int(first_line[1])

    items = list()

    for i in range(1, item_count + 1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i - 1, int(parts[0]), int(parts[1])))

    # Initialize a table to store the maximum value that can be achieved
    # using items up to a certain index with a certain capacity
    table = [[0] * (total_capacity + 1) for _ in range(item_count + 1)]

    # Fill the table using dynamic programming
    for i in range(1, item_count + 1):
        for active_capacity in range(1, total_capacity + 1):
            if items[i - 1].weight <= active_capacity:
                table[i][active_capacity] = max(table[i - 1][active_capacity],
                                                table[i - 1][active_capacity - items[i - 1].weight] + items[
                                                    i - 1].value)
            else:
                table[i][active_capacity] = table[i - 1][active_capacity]

    # Backtrack to find which items are selected
    value = table[item_count][total_capacity]
    taken = [0] * item_count
    active_capacity = total_capacity
    for i in range(item_count, 0, -1):
        if value <= 0:
            break
        if value == table[i - 1][active_capacity]:
            continue
        else:
            taken[items[i - 1].index] = 1
            value -= items[i - 1].value
            active_capacity -= items[i - 1].weight

    # Prepare the solution in the specified output format
    output_data = str(table[item_count][total_capacity]) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, taken))

    # Visualize the knapsack
    visualize_knapsack(input_data, taken)

    return output_data


if __name__ == '__main__':
    file_location = r'../data/ks_X_X'
    with open(file_location, 'r') as input_data_file:
        knapsack_input = input_data_file.read()
    print(solve_it(knapsack_input))
