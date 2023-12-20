# Verwsion: 1.0.3
# Last Update: 2023/12/20
# Authoer: Tomio Kobayashi

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class DataJourneyDAG:

    def __init__(self):
        self.vertex_names = []
        self.adjacency_matrix = []
        self.adjacency_matrix_T = []
        self.size_matrix = 0
        
    def adjacency_matrix_to_edge_list(self, adc_matrix):
        """
        Converts an adjacency matrix to an edge list.

        Args:
            adjacency_matrix: A 2D list representing the adjacency matrix.

        Returns:
            A list of tuples, where each tuple represents an edge (source node, target node).
        """

        edge_list = []
        num_nodes = len(adc_matrix)

        for i in range(num_nodes):
            for j in range(num_nodes):
                if adc_matrix[i][j] == 1:
                    edge_list.append((i, j))  # Add edges only for non-zero entries

        return edge_list
    
    def draw_selected_vertices_reverse(self, adj_matrix, selected_vertices1, selected_vertices2, title, node_labels, pos, reverse=False):
        # Create a directed graph from the adjacency matrix
        G = nx.DiGraph(adj_matrix)

        # Create a subgraph with only the selected vertices
        subgraph1 = G.subgraph(selected_vertices1)
        subgraph2 = G.subgraph(selected_vertices2)
        
        if reverse:
            subgraph1 = subgraph1.reverse()
            subgraph2 = subgraph2.reverse()

        # Set figure size to be larger
        plt.figure(figsize=(12, 8))

        # Draw the graph
        nx.draw(subgraph1, pos, with_labels=True, labels=node_labels, node_size=600, node_color='skyblue', font_size=8, font_color='black', font_weight='bold', arrowsize=10, edgecolors='black', linewidths=1)
        nx.draw(subgraph2, pos, with_labels=True, labels=node_labels, node_size=1000, node_color='pink', font_size=8, font_color='black', font_weight='bold', arrowsize=10, edgecolors='black', linewidths=1)

        plt.title(title)
        plt.show()

    def edge_list_to_adjacency_matrix(self, edges):
        """
        Converts an edge list to an adjacency matrix.

        Args:
            edges: A list of tuples, where each tuple represents an edge (source node, target node).

        Returns:
            A 2D list representing the adjacency matrix.
        """

        num_nodes = max(max(edge) for edge in edges) + 1  # Determine the number of nodes
        adjacency_matrix = [[0] * num_nodes for _ in range(num_nodes)]

        for edge in edges:
            adjacency_matrix[edge[0]][edge[1]] = 1

        return adjacency_matrix

    def data_import(self, file_path, is_edge_list=False):
#         Define rows as TO and columns as FROM
        if is_edge_list:
            edges = self.read_edge_list_from_file(file_path)
            self.adjacency_matrix = self.edge_list_to_adjacency_matrix(edges)
        else:
            data = np.genfromtxt(file_path, delimiter='\t', dtype=str, encoding=None)

            # Extract the names from the first record
            self.vertex_names = data[0]

            # Extract the adjacency matrix
            self.adjacency_matrix = data[1:]
        
        # Convert the adjacency matrix to a NumPy array of integers
        self.adjacency_matrix = np.array(self.adjacency_matrix, dtype=int)

        self.adjacency_matrix_T = self.adjacency_matrix.T

        # Matrix of row=FROM, col=TO
        self.size_matrix = len(self.adjacency_matrix)

    def write_edge_list_to_file(self, filename):
        """
        Writes an edge list to a text file.

        Args:
            edges: A list of tuples, where each tuple represents an edge (source node, target node).
            filename: The name of the file to write to.
        """
        edges = self.adjacency_matrix_to_edge_list(self.adjacency_matrix)

        with open(filename, "w") as file:
            # Write headers
            file.write("\t".join(self.vertex_names) + "\n")
            for edge in edges:
                file.write(f"{edge[0]}\t{edge[1]}\n")

    def read_edge_list_from_file(self, filename):
        """
        Reads an edge list from a text file.

        Args:
            filename: The name of the file to read.

        Returns:
            A list of tuples, where each tuple represents an edge (source node, target node).
        """

        edges = []
        with open(filename, "r") as file:
            ini = True
            for line in file:
                if ini:
                    self.vertex_names = line.strip().split("\t")
                    ini = False
                else:
                    source, target = map(int, line.strip().split())
                    edges.append((source, target))
        return edges

    def write_adjacency_matrix_to_file(self, filename):
        """
        Writes a matrix to a tab-delimited text file.

        Args:
            matrix: The matrix to write.
            filename: The name of the file to write to.
        """

        with open(filename, "w") as file:
            file.write("\t".join(self.vertex_names) + "\n") 
            for row in self.adjacency_matrix:
                file.write("\t".join(map(str, row)) + "\n")  # Join elements with tabs and add newline


# Example usage

    def drawOrigins(self, target_vertex):


        # Draw the path TO the target
        res_vector = np.array([np.zeros(self.size_matrix) for i in range(self.size_matrix+1)])
        res_vector[0][target_vertex] = 1
        for i in range(self.size_matrix):
            if sum(res_vector[i]) == 0:
                break
            res_vector[i+1] = self.adjacency_matrix @ res_vector[i]

        res_vector_T = res_vector.T

        selected_vertices1 = set()
        for i in range(len(res_vector)):
            if sum(res_vector[i]) == 0:
                break
            for j in range(len(res_vector[i])):
                if j == 0:
                    continue
                if res_vector[i][j] != 0 and j != 0: 
                    selected_vertices1.add(j)

        position = {}
        colpos = {}
        posfill = set()

        for i in range(len(res_vector)):
            colpos[i] = 0

        last_pos = 0
        for i in range(len(res_vector)):
            if sum(res_vector[i]) == 0:
                break
            last_pos += 1

        done = False
        largest_j = 0
        for i in range(len(res_vector)):
            if sum(res_vector[i]) == 0:
                break
            nonzero = 0
            for j in range(len(res_vector[i])):
                if j not in selected_vertices1:
                    continue
                if j in posfill:
                    continue
                if j == 0:
                    continue
                if res_vector[i][j]:
                    posfill.add(j)
                    position[j] = ((last_pos-i), colpos[(last_pos-i)]) 
                    colpos[(last_pos-i)] += 1
                    if largest_j < j:
                        largest_j = j


        selected_vertices1 = list(selected_vertices1)

        selected_vertices2 = [target_vertex]

        node_labels = {i: name for i, name in enumerate(self.vertex_names) if i in selected_vertices1 or i in selected_vertices2}
        title = "Data Origins (" + str(last_pos-2) + " stages)"
        self.draw_selected_vertices_reverse(self.adjacency_matrix, selected_vertices1,selected_vertices2, title=title, node_labels=node_labels, pos=position)

        
    def drawOffsprings(self, target_vertex):

#         Draw the path FROM the target
        position = {}
        colpos = {}
        posfill = set()
        selected_vertices1 = set()
        res_vector = np.array([np.zeros(self.size_matrix) for i in range(self.size_matrix+1)])
        res_vector[0][target_vertex] = 1

        for i in range(len(res_vector)):
            colpos[i] = 0

        for i in range(self.size_matrix):
            if sum(res_vector[i]) == 0:
                break
            res_vector[i+1] = self.adjacency_matrix_T @ res_vector[i]
        for i in range(len(res_vector)):
            if sum(res_vector[i]) == 0:
                break
            for j in range(len(res_vector[i])):
                if res_vector[i][j] != 0 and j != self.size_matrix - 1 and j != 0: 
                    selected_vertices1.add(j)
        last_pos = 0
        for i in range(len(res_vector)):
            if sum(res_vector[i]) == 0:
                break
            last_pos += 1
        done = False
        largest_j = 0
        for i in range(len(res_vector)):
            if sum(res_vector[i]) == 0:
                break
            nonzero = 0
            for j in range(len(res_vector[i])):
                if j not in selected_vertices1:
                    continue
                if j in posfill:
                    continue
                if j == 0 or j == self.size_matrix - 1:
                    continue
                if res_vector[i][j]:
                    posfill.add(j)
                    position[j] = (i, colpos[i]) 
                    colpos[i] += 1
                    if largest_j < j:
                        largest_j = j
                    
        selected_vertices1 = list(selected_vertices1)
        selected_vertices2 = [target_vertex]

        node_labels = {i: name for i, name in enumerate(self.vertex_names) if i in selected_vertices1 or i in selected_vertices2}

        title = "Data Offsprings (" + str(last_pos-2) + " stages)"
        self.draw_selected_vertices_reverse(self.adjacency_matrix_T, selected_vertices1,selected_vertices2, title=title, node_labels=node_labels, pos=position, reverse=True)


mydag = DataJourneyDAG()
# mydag.data_import('/kaggle/input/matrix2/adjacency_matrix2.txt')
# mydag.data_import('dag_data_with_headers.txt')
mydag.data_import('dag_data9.txt')
# mydag.data_import('edge_list.txt', is_edge_list=True)
mydag.write_edge_list_to_file('edge_list2.txt')
# mydag.write_adjacency_matrix_to_file('dag_data9.txt')

mydag.drawOrigins(250)
mydag.drawOffsprings(250)


