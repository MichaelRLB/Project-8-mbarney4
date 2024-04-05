from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.task.Task import TaskManager
from direct.interval.IntervalGlobal import Sequence
import DefensePaths as defensePaths
from panda3d.core import *
from CollideObjectBase import *

# Keybinds in Player class don't work after converting to SphereCollideObject.
# Figure out the correct scales for the collision functions.
class Planet(SphereCollideObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Planet, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 1.05)  

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
class Universe(InverseSphereCollideObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Universe, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 0.9)

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
class Station(CapsuleCollidableObject):
     def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Station, self).__init__(loader, modelPath, parentNode, nodeName, 1, -1, 5, 1, -1, -5, 19)

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)   
class Drone(SphereCollideObject):
    droneCount = 0
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Drone, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 0.5)        

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
class Missile(SphereCollideObject):
    fireModels = {}
    cNodes = {}
    collisionSolids = {}
    Intervals = {}
    missileCount = 0
    def __init__(self, loader: Task.Loader, modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, scaleVec: float = 1.0):
        super().__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 3.0)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setPos(posVec)
        Missile.missileCount += 1
        Missile.fireModels[nodeName] = self.modelNode
        Missile.cNodes[nodeName] = self.collisionNode
        # We retrieve the solid for our collisionNode.
        Missile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
        Missile.cNodes[nodeName].show()
        print("Fire torpedo #" + str(Missile.missileCount))
        Missile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
        print("Fire torpedo #" + str(Missile.missileCount))
class Orbiter(SphereCollideObject):
    numOrbits = 0
    velocity = 0.01
    cloudTimer = 240
    def __init__(self, loader: Loader, taskMgr: TaskManager, modelPath: str, parentNode: NodePath, nodeName: str, scaleVec: Vec3, texPath: str, centralObject: PlacedObject, orbitRadius: float, orbitType: str, staringAt: Vec3):
        super(Orbiter, self,).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 2.0)
        self.taskMgr = taskMgr
        self.orbitType = orbitType
        self.modelNode.setScale(scaleVec)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        self.orbitObject = centralObject
        self.orbitRadius = orbitRadius
        self.staringAt = staringAt
        Orbiter.numOrbits += 1

        self.cloudClock = 0
        self.taskFlag = "Traveler-" + str(Orbiter.numOrbits)
        taskMgr.add(self.Orbit, self.taskFlag)
    def Orbit(self, task):
        if self.orbitType == "MLB":
            positionVec = defensePaths.BaseballSeams(task.time * Orbiter.velocity, self.numOrbits, 3.0)
            self.modelNode.setPos(positionVec * self.orbitRadius + self.orbitObject.modelNode.getPos())
        
        elif self.orbitType == "Cloud":
            if self.cloudClock < Orbiter.cloudTimer:
                self.cloudClock += 1

            else:
                self.cloudClock = 0
                positionVec = defensePaths.Cloud()
                self.modelNode.setPos(positionVec * self.orbitRadius + self.orbitObject.modelNode.getPos())
        self.modelNode.lookAt(self.staringAt.modelNode)
        return task.cont
class Wanderer(SphereCollideObject):
    numWanderers = 0

    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, modelName: str, scaleVec: Vec3, texPath: str, staringAt: Vec3):
        super(Wanderer, self).__init__(loader, modelPath, parentNode, modelName, Vec3(0, 0, 0), 3.2)

        self.modelNode.setScale(scaleVec)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        self.staringAt = staringAt
        Wanderer.numWanderers += 1

        posInterval0 = self.modelNode.posInterval(20, Vec3(350, 5000, 67), startPos = Vec3(0, 0, 0))
        posInterval1 = self.modelNode.posInterval(20, Vec3(1500, -2000, 67), startPos = Vec3(350, 5000, 67))
        posInterval2 = self.modelNode.posInterval(20, Vec3(350, 5000, 67), startPos = Vec3(1500, -2000, 67))

        self.travelRoute = Sequence(posInterval0, posInterval1, posInterval2, name = "Traveler")

        self.travelRoute.loop()