#!/usr/bin/env python3
"""
COSC 364 - Internet Technologies and Engineering
RIP Protocol Implementation
Based on RFC 2453 (RIP Version 2)

This program implements a RIP routing daemon that communicates with 
other instances through local UDP sockets. Each instance corresponds
to a router in a simulated network.

Execute with:
================================
python3 router.py <config_file>
================================
"""

import sys
import socket
import select
import time
import random
import struct
import threading
import re
import os


class RIPPacket:
    """Class to handle RIP packet creation and parsing"""
    
    # RIP constants
    HEADER_SIZE = 4
    RTE_SIZE = 20  # Route Table Entry size
    
    # RIP command values
    COMMAND_REQUEST = 1
    COMMAND_RESPONSE = 2
    
    # RIP version
    VERSION = 2
    
    # RIP constants
    INFINITY = 16
    
    @staticmethod
    def create_header(router_id, command=COMMAND_RESPONSE, version=VERSION):
        """
        Create a RIP packet header
        
        Parameters:
        router_id (int): ID of the sender router
        command (int): RIP command (1=request, 2=response)
        version (int): RIP version (should be 2)
        
        Returns:
        bytes: The header as bytes
        """
        # Pack header: command (1B), version (1B), router_id (2B)
        return struct.pack('!BBH', command, version, router_id)
    
    @staticmethod
    def create_rte(dest_id, metric):
        """
        Create a Route Table Entry (RTE)
        
        Parameters:
        dest_id (int): Destination router ID
        metric (int): Metric/cost to the destination
        
        Returns:
        bytes: The RTE as bytes
        """
        # In RIP, family identifier would be 2B, route tag 2B, IP address 4B,
        # subnet mask 4B, next hop 4B, metric 4B
        # Here we simplify and use: zeros (12B), dest_id (4B), metric (4B)
        return struct.pack('!12xII', dest_id, metric)
    
    @staticmethod
    def create_response(router_id, routes):
        """
        Create a complete RIP response packet
        
        Parameters:
        router_id (int): ID of the sender router
        routes (list): List of (dest_id, metric) tuples
        
        Returns:
        bytes: The complete packet as bytes
        """
        # Create header
        packet = RIPPacket.create_header(router_id)
        
        # Add each route table entry
        for dest_id, metric in routes:
            packet += RIPPacket.create_rte(dest_id, metric)
            
        return packet
    
    @staticmethod
    def parse(data):
        """
        Parse a RIP packet
        
        Parameters:
        data (bytes): The packet data
        
        Returns:
        tuple: (command, version, router_id, routes)
               where routes is a list of (dest_id, metric) tuples
        """
        if len(data) < RIPPacket.HEADER_SIZE:
            return None  # Packet too small
        
        # Parse header
        command, version, router_id = struct.unpack('!BBH', data[:RIPPacket.HEADER_SIZE])
        
        # Check version
        if version != RIPPacket.VERSION:
            return None  # Wrong version
        
        # Parse routes
        routes = []
        rte_count = (len(data) - RIPPacket.HEADER_SIZE) // RIPPacket.RTE_SIZE
        
        for i in range(rte_count):
            start = RIPPacket.HEADER_SIZE + i * RIPPacket.RTE_SIZE
            end = start + RIPPacket.RTE_SIZE
            
            # Extract destination and metric from RTE
            # Skip the first 12 bytes (would be address/netmask in real RIP)
            dest_id, metric = struct.unpack('!12xII', data[start:end])
            
            # Check metric range
            if 0 <= metric <= RIPPacket.INFINITY:
                routes.append((dest_id, metric))
        
        return (command, version, router_id, routes)


class Router:
    """Class representing a RIP router implementation"""
    
    def __init__(self, config_file):
        """
        Initialize the router with a configuration file
        
        Parameters:
        config_file (str): Path to the configuration file
        """
        # Router properties
        self.router_id = None
        self.input_ports = []
        self.outputs = []  # List of (port, metric, router_id) tuples
        
        # Routing table: {dest_id: (next_hop_id, metric, timestamp, garbage_collection)}
        # next_hop_id is the ID of the router to forward packets to
        # metric is the cost to reach the destination
        # timestamp is the last time the route was updated
        # garbage_collection is a flag indicating if route is in garbage collection
        self.routes = {}
        
        # Timers (in seconds)
        self.periodic_update_interval = 30  # Default: 30
        self.route_timeout = 180  # Default: 180
        self.garbage_collection_timeout = 120  # Default: 120
        
        # Sockets for communication
        self.sockets = []
        
        # Parse the configuration file
        self.parse_config(config_file)
        
        # Initialize routing table with directly connected routers
        for _, metric, neighbor_id in self.outputs:
            self.routes[neighbor_id] = (neighbor_id, metric, time.time(), False)
        
        # Add ourselves with metric 0
        self.routes[self.router_id] = (self.router_id, 0, float('inf'), False)
        
    def parse_config(self, config_file):
        """
        Parse the configuration file
        
        Parameters:
        config_file (str): Path to the configuration file
        
        Raises:
        ValueError: If the configuration file is invalid
        """
        if not os.path.exists(config_file):
            print(f"Error: Configuration file '{config_file}' not found.")
            sys.exit(1)
            
        try:
            with open(config_file, 'r') as f:
                lines = [line.strip() for line in f.readlines()]
            
            router_id_found = False
            input_ports_found = False
            outputs_found = False
            
            for line in lines:
                # Skip comments and empty lines
                if line.startswith('#') or not line:
                    continue
                
                # Parse router-id
                if line.startswith('router-id'):
                    parts = line.split()
                    if len(parts) != 2:
                        raise ValueError("Invalid router-id format")
                    
                    router_id = int(parts[1])
                    if not (1 <= router_id <= 64000):
                        raise ValueError("Router ID must be between 1 and 64000")
                    
                    self.router_id = router_id
                    router_id_found = True
                
                # Parse input-ports
                elif line.startswith('input-ports'):
                    parts = line[len('input-ports'):].strip()
                    if not parts:
                        raise ValueError("No input ports specified")
                    
                    # Split by commas and strip whitespace
                    port_strs = [p.strip() for p in parts.split(',')]
                    
                    for port_str in port_strs:
                        port = int(port_str)
                        if not (1024 <= port <= 64000):
                            raise ValueError(f"Port number {port} must be between 1024 and 64000")
                        if port in self.input_ports:
                            raise ValueError(f"Duplicate input port: {port}")
                        
                        self.input_ports.append(port)
                    
                    input_ports_found = True
                
                # Parse outputs
                elif line.startswith('outputs'):
                    parts = line[len('outputs'):].strip()
                    if not parts:
                        raise ValueError("No outputs specified")
                    
                    # Split by commas and strip whitespace
                    output_strs = [o.strip() for o in parts.split(',')]
                    
                    for output_str in output_strs:
                        match = re.match(r'(\d+)-(\d+)-(\d+)', output_str)
                        if not match:
                            raise ValueError(f"Invalid output format: {output_str}")
                        
                        port, metric, router_id = map(int, match.groups())
                        
                        if not (1024 <= port <= 64000):
                            raise ValueError(f"Output port {port} must be between 1024 and 64000")
                        if not (1 <= metric <= 15):
                            raise ValueError(f"Metric {metric} must be between 1 and 15")
                        if not (1 <= router_id <= 64000):
                            raise ValueError(f"Router ID {router_id} must be between 1 and 64000")
                        if port in self.input_ports:
                            raise ValueError(f"Output port {port} cannot be an input port")
                        
                        self.outputs.append((port, metric, router_id))
                    
                    outputs_found = True
                
                # Parse timers
                elif line.startswith('periodic-update-time'):
                    self.periodic_update_interval = int(line.split()[1])
                
                elif line.startswith('route-timeout'):
                    self.route_timeout = int(line.split()[1])
                
                elif line.startswith('garbage-collection-timeout'):
                    self.garbage_collection_timeout = int(line.split()[1])
            
            # Check if required parameters are present
            if not router_id_found:
                raise ValueError("router-id parameter missing")
            if not input_ports_found:
                raise ValueError("input-ports parameter missing")
            if not outputs_found:
                raise ValueError("outputs parameter missing")
                
        except Exception as e:
            print(f"Error parsing configuration file: {e}")
            sys.exit(1)
    
    def setup_sockets(self):
        """
        Set up UDP sockets for all input ports
        
        Returns:
        bool: True if successful, False otherwise
        """
        try:
            for port in self.input_ports:
                # Create UDP socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                
                # Allow reuse of address
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                # Bind to port
                sock.bind(('127.0.0.1', port))
                
                # Add to list of sockets
                self.sockets.append(sock)
            
            return True
        except Exception as e:
            print(f"Error setting up sockets: {e}")
            return False
    
    def get_routing_table(self):
        """
        Get the current routing table
        
        Returns:
        list: List of (dest_id, next_hop_id, metric, age, garbage) tuples
        """
        now = time.time()
        table = []
        
        for dest_id, (next_hop_id, metric, timestamp, garbage) in self.routes.items():
            age = int(now - timestamp)
            table.append((dest_id, next_hop_id, metric, age, garbage))
        
        return sorted(table, key=lambda x: x[0])  # Sort by destination ID
    
    def print_routing_table(self):
        """Print the current routing table"""
        table = self.get_routing_table()
        
        print("\n" + "=" * 70)
        print(f"Routing table for Router {self.router_id}")
        print("=" * 70)
        print(f"{'Destination':<12} {'Next Hop':<12} {'Metric':<8} {'Age (s)':<8} {'Garbage'}")
        print("-" * 70)
        
        for dest_id, next_hop_id, metric, age, garbage in table:
            garbage_str = "Yes" if garbage else "No"
            
            # Mark routes with infinity metric
            if metric == RIPPacket.INFINITY:
                metric_str = "∞"
            else:
                metric_str = str(metric)
                
            print(f"{dest_id:<12} {next_hop_id:<12} {metric_str:<8} {age:<8} {garbage_str}")
        
        print("=" * 70 + "\n")
    
    def send_updates(self, triggered=False):
        """
        Send routing updates to all neighbors
        
        Parameters:
        triggered (bool): Whether this is a triggered update
        """
        for out_port, out_metric, neighbor_id in self.outputs:
            # Create a copy of routes for split horizon with poisoned reverse
            routes_to_send = []
            
            for dest_id, (next_hop_id, metric, _, _) in self.routes.items():
                # Skip routes that go through this neighbor (split horizon)
                # or poison them by setting metric to INFINITY (poisoned reverse)
                if next_hop_id == neighbor_id:
                    # Poisoned reverse: advertise with INFINITY metric
                    routes_to_send.append((dest_id, RIPPacket.INFINITY))
                else:
                    # Normal route
                    routes_to_send.append((dest_id, metric))
            
            # Create the packet
            packet = RIPPacket.create_response(self.router_id, routes_to_send)
            
            # Send the packet
            try:
                # Use the first socket to send
                self.sockets[0].sendto(packet, ('127.0.0.1', out_port))
                
                if not triggered:
                    print(f"Sent periodic update to neighbor {neighbor_id} (port {out_port})")
                else:
                    print(f"Sent triggered update to neighbor {neighbor_id} (port {out_port})")
            except Exception as e:
                print(f"Error sending update to neighbor {neighbor_id}: {e}")
    
    def process_update(self, router_id, routes):
        """
        Process a routing update from a neighbor
        
        Parameters:
        router_id (int): ID of the sending router
        routes (list): List of (dest_id, metric) tuples
        
        Returns:
        bool: True if the routing table was modified, False otherwise
        """
        # Find the output entry for this neighbor
        neighbor_entry = None
        for port, metric, n_id in self.outputs:
            if n_id == router_id:
                neighbor_entry = (port, metric, n_id)
                break
        
        if not neighbor_entry:
            print(f"Received update from unknown neighbor {router_id}, ignoring")
            return False
        
        # Extract the base metric to this neighbor
        _, base_metric, _ = neighbor_entry
        
        # Flag to indicate if the routing table was modified
        table_modified = False
        
        # Current time
        now = time.time()
        
        # Process each route
        for dest_id, metric in routes:
            # Skip if destination is ourselves
            if dest_id == self.router_id:
                continue
            
            # Calculate new metric (neighbor metric + cost to neighbor)
            new_metric = min(base_metric + metric, RIPPacket.INFINITY)
            
            # Check if we already have a route to this destination
            if dest_id in self.routes:
                current_next_hop, current_metric, timestamp, garbage = self.routes[dest_id]
                
                # If the route is from the same neighbor
                if current_next_hop == router_id:
                    # Always update the route if it's from the same neighbor
                    if new_metric != current_metric:
                        if new_metric >= RIPPacket.INFINITY and current_metric < RIPPacket.INFINITY:
                            # Route became invalid, set garbage collection
                            self.routes[dest_id] = (router_id, RIPPacket.INFINITY, now, True)
                            table_modified = True
                            print(f"Route to {dest_id} via {router_id} became invalid, starting garbage collection")
                        else:
                            # Regular update
                            self.routes[dest_id] = (router_id, new_metric, now, garbage)
                            table_modified = True
                            print(f"Updated route to {dest_id} via {router_id} with metric {new_metric}")
                    else:
                        # Just refresh the timestamp
                        self.routes[dest_id] = (router_id, current_metric, now, garbage)
                
                # If we receive a better route
                elif new_metric < current_metric:
                    self.routes[dest_id] = (router_id, new_metric, now, False)
                    table_modified = True
                    print(f"Better route found to {dest_id} via {router_id} with metric {new_metric}")
            
            # If we don't have a route to this destination yet
            elif new_metric < RIPPacket.INFINITY:
                self.routes[dest_id] = (router_id, new_metric, now, False)
                table_modified = True
                print(f"New route added to {dest_id} via {router_id} with metric {new_metric}")
        
        return table_modified
    
    def check_timeouts(self):
        """
        Check for route timeouts and handle expired routes
        
        Returns:
        bool: True if the routing table was modified, False otherwise
        """
        now = time.time()
        table_modified = False
        
        for dest_id in list(self.routes.keys()):
            # Skip our own route
            if dest_id == self.router_id:
                continue
                
            next_hop, metric, timestamp, garbage = self.routes[dest_id]
            
            if garbage:
                # Route is in garbage collection
                if now - timestamp > self.garbage_collection_timeout:
                    # Garbage collection timeout expired, remove route
                    del self.routes[dest_id]
                    table_modified = True
                    print(f"Route to {dest_id} via {next_hop} removed after garbage collection")
            else:
                # Regular route
                if now - timestamp > self.route_timeout:
                    # Route timeout expired, mark as invalid and start garbage collection
                    self.routes[dest_id] = (next_hop, RIPPacket.INFINITY, now, True)
                    table_modified = True
                    print(f"Route to {dest_id} via {next_hop} timeout expired, starting garbage collection")
        
        return table_modified
    
    def run(self):
        """Main router loop"""
        if not self.setup_sockets():
            return
        
        print(f"Router {self.router_id} starting...")
        self.print_routing_table()
        
        # Send initial updates
        self.send_updates()
        
        # Set up timer for periodic updates
        last_periodic_update = time.time()
        
        try:
            while True:
                # Calculate timeout for select() call
                now = time.time()
                time_since_last_update = now - last_periodic_update
                next_update_in = max(0.1, self.periodic_update_interval - time_since_last_update)
                
                # Wait for incoming packets or timeout
                readable, _, _ = select.select(self.sockets, [], [], next_update_in)
                
                table_modified = False
                
                # Handle incoming packets
                for sock in readable:
                    try:
                        data, addr = sock.recvfrom(2048)
                        parsed = RIPPacket.parse(data)
                        
                        if parsed:
                            command, version, router_id, routes = parsed
                            
                            if command == RIPPacket.COMMAND_RESPONSE:
                                print(f"Received update from Router {router_id}")
                                table_modified |= self.process_update(router_id, routes)
                    except Exception as e:
                        print(f"Error handling incoming packet: {e}")
                
                # Check for route timeouts
                table_modified |= self.check_timeouts()
                
                # Print the routing table if it was modified
                if table_modified:
                    self.print_routing_table()
                    # Send triggered updates if needed
                    self.send_updates(triggered=True)
                
                # Check if it's time for a periodic update
                now = time.time()
                if now - last_periodic_update >= self.periodic_update_interval:
                    # Add some randomness to avoid synchronization issues
                    jitter = random.uniform(-0.1, 0.1) * self.periodic_update_interval
                    last_periodic_update = now + jitter
                    
                    # Send periodic updates
                    self.send_updates()
                    
                    # Print the routing table
                    self.print_routing_table()
                    
        except KeyboardInterrupt:
            print(f"\nRouter {self.router_id} shutting down...")
        finally:
            # Close all sockets
            for sock in self.sockets:
                sock.close()


def main():
    """Main function to start the router"""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    router = Router(config_file)
    router.run()


if __name__ == "__main__":
    main()
