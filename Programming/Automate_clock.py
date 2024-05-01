import os
from pyldplayer.console import Console
from pyldplayer.process import DefaultProcess


LDplayer_is_running = False

class LDplayer:
    def __init__(self):
        self.path = r"C:\LDPlayer\LDPlayer9\ldconsole.exe"
        self.process = DefaultProcess(self.path)
        self.console = Console(self.process)
        self.instance = self.console.list2()
        self.runapp = self.console.runapp
        
    def openLDPlayer(self):
        if self.instance:
            self.instance[0].modify(root=True)
            self.instance[0].launch()
            self.instance[0].refresh
        else:
            print("No LDPlayer instance found")
            
    def RunApp(self, nameOrId, packageName):
        self.runapp(nameOrId, packageName)
        print("App is running")
            
# Open emulator for clock in
ldplayer_instance = LDplayer() 
ldplayer_instance.openLDPlayer()
LDplayer_is_running = True


if LDplayer_is_running == True:
    ldplayer_instance.runapp("HumanOS", "HumanOS")