import random
import time
import matplotlib
import pandas as pd
matplotlib.use('Agg')  # Use Agg backend to avoid Tkinter issues
import matplotlib.pyplot as plt

# Set default font properties for the graphs
plt.rc('font', family='Times New Roman', size=15)

class Packet:
    """
    Represents a network packet with a unique packet ID, size, and arrival time.
    """
    def __init__(self, packet_id, size, arrival_time):
        self.packet_id = packet_id
        self.size = size  # Size in bytes
        self.arrival_time = arrival_time

class Node:
    """
    Represents a network node capable of generating packets.
    """
    def __init__(self, node_id):
        self.node_id = node_id

    def generate_packet(self, min_size=100, max_size=1200):
        """
        Generates a packet with a random size between min_size and max_size.
        """
        packet_size = random.randint(min_size, max_size)
        return Packet(packet_id=f"Node{self.node_id}_Packet{int(time.time()*1000)}",
                      size=packet_size,
                      arrival_time=time.time())

class Switch:
    """
    Represents a network switch with a queue to manage packets.
    """
    def __init__(self, switch_id, max_queue_size):
        self.switch_id = switch_id
        self.queue = []
        self.max_queue_size = max_queue_size
        self.dropped_packets = 0

    def enqueue_packet(self, packet):
        """
        Enqueues a packet to the switch queue if there is space; otherwise, increments the dropped packet count.
        """
        if len(self.queue) < self.max_queue_size:
            self.queue.append(packet)
        else:
            self.dropped_packets += 1

    def process_packet(self):
        """
        Processes (removes) a packet from the front of the queue if available.
        """
        if self.queue:
            return self.queue.pop(0)
        return None

    def has_space(self):
        """
        Checks if there is space in the queue for more packets.
        """
        return len(self.queue) < self.max_queue_size

    def queue_length(self):
        """
        Returns the current length of the queue.
        """
        return len(self.queue)

def simulate_traffic():
    """
    Simulates network traffic involving multiple nodes and switches over a set duration.
    Returns packet drop data, queue lengths, and average latency.
    """
    nodes = [Node(node_id=i) for i in range(1, 5)]
    switch1 = Switch(switch_id=1, max_queue_size=50)
    switch2 = Switch(switch_id=2, max_queue_size=50)

    start_time = time.time()
    simulation_duration = 10
    packet_latency = []

    dropped_packets_sw1 = []
    dropped_packets_sw2 = []
    queue_length_sw1 = []
    queue_length_sw2 = []
    time_steps = []

    while time.time() - start_time < simulation_duration:
        time.sleep(random.uniform(0.02, 0.1))

        for node in nodes:
            packet = node.generate_packet()
            if random.choice([True, False]):
                if switch1.has_space():
                    switch1.enqueue_packet(packet)
                else:
                    switch1.dropped_packets += 1
            else:
                if switch2.has_space():
                    switch2.enqueue_packet(packet)
                else:
                    switch2.dropped_packets += 1

        dropped_packets_sw1.append(switch1.dropped_packets)
        dropped_packets_sw2.append(switch2.dropped_packets)
        queue_length_sw1.append(switch1.queue_length())
        queue_length_sw2.append(switch2.queue_length())
        time_steps.append(time.time() - start_time)

        packet_from_switch1 = switch1.process_packet()
        if packet_from_switch1:
            if switch2.has_space():
                packet_latency.append(time.time() - packet_from_switch1.arrival_time)
                switch2.enqueue_packet(packet_from_switch1)
            else:
                switch2.dropped_packets += 1

        switch2.process_packet()

    avg_latency = sum(packet_latency) / len(packet_latency) if packet_latency else 0

    return (dropped_packets_sw1, dropped_packets_sw2, queue_length_sw1, 
            queue_length_sw2, time_steps, avg_latency)

def plot_results(dropped_sw1, dropped_sw2, queue_len_sw1, queue_len_sw2, time_steps):
    """
    Plots the results of the simulation including packet drops and queue length over time.
    """
    plt.figure()
    plt.plot(time_steps, dropped_sw1, label="SW1 Drops", linestyle='-', color='blue')
    plt.plot(time_steps, dropped_sw2, label="SW2 Drops", linestyle='-', color='red')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Packet Drops")
    plt.title("Packet Drops Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig("packet_drops_over_time.png")
    plt.close()

    plt.figure()
    plt.plot(time_steps, queue_len_sw1, label="SW1 Queue Length", linestyle='-', color='blue')
    plt.plot(time_steps, queue_len_sw2, label="SW2 Queue Length", linestyle='-', color='red')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Queue Length")
    plt.title("Queue Length Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig("queue_length_over_time.png")
    plt.close()

if __name__ == "__main__":
    (dropped_sw1, dropped_sw2, queue_len_sw1, queue_len_sw2, 
     time_steps, avg_latency) = simulate_traffic()

    print(f"Average Latency: {avg_latency:.4f} seconds")
    print(f"Total Packets Dropped at SW1: {dropped_sw1[-1]}")
    print(f"Total Packets Dropped at SW2: {dropped_sw2[-1]}")

    plot_results(dropped_sw1, dropped_sw2, queue_len_sw1, queue_len_sw2, time_steps)
