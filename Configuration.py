
import numpy as np
from Polygon import Vertex, Polygon
import random
from Fiber import Fiber,Edge
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch


def draw_diagonal_spring(ax, start_x, start_y, end_x, end_y, coils, radius):
    # Calculate the spring's length and angle
    dx = end_x - start_x
    dy = end_y - start_y
    spring_length = np.sqrt(dx**2 + dy**2)
    angle = np.arctan2(dy, dx)
    
    # Generate the x and y coordinates for the spring's linear path
    t = np.linspace(0, 1, num=1000)
    x_linear = start_x + t * dx
    y_linear = start_y + t * dy
    
    # Calculate the sine wave for the coils
    sine_wave = np.sin(np.linspace(0, coils * 2 * np.pi, num=1000)) * radius
    
    # Rotate the sine wave to align with the spring's angle
    sine_wave_x = sine_wave * np.cos(angle + np.pi/2)
    sine_wave_y = sine_wave * np.sin(angle + np.pi/2)
    
    # Adjust the spring's coordinates based on the sine wave to create coils
    x_spring = x_linear + sine_wave_x
    y_spring = y_linear + sine_wave_y
    
    # Plot the spring
    ax.plot(x_spring, y_spring, color="green", linewidth = 2)
    
    # Adjust plot limits and aspect ratio
    ax.set_aspect('equal', 'box')
    ax.set_xlim([min(start_x, end_x) - radius, max(start_x, end_x) + radius])
    ax.set_ylim([min(start_y, end_y) - radius, max(start_y, end_y) + radius])

    return

def plot_configuration(polygon, fiber, filename = "initial.png"):
    fig, ax = plt.subplots(figsize=(10,10))
    ColorMap = {"fixed": "red", "linker": "green", "free": "black"}

    # Plot the polygon

    for i, vertex in enumerate(polygon.vertices_):
        ForceArrowColor = "blue"
        # ax.plot(P.vertices_[i].position_,P.vertices_[i-1].position_,color='black')
        if vertex.is_fixed_:
            Color = ColorMap["fixed"]
            ForceArrowColor = "red"

        elif vertex.is_linked_: 
            Color = ColorMap["linker"]
        else:
            Color = ColorMap["free"]

        # add colored vertices for the polygon
            
        ax.plot(vertex.position_[0],vertex.position_[1],'o',color = Color)
        # Only draw the force if it is not if it is not too small
        if np.linalg.norm(vertex.force_) > 1e-15:
            ForceArrow = FancyArrowPatch(posA = vertex.position_,
                                         posB = np.add(vertex.position_,vertex.force_),
                                         arrowstyle='->,head_width=5,head_length=10',
                                         color=ForceArrowColor, linewidth=2)
            ax.add_patch(ForceArrow)
        EdgeArrow = FancyArrowPatch(posA = vertex.position_,
                                    posB = polygon.vertices_[i-1].position_,
                                    arrowstyle='-',
                                    color='black', linewidth=2)

        ax.add_patch(EdgeArrow)

    # plot the fiber
        
    for edge in fiber.edges_:
        ForceArrowColor = "blue"
        fiberEdgeArrow = FancyArrowPatch(posA = edge.nodes_[0].position_,
                                         posB = edge.nodes_[1].position_,
                                         arrowstyle='-',
                                         color='black', linewidth=2)
        
        # add colored nodes:
        for node in edge.nodes_:
            if node.is_fixed_:
                FiberNodeColor = ColorMap["fixed"]
                ForceArrowColor = "red"
            elif node.is_linked_: 
                FiberNodeColor = ColorMap["linker"]
            else:
                FiberNodeColor = ColorMap["free"]
            ax.plot(node.position_[0],node.position_[1],'o',color = FiberNodeColor)
            # Add force arrow at the node, but only if it is not too small
            if np.linalg.norm(node.force_) > 1e-15:
                ForceArrow = FancyArrowPatch(posA = node.position_,
                                             posB = np.add(node.position_,node.force_),
                                             arrowstyle='->,head_width=5,head_length=10',
                                             color=ForceArrowColor, linewidth=2)
                ax.add_patch(ForceArrow)

        


        ax.add_patch(fiberEdgeArrow)
    # draw the linker spring
        
    draw_diagonal_spring(ax,
                         polygon.vertices_[0].position_[0],
                         polygon.vertices_[0].position_[1],
                         fiber.edges_[0].nodes_[0].position_[0],
                         fiber.edges_[0].nodes_[0].position_[1],
                         4,
                         0.1
                         )
    plt.xlim(-4, 4)
    plt.ylim(-4, 4)
    plt.savefig(filename)
    plt.close()
    return

def initialize_a_fiber():
    l0 = 0.5
    num_edges = 2  
    edges = []
    nodes = []
    Node0 = Vertex(np.random.uniform(low = 1, high = 1+l0/2, size=2))
    nodes.append(Node0)
    for i in range(num_edges):

        # initialize an edge with a natural length of l0,
        # a random direction, and a random strain between -0.1 and 0.1,

        theta = random.uniform(-np.pi/2, np.pi/2)
        length = random.uniform(l0 -l0/10, l0 +l0/10)
        Node1 = np.add(nodes[-1].position_,
                       [length*np.cos(theta), length*np.sin(theta)])
        nodes.append(Vertex(Node1))
        edges.append(Edge([nodes[-2], nodes[-1]],
                          l0 = l0))
        # Node0 = copy.deepcopy(Node1)

    # the first node connects to a linker spring; the last node is fixed.
    edges[0].nodes_[0].is_linked_ = True
    edges[-1].nodes_[1].is_fixed_ = True

    return Fiber(edges)

def initialize_a_polygon(P0 = 3.7):
    num_vertices = random.randint(5, 8)
    theta = 2 * np.pi / num_vertices
    vertices = []
    for i in range(num_vertices):
        r_vertex = np.sqrt(1/np.pi) + random.uniform(-0.1, 0.1)
        theta_vertex = i*theta + random.uniform(-0.001, 0.001)
        x = r_vertex * np.cos(theta_vertex)
        y = r_vertex * np.sin(theta_vertex)
        vertices.append(Vertex([x, y]))

    # the first vertex connects to a linker spring.
    # Some other vertex, chosen at random, is fixed.
    vertices[0].is_linked_ = True
    vertices[random.randint(1, num_vertices-1)].is_fixed_ = True
    return Polygon(vertices,P0)

def initialize_a_configuration(): pass