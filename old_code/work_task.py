from abc import ABC, abstractmethod

class WorkTask(ABC):
    @abstractmethod
    def explanation(province_printer, good_printer):
        pass

class Trade(WorkTask):
    def __init__(self, good, source, target):
        self._good = good
        self._from = source
        self._to = target

    def explanation(province_printer, good_printer):
        return f"transporting {good_printer(self._good)} from {province_printer(self._from)} to {province.printer(self._to)}"
    

class Production(WorkTask):
    pass
