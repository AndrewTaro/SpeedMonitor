API_VERSION = 'API_v1.0'
MOD_NAME = 'SpeedMonitor' 

try:
    import utils, events, ui, callbacks, battle
except:
    pass


COMPONENT_KEY   = 'modSpeedMonitor'
KNOTS_TO_MPS    = 0.5144444444444445
MPS_TO_KNOTS    = 1.0 / KNOTS_TO_MPS
BW_TO_METER     = 30.0
TIME_SCALE      = 5.22

BW_MPS_TO_KNOTS = MPS_TO_KNOTS * BW_TO_METER / TIME_SCALE


class SpeedMonitor(object):
    def __init__(self):
        self.vary = None
        self.vehiclePositions = {}
        self.prevTime = 0.0
        events.onBattleStart(self.onBattleStart)
        events.onBattleQuit(self.onBattleQuit)
        
    def onBattleStart(self, *args):
        self.vehiclePositions = {}
        self.prevTime = utils.getTimeFromGameStart()
        self.vary = callbacks.perTick(self.update)
        self._addEntity()

    def onBattleQuit(self, *args):
        callbacks.cancel(self.vary)
        self.prevTime = 0.0
        self.vehiclePositions.clear()
        self._removeEntity()

    def _addEntity(self):
        self.entityId = ui.createUiElement()
        ui.addDataComponentWithId(self.entityId, COMPONENT_KEY, {'speeds': {}})

    def _removeEntity(self):
        ui.deleteUiElement(self.entityId)
        self.entityId = None
        
    def update(self, *args):
        currentTime = utils.getTimeFromGameStart()
        timeDiff = currentTime - self.prevTime
        if timeDiff == 0.0:
            return
        data = {}

        for ship in battle.getAllShips():
            uiId    = ship.uiId
            shipPos = ship.getPosition()

            if uiId not in self.vehiclePositions:
                # First spot: can't calculate the correct speed from displacement
                # Vehicles spotted a long ago will have an incorrect speed too
                # But it's just only one frame so it's okey
                self.vehiclePositions[uiId] = shipPos
                continue
                
            posDiff = shipPos - self.vehiclePositions[uiId]
            speed   = posDiff.length / timeDiff
            data[uiId] = speed * BW_MPS_TO_KNOTS

            self.vehiclePositions[uiId] = shipPos

        ui.updateUiElementData(self.entityId, {'speeds': data})
        self.prevTime = currentTime


gSpeedMonitor = SpeedMonitor()
