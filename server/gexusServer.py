import cherrypy
import os
import copy
import time
import thread
import threading
import json
import random
import uuid
import time

import Evader

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

def runGame(gameName, gameLogic, gameData, gameInput, terminate):
    
    print "Running game thread for " + gameName
    
    # # if this is too small, the webserver thread is blocked too often
    deltaT = 1.1
    
    while not terminate:
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
        
class EvaderFrontend (CherryExposedBase):
    
    def __init__(self, makoLookup, gameLogic, gameData, gameInput):
        super (EvaderFrontend, self).__init__(makoLookup)
        self.gData = gameData
        self.gLogic = gameLogic
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
    def gameState(self, playerId):
        # mytemplate = self.getTemplate("space_evader/evader_view.html")
        # return mytemplate.render()
        taskForPlayer = 0
        
        for ts in self.gData.currentTasks:
            if ts.shownToPlayer == playerId:
                taskForPlayer = ts
        
        
        if taskForPlayer == 0:
            taskForPlayerSer = taskForPlayer
        else:
            taskForPlayerSer = taskForPlayer.__dict__
        
        gs = { "playerTask": taskForPlayerSer,
               "playerId" :  playerId}
        
        jsonState = json.dumps(gs) 
        return jsonState

    @cherrypy.expose
    def listControls(self, playerId):
        playerControls = filter(lambda x : x.playerId == playerId, self.gData.possibleControls)
        
        dictList = []
        for dd in playerControls:
            dictList += [ dd.__dict__ ]
        
        asJson = json.dumps ( dictList )
        return asJson

    @cherrypy.expose
    def registerPlayer(self):
        
        # # seconds in float
        pId = self.gLogic.createUser(self.gData, True)
        print "Welcome new player " + pId
        return pId

    @cherrypy.expose
    def controlActivate(self, playerId, controlId):
        self.setPlayerInput(playerId, controlId)

    def setPlayerInput(self, playerId, move):
        with self.gInput.lock:
            self.gInput.content [ playerId] = move

class Box(object):
    def __init__(self, x, y, sizeX, sizey):
        self.location = (x, y)
        sefl.size = (sizeX, sizeY) 


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

evaderLogic = Evader. EvaderLogic()
evaderData = Evader.EvaderData()
evaderInput = Evader.EvaderInput()

root = Gexus(makoLookup)
root.m_makoLookup = makoLookup
root.Pong = Pong(makoLookup)
root.Evader = EvaderFrontend(makoLookup, evaderLogic, evaderData, evaderInput)
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

terminateLogic = False

conf = { 
         '/css/base.css' : {
                 'tools.staticfile.on': True,
                 'tools.staticfile.filename' : cssPath + 'base.css'
        },
        '/js/base.js' : {
                 'tools.staticfile.on': True,
                 'tools.staticfile.filename' : jsPath + 'base.js'
        },
       '/EvaderWs': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': ChatWebSocketHandler},
        '/' : {
                 # 'tools.sessions.on' : True,
                 # 'tools.sessions.storage_type' : 'file',
                 # 'tools.sessions.storage_path' : "/home/poseidon/tmp/",
                 # 'tools.sessions.timeout' : 60
        }
        }



# read only for the web output
root.Evader.m_gameData = evaderData
# webserice can wire here, but must lock
root.Evader.m_gameInput = evaderInput

terminateLogic = False
# run game threads
thread.start_new_thread(runGame, ("evaderThread", evaderLogic, evaderData, evaderInput, terminateLogic))

cherrypy.quickstart(root, config=conf)
terminateLogic = True
