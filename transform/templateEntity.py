
class CaduceusTemplateResults():
	SUCCESS = 1
	FAILURE = 2
	ERROR = 3
	
	def __init__(self, tmplPath):
		self._tmptPath = tmplPath
		self._title = ""
		
		self._assertions = []
		self._assertionsSumup = { self.SUCCESS: 0, self.FAILURE: 0, self.ERROR: 0 }

		self._exceptions = []
		
	def setTitle(self, title):		
		self._title = title

	def getTitle(self):		
		return self._title
	
	def getTemplatePath(self):
		return self._tmptPath
		
	def addAssertion(self, assertionType, szMsg):
		newIndex = len(self._assertions)
		name = "assertion_id_%d" % newIndex
		self._assertions.append([name, assertionType, szMsg])
		self._assertionsSumup[assertionType] += 1
		
		return name
		
	def getAssertionTypeCount(self, assertionType):
		return self._assertionsSumup[assertionType]
		
	def getAssertionCount(self):
		return len(self._assertions)

	def getAssertions(self):
		return self._assertions
		
	def addExceptionsError(self, szError):
		newIndex = len(self._exceptions)
		name = "exception_id_%d" % newIndex
		self._exceptions.append([name, szError])
		
		return name
	
	def getErrors(self):
		errors = [] + self._exceptions
		for assertion in self._assertions:
			if (assertion[1] == self.ERROR):
				errors.append([assertion[0], assertion[2]])
		return errors
	
	def getFailures(self):
		failures = []
		for assertion in self._assertions:
			if (assertion[1] == self.FAILURE):
				failures.append([assertion[0], assertion[2]])
		return failures

class CaduceusResults():
	def __init__(self):
		self.assertions = 0
		self.success = 0
		self.failures = 0
		self.errors = 0
		self._templates = []
		
	def addTemplateResult(self, templateResult):
		self._templates.append(templateResult)
	
	def getAssertionTypeCount(self, assertionType):
		count = 0
		for result in self._templates:
			count += result.getAssertionTypeCount(assertionType)
		return count
	
	def getAssertionCount(self):
		count = 0
		for result in self._templates:
			count += result.getAssertionCount()
		return count
	
	def getTemplateResults(self):
		return self._templates
	
	def hasFailed(self):
		return bool(self.getAssertionTypeCount(CaduceusTemplateResults.FAILURE) or self.getAssertionTypeCount(CaduceusTemplateResults.ERROR))
		
class CaduceusTemplateEntity():
	def __init__(self):
		self._parent = None
		self._childs = []
	
	def addToken(self, token):
		token._parent = self
		self._childs.append(token)
		
		return token
			
	def endTag(self, tag):
		token = self
		while not token._matchTag(tag):
			token = token._parent
		return token._parent		
		
	def render(self, dictGlob, dictLoc, results):
		content = ""
		for child in self._childs:
			content += child.render(dictGlob, dictLoc, results)
		return content
			
	def _matchTag(self, tag):
		return False
	
	def addTokenFirst(self, token):
		token._parent = self
		self._childs.insert(0, token)
		
		return token
	
