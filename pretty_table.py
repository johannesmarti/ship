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
class PrettyTableConfiguration:
    schema: Schema
    list_of_indices: list[int]
    float_precision: int = 3
    column_width: int = 10
    separator: str = "  "

def set_global_table_logging_from_schema(schema: Schema):
    global global_table_logging_configuration
    list_of_indices = schema.list_provinces_over_goods(None, None)
    config = PrettyTableConfiguration(schema, list_of_indices)
    global_table_logging_configuration = config

def set_global_table_logging_configuration(config: PrettyTableConfiguration):
    global global_table_logging_configuration
    global_table_logging_configuration = config

def pretty_table(value_list: list[str, np.ndarray], file=sys.stdout):
    global global_table_logging_configuration

    config = global_table_logging_configuration
    schema = config.schema
    list_of_indices = config.list_of_indices
    sep = config.separator
    float_precision = config.float_precision
    column_width = config.column_width

    num_columns = len(value_list)
    headers = (v[0] for v in value_list)
    values = [v[1] for v in value_list]


    row_names = (schema.ix_to_str(ix) for ix in list_of_indices)
    first_column_width = max(len(s) for s in row_names)

    fmt_floats = sep.join("{:" + str(column_width) + "." + str(float_precision) + "f}"
                                           for _ in range(num_columns))
    fmt_headers = sep.join("{:<" + str(column_width) + "}"
                                           for _ in range(num_columns))

    print(fmt_headers.format(*headers), file=file)
    for ix in list_of_indices:
        row = [v[ix] for v in values]
        line = fmt_floats.format(*(v[ix] for v in values)) + sep + schema.ix_to_str(ix)
        print(line, file=file)


def log_values(log_level, value_list: list[str, np.ndarray]):
    if not logging.getLogger(__name__).isEnabledFor(log_level):
        return
    pretty_table(value_list, file=sys.stderr)
