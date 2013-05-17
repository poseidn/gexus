import uuid
import time
import random
import threading
import copy

import Support

class Control(object):
    def __init__(self, playerId, name, id, type="pushButton", minValue=0, maxValue=10):
        self.playerId = playerId
        self.name = name
        self.id = id
        self.type = type
        self.minValue = minValue
        self.maxValue = maxValue
    
    def getActionList (self):
        if self.type == "pushButton" :
            # just one possible action
            # id and user text : warp curvature to 4
            return [(self.id, self.name)]
        if self.type == "slider" :
            # just one possible action
            # id and user text : warp curvature to 4
            it = []
            for i in range(self.maxValue): 
                it += [(self.id + "_" + str(i), self.name + " to " + str(i))]
            return it                                 


class EvaderLogic(object):
    def __init__(self):
        
        self.actionName = ["Purge", "Activate", "Dismantle", "Engage", "Disengage", "Mismatch", "Mess-up"]
        self.firstName = ["", "", "", "Forward", "Backward", "Minor", "Starbird", "Internal", "External" ]
        self.secondName = ["Beam", "Fire", "Cooling", "", "", "", "", "", "" ]
        self.thirdName = ["Manifold", "Confinement", "Shielding", "Extraciter", "Preglobalizer", "Intrarectifier" ]
        
        pass
    

    
    def generateControl(self, gameData, playerId):
        act = Support.randomFromList(self.actionName)
        fr = Support.randomFromList(self.firstName)
        sc = Support.randomFromList(self.secondName)
        th = Support.randomFromList(self.thirdName)
        
        fullName = act + " " + fr + " " + sc + " " + th
        print "Generated control with name " + fullName
        return Control(playerId, fullName, str(gameData.getFreeControlId()))
    
    def generateTasks (self , gameData, fixedTask=None):
        for (pid, pdata) in gameData.player.iteritems():
            if not gameData.hasTasks (pid):
                print "generating task for player " + pid
                
                acts = gameData.getPossibleActions()
                if len(acts) > 0:
                    if fixedTask == None: 
                        ourAct = Support.randomFromList(acts)
                    else:
                        ourAct = acts[fixedTask]
                    gameData.currentTasks += [ Task(ourAct[1], ourAct[0], pid, 10) ]
    
    def execute(self, gameData, gameInput, timeDelta):
        with gameInput.lock:
            localGameInput = copy.deepcopy (gameInput.content)
        
        print "Current tasks in list" + str (len (gameData.currentTasks))
        
        for t in gameData.currentTasks:
            if not t.isComplete:
                if t.doesMatch (localGameInput):
                    t.complete()
                    
                    print "Task completed"
                else:
                    t.timeRunning += timeDelta
        
        self.generateTasks(gameData)
            # if (pIn == "up"):
            #    gameData.playerLocation [ pId ] = maxXHigh
            # if (pIn == "middle"):
            #    gameData.playerLocation [ pId ] = (maxXHigh - maxXLow) * 0.5
            # if (pIn == "down"):
            #    gameData.playerLocation [ pId ] = maxXLow

class Task(object):
    def __init__(self, taskName, action, shownToPlayer, maxTime):
        self.taskName = taskName
        self.neededAction = action
        self.shownToPlayer = shownToPlayer
        self.maxTime = maxTime
        self.timeRunning = 0.0
        self.isComplete = False
    
    def complete (self):
        self.isComplete = True
    
    def doesMatch(self, actionList):
        print actionList
        print self.neededAction
        for (pid, ac) in actionList.iteritems():
            if ac == self.neededAction:
                return True
        return False


class EvaderData(object):
    def __init__(self):
        self.player = {}
        self.possibleControls = []
        self.currentTasks = []
        self.freeControlId = 1
        pass
    
    def getFreeControlId(self):
        yourId = self.freeControlId
        self.freeControlId += 1
        return yourId
    
    def createUser(self):
        pId = str(uuid.uuid1())
        
        # # seconds in float
        self.player[ pId ] = { time.time() }
        return pId

    def addControl(self, control):
        self.possibleControls += [ control]
        
    def getPossibleActions(self):
        act = []
        for contr in self.possibleControls:
            act += contr.getActionList() 
        return act
        
    def removeControlsOfPlayer (self, playerId):
        # todo: also the pending task for this players controls
        
        self.possibleControls = filter(lambda x: x.playerId == playerId, self.possibleControls)

    # # make thread safe
    def asJson(self):
        # return json.dumps ({ "player" : self.playerLocation, "boxes" : self.boxes })
        return json.dumps (self.currentTasks)
    
    def getUncompletedTasks(self):
        return filter (lambda x: x.isComplete == False, self.currentTasks)

    def getCompletedTasks(self):
        return filter (lambda x: x.isComplete == True, self.currentTasks)

    
    def hasTasks (self, playerId):
        for t in self.currentTasks:
            if (t.shownToPlayer == playerId) and (not t.isComplete):
                return True
        return False

class EvaderInput(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.content = {}
        pass
