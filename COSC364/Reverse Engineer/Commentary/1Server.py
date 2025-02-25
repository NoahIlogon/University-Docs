"""
    SERVER.PY

    This file creates a Router class, responsible for running all of the
    operations of a router once we have obtained the information about
    the Router's setup from the config files.

    The Router class deals with all matters of receiving and sending
    datagrams and updating the Routing Table.
"""

from socket import *
import select
import time  # Required for timer operations

from timer import Timer
from packets import *
from forwarding_table import *

# Constants used throughout the implementation
BUFSIZE = 4096         # Buffer size for receiving packets
BLOCKING_TIME = 0.1    # Maximum blocking time when waiting for packets
INFINITY = 16          # Value representing an unreachable route (standard for RIP)

class Router:
    
    def __init__(self, router_id, inputs, outputs, timer_value):
        """
        Initializes the Router with configuration parameters.
        
        Args:
            router_id: Unique identifier for this router
            inputs: List of port numbers to listen on
            outputs: List of OutputInterface objects with peer router information
            timer_value: Base timer value in seconds for periodic operations
        """
        # Store basic router identity and configuration
        self.id = router_id
        self.inputs = inputs          # Ports to listen for incoming packets
        self.outputs = outputs        # Information about connected peers
        self.timer_value = timer_value  # Base value for timer calculations
        
        # Calculate timeouts based on the timer value
        self.timeout_time = timer_value * 6  # Routes timeout after 6x the timer value
        self.garbage_time = timer_value * 4  # Garbage collection after 4x the timer value

        # Initialize an empty routing table (dictionary where keys are destination IDs)
        self.routing_table = {}

        # Initialize timer reference (will be set in main())
        self.timer = None
        
        # Flag to indicate if a triggered update is needed
        self.triggered_update_call = False

        # Set up the UDP sockets for receiving datagrams
        self.sockets = self.setup_sockets()


    def setup_sockets(self):
        """
        Creates and configures UDP sockets for all input ports.
        
        Returns:
            Dictionary mapping port numbers to configured socket objects
        """
        # Dictionary to store sockets indexed by their port numbers
        sockets = {}
        
        # For each input port specified in the configuration
        for port in self.inputs:
            # Create a UDP socket (SOCK_DGRAM)
            s = socket(AF_INET, SOCK_DGRAM)
            
            # Bind to the loopback interface (127.0.0.1) and the specified port
            s.bind(('127.0.0.1', port))
            
            # Store the socket in the dictionary
            sockets[port] = s
            
        return sockets

    
    def resolve_update(self, data):
        """
        Processes received routing update packets and updates the routing table.
        
        Args:
            data: Binary data packet received from another router
        """
        # Decode the packet to extract the source router ID and table entries
        src_id, table_entries = decode_packet(data)

        # Process each routing table entry received from the neighbor
        for entry in table_entries:
            # Skip entries about routing to this router itself
            if entry.dst_id != self.id:

                # Calculate the total cost by adding the link cost to the advertised metric
                for output in self.outputs:
                    if output.peer_id == src_id:
                        link_cost = output.link_cost
                        # Cap the total cost at INFINITY to prevent count-to-infinity
                        entry.metric = min(entry.metric + link_cost, INFINITY)
                
                # CASE 1: Path to a new destination not in our routing table
                if entry.dst_id not in self.routing_table:
                    if entry.metric != INFINITY:  # Only add valid routes
                        entry.changed_flag = True  # Mark as changed to trigger updates
                        entry.init_timeout()      # Initialize the timeout timer
                        self.routing_table[entry.dst_id] = entry  # Add to routing table

                # CASE 2: Route replacement for a destination already marked for deletion 
                elif self.routing_table[entry.dst_id].garbage_flag is True and entry.metric < INFINITY:
                    entry.changed_flag = True     # Mark as changed to trigger updates
                    entry.init_timeout()          # Initialize the timeout timer
                    self.routing_table[entry.dst_id] = entry  # Replace the route

                # CASE 3: Equal-cost route management 
                elif entry.metric == self.routing_table[entry.dst_id].metric:
                    
                    # If it's the same next hop, just refresh the timeout
                    if entry.next_hop == self.routing_table[entry.dst_id].next_hop:
                        self.routing_table[entry.dst_id].init_timeout()
                        
                    # If it's a different next hop but our current route is aging,
                    # replace it with the fresh one (route refresh strategy)
                    elif time.time() >= self.routing_table[entry.dst_id].timeout + (self.timeout_time / 2):
                        entry.changed_flag = True
                        entry.init_timeout()
                        self.routing_table[entry.dst_id] = entry

                # CASE 4: Better route found or current route's metric has changed
                elif (self.routing_table[entry.dst_id].next_hop == src_id and entry.metric != self.routing_table[entry.dst_id].metric) or entry.metric < self.routing_table[entry.dst_id].metric:
                    entry.changed_flag = True
                    entry.init_timeout()
                    self.routing_table[entry.dst_id] = entry

                    # If the route has become unreachable, mark for garbage collection
                    if entry.metric == INFINITY:
                        self.routing_table[entry.dst_id].garbage_flag = True
                        self.routing_table[entry.dst_id].init_garbage()
                        self.triggered_update_call = True  # Schedule a triggered update
                
                
    def triggered_update(self):
        """
        Sends immediate updates to neighbors for routes that have changed.
        This helps speed up convergence when the network topology changes.
        """
        # Print the current state of the routing table for debugging
        print(f'Router {self.id} - Routing Table Update for Triggered Update at {time.strftime("%H:%M:%S", time.localtime())}')
        print("| Destination | Next Hop | Metric | Changed | Garbage |")
        for destination in sorted(self.routing_table.keys()):
            print(self.routing_table[destination])
        print(" "+"-"*53+"\n")
        
        # Collect all entries marked as changed
        table_entries = []
        for entry in self.routing_table.values():
                if entry.changed_flag == True:
                    table_entries.append(entry)
                    entry.changed_flag = False  # Reset the changed flag
                    
        # Only proceed if there are changed entries to report
        if len(table_entries) > 0:
            # Process updates for each neighbor
            for output in self.outputs:
                
                # Apply split horizon with poisoned reverse:
                # Report INFINITY metric for routes that use this neighbor as the next hop
                entries_sh_pr = []
                for entry in table_entries:
                    if entry.next_hop == output.peer_id:
                        # Poison the route - tell the neighbor it's unreachable through us
                        entries_sh_pr.append(RoutingTableEntry(entry.dst_id, entry.next_hop, INFINITY))
                    else:
                        # Include the route normally
                        entries_sh_pr.append(entry)

                
                # Encode and send the packets to this neighbor
                packets = encode_packet(self.id, entries_sh_pr)
                for packet in packets:
                    # Use the first socket (any socket would work as they're all UDP)
                    list(self.sockets.values())[0].sendto(packet, ('127.0.0.1', output.peer_port_no))

        # Reset the triggered update flag
        self.triggered_update_call = False


    def check_timeout(self):
        """
        Checks for routes that have timed out and marks them as invalid.
        """
        for entry in self.routing_table.values():
            # Only check entries not already marked for garbage collection
            if self.routing_table[entry.dst_id].garbage_flag == False:
                # If the route's timeout period has elapsed
                if time.time() >= self.routing_table[entry.dst_id].timeout + self.timeout_time:
                    # Initialize garbage collection timer
                    self.routing_table[entry.dst_id].init_garbage()
                    # Mark the route as unreachable and for garbage collection
                    self.routing_table[entry.dst_id].garbage_flag = True
                    self.routing_table[entry.dst_id].metric = INFINITY
                    # Flag the entry as changed to trigger updates
                    self.routing_table[entry.dst_id].changed_flag = True
                    # Schedule a triggered update
                    self.triggered_update_call = True


    def check_garbage(self):
        """
        Removes routes that have been in the garbage collection state
        for longer than the garbage_time period.
        """
        # List to collect entries that need to be removed
        remove_list = []

        # Check each entry in the routing table
        for entry in self.routing_table.values():
            # If the entry is marked for garbage collection
            if self.routing_table[entry.dst_id].garbage_flag == True:
                # And if the garbage collection timer has expired
                if time.time() >= self.routing_table[entry.dst_id].garbage_time + self.garbage_time:
                    # Add to the removal list
                    remove_list.append(entry.dst_id)
                    
        # Remove all expired entries from the routing table
        for remove_id in remove_list:
            del self.routing_table[remove_id]


    def periodic_update(self):
        """
        Sends the complete routing table to all neighbors at regular intervals.
        This is the standard mechanism to ensure routing information consistency.
        """
        # Print the current state of the routing table for debugging
        print(f'Router {self.id} - Routing Table Update for Periodic Update at {time.strftime("%H:%M:%S", time.localtime())}')
        print("| Destination | Next Hop | Metric | Changed | Garbage |")
        for destination in sorted(self.routing_table.keys()):
            print(self.routing_table[destination])
        print(" "+"-"*53+"\n")
        
        # Create a complete list of entries, including a route to self with 0 cost
        table_entries = [RoutingTableEntry(self.id, self.id, 0)]
        table_entries.extend(list(self.routing_table.values()))
        
        # Process each neighbor
        for output in self.outputs:

            # Apply split horizon with poisoned reverse:
            # Report INFINITY metric for routes that use this neighbor as the next hop
            entries_sh_pr = []
            for entry in table_entries:
                if entry.next_hop == output.peer_id:
                    # Poison the route - tell the neighbor it's unreachable through us
                    entries_sh_pr.append(RoutingTableEntry(entry.dst_id, entry.next_hop, INFINITY))
                else:
                    # Include the route normally
                    entries_sh_pr.append(entry)
            
            # Encode and send the packets to this neighbor
            packets = encode_packet(self.id, entries_sh_pr)
            for packet in packets:
                # Use the first socket (any socket would work as they're all UDP)
                list(self.sockets.values())[0].sendto(packet, ('127.0.0.1', output.peer_port_no))

        # Reset all changed flags after the periodic update
        for destination in self.routing_table:
            if self.routing_table[destination].changed_flag is True:
                self.routing_table[destination].changed_flag = False

        # No need for triggered update after sending everything in periodic update
        self.triggered_update_call = False


    def main(self):
        """
        Main router operation loop that continuously processes incoming updates
        and manages the routing table.
        """
        # Initialize the periodic update timer
        self.timer = Timer(self.timer_value, self.periodic_update)
        self.timer.start_timer()

        # Main loop - runs as long as sockets exist
        while list(self.sockets.values()):

            # Wait for incoming packets or until BLOCKING_TIME seconds have passed
            # select() returns lists of sockets that are ready for reading, writing, or have errors
            readable, writable, exceptional = select.select(list(self.sockets.values()), [], [], BLOCKING_TIME)

            # Process any received packets
            for s in readable:
                # Receive data and sender address from the socket
                data, address = s.recvfrom(BUFSIZE)
                if data:
                    # Process the received update packet
                    self.resolve_update(data)

            # Perform periodic maintenance tasks
            self.timer.update_timer()  # Update the periodic update timer
            self.check_timeout()       # Check for timed-out routes
            self.check_garbage()       # Remove expired garbage routes

            # Send triggered updates if needed and allowed by the timer
            if self.triggered_update_call and self.timer.triggered_update_allowed():
                self.triggered_update()
