"""
Module for logging digivolution trees in a hierarchical, readable format.
"""
from . import constants


class DigivolutionTreeLogger:
    """Formats and logs digivolution trees starting from root Digimon."""
    
    def __init__(self, logger, generated_evolutions, generated_conditions, pre_evos, base_digimon_info):
        self.logger = logger
        self.generated_evolutions = generated_evolutions
        self.generated_conditions = generated_conditions
        self.pre_evos = pre_evos
        self.base_digimon_info = base_digimon_info
        
        # Track which digimon have been logged to avoid duplicates
        self.logged_digimon = set()
    
    def find_root_digimon(self):
        """
        Find all digimon that are roots of evolution trees.
        These are digimon that either:
        - Have no pre-evolution, OR
        - Have a pre-evolution that doesn't exist in the generated_evolutions
        """
        roots = []
        
        # Check all digimon that have evolutions
        for digimon_id in self.generated_evolutions.keys():
            # If this digimon has no pre-evo, it's a root
            if digimon_id not in self.pre_evos:
                roots.append(digimon_id)
            # If this digimon's pre-evo wasn't randomized, it's also a root
            elif self.pre_evos[digimon_id] not in self.generated_evolutions:
                roots.append(digimon_id)
        
        # Sort by ID for consistent ordering
        roots.sort()
        return roots
    
    def build_tree_structure(self, root_id, visited=None):
        """
        Recursively build the tree structure starting from root_id.
        Returns a dict representing the tree.
        """
        if visited is None:
            visited = set()
        
        if root_id in visited:
            return None
        
        visited.add(root_id)
        
        tree = {
            'id': root_id,
            'name': constants.DIGIMON_ID_TO_STR.get(root_id, f"Unknown_{root_id}"),
            'children': []
        }
        
        # Add all evolutions as children
        if root_id in self.generated_evolutions:
            for evo_id in self.generated_evolutions[root_id]:
                child_tree = self.build_tree_structure(evo_id, visited)
                if child_tree:
                    tree['children'].append(child_tree)
        
        return tree
    
    def format_tree_chart(self, tree):
        """
        Format the tree structure into ASCII art with linear chains on same line.
        First branch continues on same line, subsequent branches get new lines.
        Returns a list of lines.
        """
        return self._format_node(tree, "", True)
    
    def _format_node(self, node, parent_indent, is_first_branch):
        """
        Recursively format a node and its children.
        """
        lines = []
        
        # Build linear chain from this node
        chain = self._build_linear_chain(node)
        chain_str = " -> ".join([n['name'] for n in chain])
        
        # Determine how to format this chain
        if parent_indent == "":
            # Root node - always starts at column 1
            lines.append(f" {chain_str}")
            base_indent = " " * (len(chain[0]['name']) + 2)
        elif is_first_branch:
            # First branch continues on same line
            lines.append(f" -> {chain_str}")
            base_indent = parent_indent + " " * (len(chain[0]['name']) + 4)
        else:
            # Subsequent branches start on new line with proper indent
            lines.append(f"{parent_indent}-> {chain_str}")
            base_indent = parent_indent + " " * (len(chain[0]['name']) + 3)
        
        # Process children of the last node in chain
        last_node = chain[-1]
        if last_node['children']:
            for i, child in enumerate(last_node['children']):
                if i == 0:
                    # First child - try to continue on same line
                    child_lines = self._format_node(child, base_indent, True)
                    # Append first child's first line to our last line
                    if lines and child_lines:
                        lines[-1] += child_lines[0]
                        lines.extend(child_lines[1:])
                else:
                    # Other children - start on new lines
                    child_lines = self._format_node(child, base_indent, False)
                    lines.extend(child_lines)
        
        return lines
    
    def _build_linear_chain(self, node):
        """
        Build a linear chain starting from node.
        A chain continues as long as each node has exactly one child.
        Returns a list of nodes in the chain.
        """
        chain = [node]
        current = node
        
        while len(current['children']) == 1:
            current = current['children'][0]
            chain.append(current)
        
        return chain
    
    def get_evolution_path_conditions(self, tree, parent_name=None):
        """
        Extract all evolution paths and their conditions.
        Returns a list of (from_name, to_name, conditions) tuples.
        """
        paths = []
        
        current_name = tree['name']
        current_id = tree['id']
        
        # If this isn't the root, add the evolution from parent to this node
        if parent_name is not None:
            conditions = self.generated_conditions.get(current_id, [])
            paths.append((parent_name, current_name, conditions))
        
        # Recursively get paths for children
        for child in tree['children']:
            child_paths = self.get_evolution_path_conditions(child, current_name)
            paths.extend(child_paths)
        
        return paths
    
    def format_conditions(self, conditions):
        """Format conditions as a string."""
        if not conditions:
            return ""
        
        condition_strs = []
        for cond_el in conditions:
            cond_id = cond_el[0]
            cond_value = cond_el[1]
            cond_name = constants.DIGIVOLUTION_CONDITIONS.get(cond_id, f"UNKNOWN_{cond_id}")
            
            # Handle special formatting cases
            if "FRIENDSHIP" in cond_name.upper() or "Friendship" in cond_name:
                # Add % sign for friendship
                condition_strs.append(f"{cond_name} {cond_value}%")
            elif cond_name.startswith("got ") or cond_name.startswith("GOT "):
                # Special case for "got X" conditions - just use the name as-is with value
                condition_strs.append(f"{cond_name}")
            else:
                condition_strs.append(f"{cond_name} {cond_value}")
        
        return ", ".join(condition_strs)
    
    def format_conditions_section(self, paths):
        """
        Format the conditions section with proper alignment.
        Returns a list of lines.
        """
        lines = []
        
        if not paths:
            return lines
        
        # Find the longest "from" name to determine padding
        max_from_len = max(len(from_name) for from_name, _, _ in paths)
        
        for from_name, to_name, conditions in paths:
            padding = " " * (max_from_len - len(from_name))
            cond_str = self.format_conditions(conditions)
            
            if cond_str:
                lines.append(f" {from_name}{padding} -> {to_name} ({cond_str})")
            else:
                lines.append(f" {from_name}{padding} -> {to_name}")
        
        return lines
    
    def log_tree(self, root_id):
        """Log a complete digivolution tree starting from root_id."""
        if root_id in self.logged_digimon:
            return
        
        # Build the tree structure
        tree = self.build_tree_structure(root_id)
        if not tree:
            return
        
        # Mark all digimon in this tree as logged
        self._mark_tree_logged(tree)
        
        # Format the header
        digimon_name = tree['name']
        digimon_num = f"#{root_id:03d}"
        
        self.logger.info(f"\n== {digimon_num}: {digimon_name} ==")
        
        # Log the tree chart
        self.logger.info("Digivolution Chart:")
        tree_lines = self.format_tree_chart(tree)
        for line in tree_lines:
            self.logger.info(line)
        
        # Log the conditions
        paths = self.get_evolution_path_conditions(tree)
        if paths:
            self.logger.info("\nDigivolve Conditions:")
            condition_lines = self.format_conditions_section(paths)
            for line in condition_lines:
                self.logger.info(line)
        
        self.logger.info("")  # Empty line for separation
    
    def _mark_tree_logged(self, tree):
        """Mark all digimon in the tree as logged."""
        self.logged_digimon.add(tree['id'])
        for child in tree['children']:
            self._mark_tree_logged(child)
    
    def log_all_trees(self):
        """Log all digivolution trees."""
        self.logger.info("\n==================== DIGIVOLUTION TREES ====================\n")
        
        roots = self.find_root_digimon()
        
        for root_id in roots:
            self.log_tree(root_id)
