from testBase import testBase

class testTest(testBase):
	def __init__(self):
		self.time = None

	def getGreeting(self):
		print self.time
		if self.time == "09:00AM":
			return "Good Morning World!"
		else:
			return "Hello World!"
	
	def greetingFor(self, name):
		return "Hello %s!" % name
	
	def setCurrentTime(self, time):
		print "setCurrentTime "
		self.time = time