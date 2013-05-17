import cherrypy
import os
import copy
import time
import thread
import threading
import json
import random

from mako.template import Template
from mako.lookup import TemplateLookup

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage



class ChatWebSocketHandler(WebSocket):
    def received_message(self, m):
        cherrypy.engine.publish('websocket-broadcast', m)

    def closed(self, code, reason="A client left the room without a proper explanation."):
        cherrypy.engine.publish('websocket-broadcast', TextMessage(reason))

def runGame(gameName, gameLogic, gameData, gameInput):
    
    print "Running game thread for " + gameName
    
    # # if this is too small, the webserver thread is blocked too often
    deltaT = 1.0
    
    while True:
        # print "Executing logic of game " + gameName
        gameLogic.execute(gameData, gameInput, deltaT)
        
        
        # cherrypy.engine.publish('websocket-broadcast', gameData.asJson())
        time.sleep(deltaT)
    
    pass

class GameDesc (object):
    def __init__(self, theId, theName, theDescription):
        self.name = theName
        self.id = theId
        self.description = theDescription
        


class CherryExposedBase (object):
    def __init__(self, makoLookup=None):
        self.m_makoLookup = makoLookup
        
    def getMakoLookup(self):
        return self.m_makoLookup
    
    def getTemplate (self , name):
        return self.getMakoLookup().get_template(name)

class Pong (CherryExposedBase):
    
    def __init__(self, makoLookup):
        super (Pong, self).__init__(makoLookup)
    
    @cherrypy.expose
    def index(self):
        mytemplate = self.getTemplate("pong/pong_controls.html")
        return mytemplate.render()

    # the call http://localhost:8080/GameOne/input/23/23 is mapped to this one !
    @cherrypy.expose
    def moveUp(self):
        print "move UP"

    @cherrypy.expose
    def moveDown(self):
        print "move Down"
        
class Evader (CherryExposedBase):
    
    def __init__(self, makoLookup, gameData, gameInput):
        super (Evader, self).__init__(makoLookup)
        self.gData = gameData
        self.gInput = gameInput
    
    @cherrypy.expose
    def index(self):
        mytemplate = self.getTemplate("space_evader/evader_controls.html")
        return mytemplate.render()

    @cherrypy.expose
    def view(self):
        mytemplate = self.getTemplate("space_evader/evader_view.html")
        return mytemplate.render()

    @cherrypy.expose
    def gameState(self):
        # mytemplate = self.getTemplate("space_evader/evader_view.html")
        # return mytemplate.render()
        taskForPlayer = 0
        
        for ts in self.gData.currentTasks:
            if ts.shownToPlayer == 0:
                taskForPlayer = ts
        
        gs = { "playerTask": taskForPlayer.__dict__}
        
        jsonState = json.dumps(gs) 
        return jsonState

    # the call http://localhost:8080/GameOne/input/23/23 is mapped to this one !
    @cherrypy.expose
    def move(self, direction):
        self.setPlayerInput(direction)
        
    @cherrypy.expose
    def controlActivate(self, controlId):
        self.setPlayerInput("activate" + str(controlId))

    def setPlayerInput(self, move):
        with self.gInput.lock:
            self.gInput.content [ 0] = move

class Box(object):
    def __init__(self, x, y, sizeX, sizey):
        self.location = (x, y)
        sefl.size = (sizeX, sizeY) 

class EvaderLogic(object):
    def __init__(self):
        pass
    
    def generateTasks (self , gameData):
        if not gameData.hasTasks (0):
            print "generating task"
            
            taskNum = random.randint(0, 4)
            gameData.currentTasks += [ Task("Activate " + str(taskNum), "activate" + str(taskNum), 0, 10) ]
    
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
        for ( pid, ac) in actionList.iteritems():
            print self.neededAction
            if ac == self.neededAction:
                return True
        return False

class EvaderData(object):
    def __init__(self):
        self.playerLocation = {}
        self.boxes = []
        self.currentTasks = []
        pass
    # # make thread safe
    def asJson(self):
        # return json.dumps ({ "player" : self.playerLocation, "boxes" : self.boxes })
        return json.dumps (self.currentTasks)
    
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


class Gexus(CherryExposedBase):

    # def __init__(self):
    #    pass
    
    def __init__(self, makoLookup):
        super (Gexus, self).__init__(makoLookup)    
        self.m_registeredGames = [GameDesc("Pong", "Pong", "come on, it's a classic !"),
                                  GameDesc("Evader", "Space Evader", "come on, it's a classic !")]
    
    @cherrypy.expose
    def index(self):
        
        mytemplate = self.getTemplate("gexus.html")
        return mytemplate.render(gamesAvail=self.m_registeredGames)
        




class WsExpose(CherryExposedBase):
    @cherrypy.expose
    def ws(self):
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))



#                         tools.staticfile.on: True
# tools.staticfile.filename: '/home/poseidon/dev/gexus/server/css/base.css'
#                       })




makoLookup = TemplateLookup(directories=['html/'])  # use for py byetcode compile, module_directory='/tmp/mako_modules')

evaderLogic = EvaderLogic()
evaderData = EvaderData()
evaderInput = EvaderInput()

root = Gexus(makoLookup)
root.m_makoLookup = makoLookup
root.Pong = Pong(makoLookup)
root.Evader = Evader(makoLookup, evaderData, evaderInput)
root.EvaderWs = WsExpose()

cherrypy.config.update({'server.socket_host':'192.168.1.33',
                        'server.socket_port': 8080}  # # be root ot have 80 on *nix
                        )

appPath = os.path.abspath(os.path.dirname(__file__))
cssPath = appPath + "/css/"
jsPath = appPath + "/js/"

WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

# cherrypy.tree.mount(DoNothing(), '/',
conf = { '/css/base.css' : {
                 'tools.staticfile.on': True,
                 'tools.staticfile.filename' : cssPath + 'base.css'
        },
        '/js/base.js' : {
                 'tools.staticfile.on': True,
                 'tools.staticfile.filename' : jsPath + 'base.js'
                 # 'tools.staticdir.index': 'index.html',
        },
       '/EvaderWs': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': ChatWebSocketHandler
            }}



# read only for the web output
root.Evader.m_gameData = evaderData
# webserice can wire here, but must lock
root.Evader.m_gameInput = evaderInput

# run game threads
thread.start_new_thread(runGame, ("evaderThread", evaderLogic, evaderData, evaderInput))

cherrypy.quickstart(root, config=conf)
