from dataclasses import dataclass
from typing import Protocol
import numpy as np
import logging

import sys
import core.schema as schema

class Schema(Protocol):
    def ix_to_str(self, ix: int) -> str:
        pass

@dataclass(frozen=True)
class TableLoggingConfiguration:
    schema: Schema
    list_of_indices: list[int]
    numeric_column_width: int = 8

def set_global_table_logging_configuration(config: TableLoggingConfiguration):
    global global_table_logging_configuration
    global_table_logging_configuration = config

def out(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def log_values(log_level, value_list: list[str, np.ndarray]):
    global global_table_logging_configuration
    if not logging.getLogger(__name__).isEnabledFor(log_level):
        return

    num_columns = len(value_list)
    headers = [""] + [v[0] for v in value_list]
    values = [v[1] for v in value_list]

    config = global_table_logging_configuration
    schema = config.schema
    list_of_indices = config.list_of_indices

    row_names = (schema.ix_to_str(ix) for ix in list_of_indices)
    first_column_width = max(len(s) for s in row_names)
    other_columns_width = config.numeric_column_width

    fmt_first_column = "{:<" + str(first_column_width) + "} "
    fmt_other_columns = " ".join("{:>" + str(other_columns_width) + "}"
                                           for _ in range(num_columns))
    fmt = fmt_first_column + fmt_other_columns
    
    # Print headers
    out(fmt.format(*headers))
    # Print rows
    for ix in list_of_indices:
        row = [schema.ix_to_str(ix)] + [v[ix] for v in values]
        out(fmt.format(*row))


