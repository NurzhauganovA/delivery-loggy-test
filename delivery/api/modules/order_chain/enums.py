from api import enums


class OrderChainType(enums.Descriptor):
    SIMPLE = 'simple'
    EXPRESS = 'express'


class OrderChainStatus(enums.Descriptor):
    NEW = 'new'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'


class StageType(enums.Descriptor):
     AIR = 'air'
     SEA = 'sea'
     RAIL = 'rail'
     ROAD = 'road'