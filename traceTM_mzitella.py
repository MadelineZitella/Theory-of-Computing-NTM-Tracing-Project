# TOC Project 2 NTM Tracer | Madeline Zitella 
import csv 
import sys
from typing import List, Tuple, Dict, Set
from collections import defaultdict

class NTM_trace: 
    def __init__(self, NTM_file: str):
        self.transitions = {}
        self.start_state = ""
        self.accept_state = ""
        self.reject_state = "qreject"
        self.parse_ntm(NTM_file)
        
    def parse_ntm(self, filename: str): 
        with open(filename) as f:
            reader = csv.reader(f)
            self.name = next(reader)[0] # Line 1: Name 
            # parse header
            next(reader)  # Line 2: States
            next(reader)  # Line 3: Input alphabet
            next(reader)  # Line 4: Tape alphabet
            self.start_state = next(reader)[0]  # Line 5: Start state
            self.accept_state = next(reader)[0]  # Line 6: Accept state
            self.reject_state = next(reader)[0]  # Line 7: Reject state
        
            for line in reader: 
                if len(line) < 5: 
                    continue
                # name of current state, character from input alphabet, new state, new symbol, direction (R or L)
                curr_state, symbol, new_state, new_symbol, direction = line
                
                # if current state is not already in transitions dictionary..
                if curr_state not in self.transitions:
                    #..create new dict for this state 
                    self.transitions[curr_state] = defaultdict(list)
                
                # add transition details 
                self.transitions[curr_state][symbol].append((new_state, new_symbol, direction))
                
    def get_next_configs(self, config: Tuple[str, str, str]) -> List[Tuple[str, str, str]]:
        """Get all possible next configurations from current configuration."""
        left, state, right = config
        if not right:
            right = "_"  # add blank if at end of tape
            
        if state == self.accept_state or state == self.reject_state:
            return []
            
        curr_symbol = right[0]
        next_configs = []
        
        # Get all possible transitions for current state and symbol
        if state in self.transitions and curr_symbol in self.transitions[state]:
            for new_state, new_symbol, direction in self.transitions[state][curr_symbol]:
                if direction == "R":
                    new_left = left + new_symbol
                    new_right = right[1:] if len(right) > 1 else "_"
                else:  # direction == "L"
                    new_left = left[:-1] if left else ""
                    new_right = new_symbol + right[1:]
                next_configs.append((new_left, new_state, new_right))
        else:
            # No transition defined, go to reject state
            next_configs.append((left, self.reject_state, right))
            
        return next_configs
    
    
     #Use BFS to trace all possible  paths of the NTM
    def trace(self, input_str: str, max_depth: int = 100) -> Tuple[str, int, float, List, List[List]]:
            # Initialize with start configuration
            config_tree = [[("", self.start_state, input_str)]]
            total_transitions = 0
            nonleaf_configs = 0
            
            for depth in range(max_depth):
                current_level = config_tree[-1]
                next_level = []
                transitions_this_level = 0
                
                for config in current_level:
                    # Skip if we're in accept/reject state
                    if config[1] in [self.accept_state, self.reject_state]:
                        continue
                        
                    next_configs = self.get_next_configs(config)
                    transitions_this_level += len(next_configs)
                    
                    # Count this config if it generated transitions
                    if next_configs:
                        nonleaf_configs += 1
                    
                    for next_config in next_configs:
                        next_level.append(next_config)
                        if next_config[1] == self.accept_state:
                            # found shortest path 
                            path = self.extract_accepting_path(config_tree + [[next_config]], next_config)
                            nondeterminism = total_transitions / nonleaf_configs if nonleaf_configs > 0 else 1.0
                            # need to add the final level 
                            if next_level:
                                config_tree.append(next_level)
                            return "accept", len(path) - 1, nondeterminism, path, config_tree
                
                if not next_level:
                    # case that all paths are rejected 
                    nondeterminism = total_transitions / nonleaf_configs if nonleaf_configs > 0 else 1.0
                    return "reject", depth, nondeterminism, [], config_tree
                
                total_transitions += transitions_this_level
                config_tree.append(next_level)
            
            # calculate non-determinism 
            nondeterminism = total_transitions / nonleaf_configs if nonleaf_configs > 0 else 1.0
            return "timeout", max_depth, nondeterminism, [], config_tree


    # Get the complete path of configurations that led to acceptance
    def extract_accepting_path(self, config_tree: List[List], final_config: Tuple) -> List[Tuple[str, str, str]]:
        path = [final_config]
        current = final_config
        
        # go through each level of the tree 
        for level in reversed(config_tree):
            for config in level:
                next_configs = self.get_next_configs(config)
                if current in next_configs:
                    path.append(config)
                    current = config
                    break
        
        # traverse from start ---> to accept 
        path = list(reversed(path))
        return path
    
    
def main():
    if len(sys.argv) != 3:
        print("Usage: python traceNTM_mzitella.py <tm_file> <input_string>")
        sys.exit(1)
        
    tm_file = sys.argv[1]
    input_str = sys.argv[2]
    
    tracer = NTM_trace(tm_file)
    result, steps, nondeterminism, path, config_tree = tracer.trace(input_str)
    
    # Required initial output
    print(f"Machine: {tracer.name}")
    print(f"Input: {input_str}")
    
    # Calculate total transitions
    total_transitions = 0
    total_configs = 0
    for level in config_tree:
        total_transitions += len(level)
        total_configs += len(level) 
    
    # Print tree depth and total transitions
    tree_depth = len(config_tree) - 1
    print(f"Depth of configuration tree: {tree_depth}")
    print(f"Total transitions simulated: {total_transitions}")
    print(f"Total configurations explored: {total_configs}")
    print(f"Degree of nondeterminism: {nondeterminism:.2f}")
    
    
    if result == "accept":
        print(f"String accepted in {steps} transitions")
    elif result == "reject":
        print(f"String rejected in {steps} transitions")
    else:
        print(f"Execution stopped after {steps}")
        
    print("\nConfiguration Tree:")
    for i, level in enumerate(config_tree):
        print(f"Depth {i}:")
        for config in level:
            left, state, right = config
            print(f"[{left}], [{state}], [{right}]")
        print()

if __name__ == "__main__":
    main()
