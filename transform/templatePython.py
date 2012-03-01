from templateEntity import CaduceusTemplateEntity, CaduceusTemplateResults
import re
import traceback
import os

class CaduceusTemplatePython(CaduceusTemplateEntity):
	def __init__(self, data, path, rootPath):
		CaduceusTemplateEntity.__init__(self)
		# Strip ? and white spaces at end of string
		self._data = data.rstrip(" ?\n")
		self._path = path
		self._rootPath = rootPath
			
	def render(self, dictGlob, dictLoc, tmplResults):
		# Render childs
		
		match = re.match("(assertEqual|assertNotEqual) (.+)", self._data)
		if match:
			return self._assert(match.group(1), match.group(2), dictGlob, dictLoc, tmplResults)
		
		match = re.match("exec (.+)", self._data)
		if match:
			return self._exec(match.group(1), dictGlob, dictLoc, tmplResults)

        match = re.match("echo (.+)", self._data)
        if match:
            return self._echo(match.group(1), dictGlob, dictLoc, tmplResults)

		match = re.match("set (.+)", self._data)
		if match:
			return self._setVariable(match.group(1), dictGlob, dictLoc, tmplResults)				

		match = re.match("for (.+) in (.+)", self._data)
		if match:
			return self._loopFor(match.group(1), match.group(2), dictGlob, dictLoc, tmplResults)				

		match = re.match("include (.+)", self._data)
		if match:
			return self._include(match.group(1), dictGlob, dictLoc, tmplResults)				

		# Skip entity, only render childs
		return CaduceusTemplateEntity.render(self, dictGlob, dictLoc, tmplResults)
	
	def _assert(self, assertionType, pythonStmt, dictGlob, dictLoc, tmplResults):
		# Get comparaison text (ie: render childs)
		content = CaduceusTemplateEntity.render(self, dictGlob, dictLoc, tmplResults)
		
		try:
			result = eval("str(%s)" % pythonStmt, dictGlob, dictLoc)
			
			if assertionType == "assertEqual":
				comparaison = '"%s" == "%s"' % (result, content)
			else:
				comparaison = '"%s" != "%s"' % (result, content)
				
			if eval(comparaison, dictGlob, dictLoc):
				tagId = tmplResults.addAssertion(CaduceusTemplateResults.SUCCESS, None)
				return '<span id="%s" class="success">%s</span>' % (tagId, content)
			else:
				tagId = tmplResults.addAssertion(CaduceusTemplateResults.FAILURE, comparaison)
				return '<span id="%s" class="failure"><span class="expected">%s</span>%s</span>' % (tagId, content, result)
		except Exception:
			traceback.print_exc()
			tagId = tmplResults.addAssertion(CaduceusTemplateResults.ERROR, traceback.format_exc())
			return '<span id="%s" class="failure"><span class="expected">%s</span><pre class="exception">%s</pre></span>' % (tagId, content, traceback.format_exc())
			
	def _exec(self, pythonStmt, dictGlob, dictLoc, tmplResults):
		# We must eval python code before rendering childs,
		# except if @ shorcut is in use
		bRunChilds = True
		content = ""
		if '@' in pythonStmt:
			# Use content to get replacement for @
			bRunChilds = False
			content = CaduceusTemplateEntity.render(self, dictGlob, dictLoc, tmplResults)
			pythonStmt = pythonStmt.replace("@", '"%s"' % content)
		
		try:
			exec pythonStmt in dictGlob, dictLoc
		except Exception, excep:
			traceback.print_exc()
			tagId = tmplResults.addExceptionsError(traceback.format_exc())
			content = '<span id="%s" class="failure"><pre class="exception">%s</pre></span>' % (tagId, traceback.format_exc())
		
		if bRunChilds:
			return content + CaduceusTemplateEntity.render(self, dictGlob, dictLoc, tmplResults)
		else:
			return content

	def _echo(self, pythonStmt, dictGlob, dictLoc, tmplResults):
		content = ""
		try:
			content = eval(pythonStmt, dictGlob, dictLoc)
		except Exception, excep:
			traceback.print_exc()
			tagId = tmplResults.addExceptionsError(traceback.format_exc())
			content = '<span id="%s" class="failure"><pre class="exception">%s</pre></span>' % (tagId, traceback.format_exc())

		return content + CaduceusTemplateEntity.render(self, dictGlob, dictLoc, tmplResults)
		
	def _setVariable(self, variable, dictGlob, dictLoc, tmplResults):
		# Get variable value (ie: render childs)
		content = CaduceusTemplateEntity.render(self, dictGlob, dictLoc, tmplResults)
		
		pythonStmt = '%s = "%s"' % (variable, content)
		try:
			exec pythonStmt in dictGlob, dictLoc
		except Exception, excep:
			traceback.print_exc()
			tagId = tmplResults.addExceptionsError(traceback.format_exc())
			return '<span id="%s" class="failure"><pre class="exception">%s</pre></span>' % (tagId, traceback.format_exc())
		
		return ""
	
	def _loopFor(self, varName, listName, dictGlob, dictLoc, tmplResults):
		content = ""
		listName = listName.rstrip(":")
		
		list = eval(listName, dictGlob, dictLoc)
		for i in list:
			dictLoc[varName] = i
			content += CaduceusTemplateEntity.render(self, dictGlob, dictLoc, tmplResults)
	
		return content
	
	def _include(self, partialName, dictGlob, dictLoc, tmplResults):
		from templateParser import CaduceusTemplateParser
		content = ""
		template = CaduceusTemplateParser.parsePatialFile(partialName, self._path, self._rootPath)
		if template:
			content = template.render(dictGlob, dictLoc, tmplResults)
	
		return content

