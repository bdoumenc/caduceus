from HTMLParser import HTMLParser, HTMLParseError
from template import CaduceusTemplate
from templateHtmlComment import CaduceusTemplateHtmlComment
from templateHtmlTag import CaduceusTemplateHtmlTag
from templateHtmlText import CaduceusTemplateHtmlText
from templatePython import CaduceusTemplatePython
import os

class CaduceusTemplateParser(HTMLParser):
	def __init__(self, filePath, rootPath, caduceusPath = None):
		HTMLParser.__init__(self)
		self._path, _filename = os.path.split(filePath)
		self._rootPath = rootPath
		self._caduceusPath = caduceusPath
		
		self._templateRoot = CaduceusTemplate(self._path, self._rootPath, self._caduceusPath)
		self._curToken = self._templateRoot
		
	def _concordionCompatibility(self, tag, attrs):
		# Concordion compatibility
		fixedAttrs = []
		pythonToken = None
		for attr in attrs:
			if attr[0] == "concordion:assertequals":
				#print attr[0]
				pythonToken = CaduceusTemplatePython("assertEqual %s" % attr[1].replace("#", "_"), self._path, self._rootPath)
			elif attr[0] == "concordion:set":
				#print attr[0]
				pythonToken = CaduceusTemplatePython("set %s" % attr[1].replace("#", "_"), self._path, self._rootPath)
			elif attr[0] == "concordion:execute":
				#print attr[0]
				statment = attr[1].replace("#TEXT", "@")
				statment = statment.replace("#", "_")
				pythonToken = CaduceusTemplatePython("exec %s" % statment, self._path, self._rootPath)
			else:
				#print attr[0]
				fixedAttrs.append(attr)
				
		return (fixedAttrs, pythonToken)
	
	def handle_starttag(self, tag, attrs):
		#print "Encountered a start tag: %s attrib %s" % (tag, attrs)
		
		attrs, pythonToken = self._concordionCompatibility(tag, attrs)
		
		token = CaduceusTemplateHtmlTag(tag, attrs)
		self._curToken = self._curToken.addToken(token)
		
		if tag == "head":
			self._templateRoot.setHeadTagRef(token)
		elif tag == "html":
			self._templateRoot.setHtmlTagRef(token)

		if pythonToken:
			self._curToken = self._curToken.addToken(pythonToken)
		
	def handle_endtag(self, tag):
		#print "Encountered  an end tag:", tag
		self._curToken = self._curToken.endTag(tag)
		
	def handle_startendtag(self, tag, attrs):
		#print "Encountered a start end tag: %s attrib %s" % (tag, attrs)
		attrs, pythonToken = self._concordionCompatibility(tag, attrs)

		if pythonToken:
			token = CaduceusTemplateHtmlTag(tag, attrs)
			self._curToken = self._curToken.addToken(token)
			self._curToken = self._curToken.addToken(pythonToken)
			self._curToken = self._curToken.endTag(tag)
		else:
			token = CaduceusTemplateHtmlTag(tag, attrs, True)
			self._curToken = self._curToken.addToken(token)
			self._curToken = self._curToken.endTag(tag)
		
	def get_starttag_text(self, text):
		#print "Encountered  an start text:", text
		pass
	
	def handle_data(self, data):
		#print "Encountered   some data:", data
		token = CaduceusTemplateHtmlText(data)
		self._curToken = self._curToken.addToken(token)
		
	def handle_comment(self, data):
		token = CaduceusTemplateHtmlComment(data)
		self._curToken = self._curToken.addToken(token)		
	
	def handle_pi(self, data):
		#print "Encountered   pi:", data
		token = CaduceusTemplatePython(data, self._path, self._rootPath)
		self._curToken = self._curToken.addToken(token)
	
	@staticmethod
	def _getTemplateFileContent(filePath):
		content = None
		file = open(filePath, 'r')
		if file:
			try:
				content = file.read()
			finally:
				file.close()
				
		return content
	
	@staticmethod
	def parseTemplateFile(filePath, rootPath, caduceusPath):
		content = CaduceusTemplateParser._getTemplateFileContent(filePath)	
		if content:
			
			parser = CaduceusTemplateParser(filePath, rootPath, caduceusPath)
			parser.feed(content)
			
			return parser._templateRoot
		
		return None
	
	@staticmethod
	def parsePatialFile(partialName, filePath, rootPath):
		# Check if partial is in current path
		partialFullPath = os.path.join(filePath, "_" + partialName)
		if not os.path.exists(partialFullPath):
			# Check if partial is in subdirectory partial of root path
			partialFullPath = os.path.join(rootPath, "partials", "_" + partialName)
			if not os.path.exists(partialFullPath):
				print "Can't locate partial '%s'" % partialName
				return None
			
		content = CaduceusTemplateParser._getTemplateFileContent(partialFullPath)	
		if content:
			parser = CaduceusTemplateParser(filePath, rootPath)
			parser.feed(content)
			
			return parser._templateRoot
		
		return None	
