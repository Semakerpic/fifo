import random 
import time 
import matplotlib 
import pandas as pd 
matplotlib.use('Agg')  # Use Agg backend to avoid Tkinter issues 
import matplotlib.pyplot as plt 
 
class Packet: 
    def __init__(self, packet_id, size, arrival_time): 
        self.packet_id = packet_id 
        self.size = size  # In bytes 
        self.arrival_time = arrival_time 
 
class Node: 
    def __init__(self, node_id): 
        self.node_id = node_id 
 
    def generate_packet(self): 
        packet_size = random.randint(64, 1500)  # Random packet size between 64 and 1500 bytes 
        return Packet(packet_id=f"Node{self.node_id}_Packet{int(time.time()*1000)}", 
                      size=packet_size, 
                      arrival_time=time.time()) 
 
class Switch: 
    def __init__(self, switch_id, max_queue_size): 
        self.switch_id = switch_id 
        self.queue = [] 
        self.max_queue_size = max_queue_size 
        self.dropped_packets = 0 
 
    def enqueue_packet(self, packet): 
        if len(self.queue) < self.max_queue_size: 
            self.queue.append(packet) 
        else: 
            self.dropped_packets += 1 
 
    def process_packet(self): 
        if self.queue: 
            packet = self.queue.pop(0)  # FIFO: first packet in the queue is processed first 
            return packet 
        return None 
 
    def has_space(self): 
        return len(self.queue) < self.max_queue_size 
 
    def queue_length(self): 
        return len(self.queue) 
 
def simulate_traffic(): 
    nodes = [Node(node_id=i) for i in range(1, 5)] 
    switch1 = Switch(switch_id=1, max_queue_size=50) 
    switch2 = Switch(switch_id=2, max_queue_size=50) 
 
    start_time = time.time() 
    simulation_duration = 10  # Simulate for 10 seconds 
    packet_latency = [] 
    dropped_packets_total = 0 
 
    # Lists to track packet drops and queue lengths over time 
    dropped_packets_sw1 = [] 
    dropped_packets_sw2 = [] 
    queue_length_sw1 = [] 
    queue_length_sw2 = [] 
    time_steps = [] 
 
    while time.time() - start_time < simulation_duration: 
        # Variable sleep time to simulate packet bursts or slowdowns 
        sleep_time = random.uniform(0.02, 0.1)  # Sleep between 20ms and 100ms 
        time.sleep(sleep_time) 
 
        # Generate packets from all nodes 
        for node in nodes: 
            packet = node.generate_packet() 
            if switch1.has_space(): 
                switch1.enqueue_packet(packet) 
            elif switch2.has_space(): 
                switch2.enqueue_packet(packet) 
            else: 
                # Both switch 1 and switch 2 are full, drop the packet randomly between the two 
                if random.choice([True, False]): 
                    switch1.dropped_packets += 1 
                else: 
                    switch2.dropped_packets += 1 
 
        # Log the packet drops and queue lengths at this time step 
        dropped_packets_sw1.append(switch1.dropped_packets) 
        dropped_packets_sw2.append(switch2.dropped_packets) 
        queue_length_sw1.append(switch1.queue_length())  # Track queue length of switch 1 
        queue_length_sw2.append(switch2.queue_length())  # Track queue length of switch 2 
        time_steps.append(time.time() - start_time) 
 
        # Process packets at switch 1 and forward to switch 2 if there's space 
        packet_from_switch1 = switch1.process_packet() 
        if packet_from_switch1: 
            if switch2.has_space(): 
                packet_latency.append(time.time() - packet_from_switch1.arrival_time) 
                switch2.enqueue_packet(packet_from_switch1) 
            else: 
                switch1.enqueue_packet(packet_from_switch1) 
 
        # Process packets at switch 2 (final destination) 
        switch2.process_packet() 
 
    # Report statistics 
    print(f"Packets dropped at switch 1: {switch1.dropped_packets}") 
    print(f"Packets dropped at switch 2: {switch2.dropped_packets}") 
    dropped_packets_total = switch1.dropped_packets + switch2.dropped_packets 
    print(f"Total packets dropped: {dropped_packets_total}") 
 
    if packet_latency: 
        avg_latency = sum(packet_latency) / len(packet_latency) 
        print(f"Average latency: {avg_latency:.4f} seconds") 
    else: 
        print("No packets processed.") 
 
    return dropped_packets_sw1, dropped_packets_sw2, queue_length_sw1, queue_length_sw2, time_steps 
 
def plot_results(dropped_sw1, dropped_sw2, queue_len_sw1, queue_len_sw2, time_steps): 
    # Plot the packet drops for both switches over time 
    plt.figure() 
    plt.plot(time_steps, dropped_sw1, label="SW1 Drops", linestyle='-', color='blue')  # Solid line for SW1 
    plt.plot(time_steps, dropped_sw2, label="SW2 Drops", linestyle='--', color='orange')  # Dashed line for SW2 
    plt.xlabel("Time (seconds)") 
    plt.ylabel("Packet Drops") 
    plt.title("Packet Drops Over Time") 
    plt.legend() 
    plt.savefig("packet_drops_over_time.png")  # Save plot instead of showing it 
    plt.close() 
    print("Packet drops plot saved as 'packet_drops_over_time.png'.") 
 
    # Plot the queue length for both switches over time 
    plt.figure() 
    plt.plot(time_steps, queue_len_sw1, label="SW1 Queue Length", linestyle='-', color='green')  # Solid line for SW1 
    plt.plot(time_steps, queue_len_sw2, label="SW2 Queue Length", linestyle='--', color='red')  # Dashed line for SW2 
    plt.xlabel("Time (seconds)") 
    plt.ylabel("Queue Length") 
    plt.title("Queue Length Over Time") 
    plt.legend() 
    plt.savefig("queue_length_over_time.png")  # Save plot instead of showing it 
    plt.close() 
    print("Queue length plot saved as 'queue_length_over_time.png'.") 
 
if __name__ == "__main__": 
    dropped_sw1, dropped_sw2, queue_len_sw1, queue_len_sw2, time_steps = simulate_traffic()  # Get the data over time 
    plot_results(dropped_sw1, dropped_sw2, queue_len_sw1, queue_len_sw2, time_steps)  # Plot the results          
 
