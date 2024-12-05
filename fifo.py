import simpy
import random
import matplotlib
import matplotlib.pyplot as plt
import pygame
import time

# Set default font properties for the graphs
plt.rc('font', family='Times New Roman', size=15)
matplotlib.use('Agg')  # Use Agg backend to avoid Tkinter issues

# Pygame settings
pygame.init()
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (255, 255, 255)
NODE_COLOR = (0, 102, 204)
SWITCH_COLOR = (0, 153, 0)
PACKET_COLOR = (0, 0, 0)
DROPPED_PACKET_COLOR = (255, 0, 0)
LINE_COLOR = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Packet Switch Network Simulation")
font = pygame.font.SysFont('Times New Roman', 20)

# Positions for nodes and switches
NODE_POSITIONS = [(100, 100), (100, 200), (100, 300), (100, 400)]
SWITCH_POSITIONS = [(400, 150), (400, 350)]

class Packet:
    def __init__(self, packet_id, size, arrival_time, from_node, to_switch):
        self.packet_id = packet_id
        self.size = size
        self.arrival_time = arrival_time
        self.from_node = from_node
        self.to_switch = to_switch
        self.color = PACKET_COLOR

class Node:
    def __init__(self, env, node_id, switches):
        self.env = env
        self.node_id = node_id
        self.switches = switches
        self.action = env.process(self.run())
        self.position = NODE_POSITIONS[node_id - 1]

    def generate_packet(self):
        packet_size = random.randint(100, 1200)
        packet_id = f"Node{self.node_id}_Packet{int(self.env.now)}"
        chosen_switch = random.choice(self.switches)
        return Packet(packet_id, packet_size, self.env.now, self.position, chosen_switch)

    def run(self):
        while True:
            yield self.env.timeout(random.uniform(0.01, 0.1))
            packet = self.generate_packet()
            draw_packet(packet, moving=True)
            packet.to_switch.enqueue_packet(packet)

class Switch:
    def __init__(self, env, switch_id, max_queue_size):
        self.env = env
        self.switch_id = switch_id
        self.max_queue_size = max_queue_size
        self.queue = []
        self.dropped_packets = 0
        self.action = env.process(self.run())
        self.position = SWITCH_POSITIONS[switch_id - 1]

    def enqueue_packet(self, packet):
        if len(self.queue) < self.max_queue_size:
            self.queue.append(packet)
        else:
            packet.color = DROPPED_PACKET_COLOR
            self.dropped_packets += 1
            draw_packet(packet, moving=False, dropped=True)

    def process_packet(self):
        if self.queue:
            return self.queue.pop(0)
        return None

    def run(self):
        while True:
            yield self.env.timeout(0.2)
            if self.queue:
                packet = self.process_packet()
                if packet:
                    draw_packet(packet, moving=False)

def draw_network(nodes, switches):
    """Draws the network topology including nodes, switches, and connections."""
    screen.fill(BACKGROUND_COLOR)
    for node in nodes:
        pygame.draw.circle(screen, NODE_COLOR, node.position, 20)
        text = font.render(f"Node {node.node_id}", True, (0, 0, 0))
        screen.blit(text, (node.position[0] - 20, node.position[1] - 30))
    for switch in switches:
        pygame.draw.rect(screen, SWITCH_COLOR, (switch.position[0] - 30, switch.position[1] - 30, 60, 60))
        text = font.render(f"Switch {switch.switch_id}", True, (0, 0, 0))
        screen.blit(text, (switch.position[0] - 30, switch.position[1] - 50))
    for node in nodes:
        for switch in switches:
            pygame.draw.line(screen, LINE_COLOR, node.position, switch.position, 1)
    pygame.display.flip()

def draw_packet(packet, moving=False, dropped=False):
    """Handles the visualization of packet movement and drop events."""
    color = DROPPED_PACKET_COLOR if dropped else PACKET_COLOR
    if moving:
        start_pos = packet.from_node
        end_pos = packet.to_switch.position
        for i in range(20):
            x = int(start_pos[0] + (end_pos[0] - start_pos[0]) * (i / 20))
            y = int(start_pos[1] + (end_pos[1] - start_pos[1]) * (i / 20))
            screen.fill(BACKGROUND_COLOR)
            draw_network(nodes, switches)
            pygame.draw.circle(screen, color, (x, y), 5)
            pygame.display.flip()
            time.sleep(0.01)
    else:
        pygame.draw.circle(screen, color, (packet.to_switch.position[0] + random.randint(-10, 10), packet.to_switch.position[1] + random.randint(-10, 10)), 5)
        pygame.display.flip()
        time.sleep(0.05)

def monitor(env, switch1, switch2, metrics):
    """Monitors the state of the simulation and records relevant metrics."""
    while True:
        yield env.timeout(0.1)
        metrics['time_steps'].append(env.now)
        metrics['queue_length_sw1'].append(len(switch1.queue))
        metrics['queue_length_sw2'].append(len(switch2.queue))
        metrics['dropped_packets_sw1'].append(switch1.dropped_packets)
        metrics['dropped_packets_sw2'].append(switch2.dropped_packets)

def simulate_traffic():
    """Simulates network traffic and runs the Pygame visualization."""
    env = simpy.Environment()
    metrics = {
        'time_steps': [],
        'queue_length_sw1': [],
        'queue_length_sw2': [],
        'dropped_packets_sw1': [],
        'dropped_packets_sw2': []
    }

    switch1 = Switch(env, switch_id=1, max_queue_size=10)
    switch2 = Switch(env, switch_id=2, max_queue_size=10)

    global nodes, switches
    nodes = [Node(env, node_id=i, switches=[switch1, switch2]) for i in range(1, 5)]
    switches = [switch1, switch2]

    env.process(monitor(env, switch1, switch2, metrics))

    draw_network(nodes, switches)

    start_time = time.time()
    while time.time() - start_time < 30:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return metrics
        env.step()
        draw_network(nodes, switches)

    return metrics

def plot_results(metrics):
    """Generates plots for the simulation results."""
    plt.figure()
    plt.plot(metrics['time_steps'], metrics['dropped_packets_sw1'], label="SW1 Drops", linestyle='-')
    plt.plot(metrics['time_steps'], metrics['dropped_packets_sw2'], label="SW2 Drops", linestyle='-')
    plt.xlabel("Time (simulation units)")
    plt.ylabel("Packet Drops")
    plt.title("Packet Drops Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig("updated_packet_drops_over_time_simpy.png")
    plt.close()

    plt.figure()
    plt.plot(metrics['time_steps'], metrics['queue_length_sw1'], label="SW1 Queue Length", linestyle='-')
    plt.plot(metrics['time_steps'], metrics['queue_length_sw2'], label="SW2 Queue Length", linestyle='-')
    plt.xlabel("Time (simulation units)")
    plt.ylabel("Queue Length")
    plt.title("Queue Length Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig("updated_queue_length_over_time_simpy.png")
    plt.close()

if __name__ == "__main__":
    metrics = simulate_traffic()
    plot_results(metrics)
    print(f"Total Packets Dropped at SW1: {metrics['dropped_packets_sw1'][-1]}")
    print(f"Total Packets Dropped at SW2: {metrics['dropped_packets_sw2'][-1]}")
    print(f"Max Queue Length SW1: {max(metrics['queue_length_sw1'])}")
    print(f"Max Queue Length SW2: {max(metrics['queue_length_sw2'])}")

    pygame.quit()
