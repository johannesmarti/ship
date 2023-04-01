from dataclasses import dataclass

@dataclass
class Placement:
    global_width : int
    production_slice : slice
    labour_index : int
