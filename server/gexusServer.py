import cherrypy
import os

from mako.template import Template
from mako.lookup import TemplateLookup


class GameDesc (object):
    def __init__(self, theId, theName, theDescription):
        self.name = theName
        self.id = theId
        self.description = theDescription
        


class CherryExposedBase (object):
    def __init__(self, makoLookup):
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
    def moveUp(self ):
        print "move UP"

    @cherrypy.expose
    def moveDown(self ):
        print "move Down"


class Gexus(CherryExposedBase):

    # def __init__(self):
    #    pass
    
    def __init__(self, makoLookup):
        super (Gexus, self).__init__(makoLookup)    
        self.m_registeredGames = [GameDesc("Pong", "Pong", "come on, it's a classic !")]
    
    @cherrypy.expose
    def index(self):
        
        mytemplate = self.getTemplate("gexus.html")
        return mytemplate.render(gamesAvail=self.m_registeredGames)
        



def buildStructure(makoLookup):
    
    root = Gexus(makoLookup)
    root.m_makoLookup = makoLookup
    root.Pong = Pong(makoLookup)
    
    return root



#                         tools.staticfile.on: True
# tools.staticfile.filename: '/home/poseidon/dev/gexus/server/css/base.css'
#                       })



mylookup = TemplateLookup(directories=['html/'])  # use for py byetcode compile, module_directory='/tmp/mako_modules')
root = buildStructure(mylookup)

cherrypy.config.update({'server.socket_host':'192.168.1.33',
                        'server.socket_port': 8080}  # # be root ot have 80 on *nix
                        )

appPath = os.path.abspath(os.path.dirname(__file__))
cssPath = appPath + "/css/"
jsPath = appPath + "/js/"


# cherrypy.tree.mount(DoNothing(), '/',
conf = { '/css/base.css' : {
                 'tools.staticfile.on': True,
                 'tools.staticfile.filename' : cssPath + 'base.css'
        },
        '/js/base.js' : {
                 'tools.staticfile.on': True,
                 'tools.staticfile.filename' : jsPath + 'base.js'
                 # 'tools.staticdir.index': 'index.html',
        }}


cherrypy.quickstart(root, config=conf)
