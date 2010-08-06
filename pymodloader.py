import clr
clr.AddReference('OpenSim.Framework')
clr.AddReference('OpenSim.Region.Framework')

import sys
sys.path.append('ScriptEngines/Lib') # stdlib seems to live here

from OpenSim.Region.Framework.Interfaces import IRegionModule
#import kek
import rexprojectspacemodule
import scriptbridgemodule

class PyReloader(IRegionModule):
    upgradable = False
    #regpymods = [kek]
    regpymods = [rexprojectspacemodule,scriptbridgemodule]
    reginstances = []

    def Initialise(self, scene, configsource):
        self.scene = scene
        self.config = configsource
        scene.AddCommand(self, "py-reload", "py-reload", "...", self.cmd_py_reload)
        print self, 'initialised with', scene

    def PostInitialise(self):
        print self, 'post-initialise'
    
    def Close(self):
        print self, 'close'

    def getname(self):
        return "MyRegionModule"

    Name = property(getname)

    def isshared(self):
        return False

    IsSharedModule = property(isshared)

    def cmd_py_reload(self, modname, args):
        try:
            self.reload(modname, args)
        except Exception, e:
            print 'err or'
            import traceback
            traceback.print_exc()
            raise

    def reload(self, modname, args):
        print 'closing modules'
        for ri in self.reginstances:
            if ri.Name in self.scene.Modules:
                ri.removed = True
                print "removing", ri.Name, "from self.scene.Modules"
                self.scene.Modules.Remove(ri.Name)
            ri.Close()

        self.reginstances[:] = []

        print 'reloading modules & looking for region classes'
        regclasses = []
        for m in self.regpymods:
            reload(m)
            for name in dir(m):
                o = getattr(m, name)
                if name.startswith('_'):
                    continue
                try:
                    x = issubclass(o, IRegionModule)
                except TypeError:
                    pass
                else:
                    if x and getattr(o, 'autoload', None):
                        print 'found', name
                        regclasses.append(o)

        print 'instantiating found regions'
        for klass in regclasses:
            ri = klass()
            ri.Initialise(self.scene, self.config)
            self.scene.AddModule(ri.Name, ri)
            self.reginstances.append(ri)
        print 'reload done'

loader = None

def sceneinit(scene, config):
    global loader
    loader = PyReloader()
    loader.Initialise(scene, config)
    loader.PostInitialise()
    loader.cmd_py_reload('', [])
