import cherrypy

from mako.template import Template
from mako.lookup import TemplateLookup


class CherryExposedBase ( object ):
    def __init__(self, makoLookup):
        self.m_makoLookup = makoLookup
        
    def getMakoLookup(self):
        return self.m_makoLookup
    
    def getTemplate (self , name ):
        return self.getMakoLookup().get_template(name)

class GameOne (CherryExposedBase):
    
    def __init__(self, makoLookup):
        super (GameOne, self).__init__(makoLookup)
    
    @cherrypy.expose
    def index(self):
        return "Game One"

    # the call http://localhost:8080/GameOne/input/23/23 is mapped to this one !
    @cherrypy.expose
    def input(self, xMove, yMove):
        return "Game One move " + str(xMove) + " : " + str(yMove)



class Gexus(CherryExposedBase):
    
    def __init__(self, makoLookup):
        super (Gexus, self).__init__(makoLookup)
    
    @cherrypy.expose
    def index(self):
        
        mytemplate = self.getTemplate( "gexus.html" )
        return mytemplate.render()
        



def buildStructure(makoLookup):
    
    root = Gexus(makoLookup)
    root.GameOne = GameOne(makoLookup)
    
    return root



mylookup = TemplateLookup(directories=['html/'])  # use for py byetcode compile, module_directory='/tmp/mako_modules')
root = buildStructure(mylookup)

cherrypy.quickstart(root)
