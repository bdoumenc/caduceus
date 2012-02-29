from templateEntity import CaduceusTemplateEntity

class CaduceusTemplateHtmlComment(CaduceusTemplateEntity):
	def __init__(self, text):
		CaduceusTemplateEntity.__init__(self)
		self._text = text
		
	def render(self, dictGlob, dictLoc, results):
		return "<!-- %s -->%s" % (self._text,
						 CaduceusTemplateEntity.render(self, dictGlob, dictLoc, results))
