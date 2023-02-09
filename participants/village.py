from participants.abstract import *
import participants.producer as pro
import participants.consumer as con

class Village(Participant):
    def __init__(self, producer : pro.Producer, consumer : con.SalaryConsumer):
        self.consumer = consumer
        self.producer = producer 

    def participate(self, prices : Prices) -> VolumeBundle:
        (wages, pbundle) = self.producer.produce(prices)
        print(wages, "wages, at prices ", prices)
        cbundle = self.consumer.consume_salary(wages, prices)
        return pbundle + cbundle
