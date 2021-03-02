import maya.cmds as cmds

#defining motionSketch class 
class motionSketch():
	
	global animObj
	
	def __init__(self):
		self.win()

	#UI window definition
	def win(self):
	    winName = "motionSketch"
	    
	    #deletes existing window UI if it already exists
	    if cmds.window(winName, exists = True):    		    			    						
	        cmds.deleteUI(winName)
	    
	    cmds.window(winName, titleBar = True, rtf = True, menuBar = True, widthHeight = (800, 500), title = "Motion Sketch")
	    cmds.columnLayout(adj = True)
	    print "window generating"
	    #Window text explaining the tool
	    cmds.text(label = 'Start recording and move the object along the desired path', align = 'center')      
	    cmds.separator(st = 'single', h = 10, hr = True)
	    #Buttons with different titles that call the same start function but with different parameter
	    cmds.iconTextButton(style = 'iconAndTextVertical', w = 150, h = 50, image1 = 'recording.png', si = 'recordStandby.png', label = 'RECORD', command = self.startFunc)
	    cmds.separator(st = 'single', h = 10, hr = True)
	    cmds.iconTextButton(style = 'iconAndTextVertical', w = 150, h = 50, image1 = 'stopClip.png', label = 'STOP', command = self.stopFunc)
	    cmds.separator(st = 'single', h = 10, hr = True)
	    cmds.iconTextButton(style = 'iconAndTextVertical', w = 150, h = 50, image1 = 'curveEP.png', label = 'BUILD CURVE', command = self.buildCurve)
	    cmds.separator(st = 'single', h = 10, hr = True)
	    cmds.iconTextButton(style = 'iconAndTextVertical', w = 150, h = 50, image1 = 'curveEditor.png', label = 'SMOOTH CURVE', command = self.smoothCurve)
	    cmds.separator(st = 'single', h = 10, hr = True)
	    self.sliderVal = cmds.floatSliderGrp(label = 'ANIMATION SPEED', min = 0.1, max= 5, value = 1, step = 0.1, field = True, changeCommand = self.animSpeed)
	    
	    #calling window function
	    cmds.showWindow()

    #recording function
	def startFunc(self):
	    
	    global animObj

	    #check for existing tool context 
	    if cmds.manipMoveContext('moveTool', exists = True):
	        cmds.deleteUI('moveTool')

	    #Setting to move tool context for recording
	    cmds.manipMoveContext('moveTool')
	    cmds.setToolTo('moveTool')
	    sel = cmds.ls(sl = True)
	    animObj = cmds.duplicate(sel)[0]  
	    cmds.delete(sel)
	    #recording translation keyframes
	    cmds.recordAttr(at = ['translateX', 'translateY', 'translateZ'])
	    cmds.play(record = True, st = True) 
	
	#stop function    
	def stopFunc(self):
	    
	    global animObj

	    cmds.play(st = False)
	    #deleting stray keyframes
	    key = int(cmds.findKeyframe(animObj, time = (1,1), which = "next"))
	    cmds.cutKey(animObj, time = (1, key))
	
	#build curve function    
	def buildCurve(self):
	    
	    global animObj
	    tList = []

	    #getting first and last keyframe of animation
	    t_start = int(cmds.findKeyframe(animObj, time = (5,5), which = "next"))
	    t_end = int(cmds.findKeyframe(animObj, which = "last"))

	    #populating list of position values
	    for x in range(t_start, t_end):
	        pos = cmds.getAttr(animObj + ".translate", time = x)  
	        #print pos[0]
	        tList.append(pos[0])

	    #build CV curve from position array
	    cmds.curve(name = 'animCurve1', p = tList, degree = 1)
	    cmds.duplicate('animCurve1', name = 'animCurve')
	    cmds.delete('animCurve1')
	    new = cmds.duplicate(animObj)
	    cmds.delete(animObj)
	    animObj = new
	    #creating path animation
	    cmds.pathAnimation(animObj, c = 'animCurve', stu = t_start, etu = t_end)

	def smoothCurve(self):
	    
	    d = cmds.getAttr('animCurve.degree')  
	    cmds.rebuildCurve('animCurve', degree = d+1, rpo = True)
	    new = cmds.duplicate(animObj)
	    cmds.delete(animObj)
	    animObj = new
	    cmds.pathAnimation(animObj, c= 'animCurve')
	    
	def animSpeed(self, void):
	    
	    global animObj
	    global sliderVal

	    #get value from slider
	    val = cmds.floatSliderGrp(self.sliderVal, q = True, value = True) 
	    #get start and end points of current path animation
	    k1 = int(cmds.pathAnimation(animObj, stu = True, query = True))
	    k2 = int(cmds.pathAnimation(animObj, etu = True, query = True))
	    
	    new = cmds.duplicate(animObj)
	    cmds.delete(animObj)
	    animObj = new
	    print new
	    print animObj
	    k3 = int(k1 +(k2-k1)/val)
	    #create path animation with new speed
	    cmds.pathAnimation(animObj, stu = k1, etu = k3, c = 'animCurve')