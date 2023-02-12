from dataclasses import dataclass

@dataclass
class Placement:
    width : int
    production_slice : slice
    labour_index : int
