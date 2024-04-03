from dataclasses import dataclass

@dataclass
class Placement:
    global_width : int
    production_slice : slice

@dataclass
class LaborPlacement(Placement):
    labor_index : int
