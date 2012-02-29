from templateEntity import CaduceusTemplateEntity

class CaduceusTemplateHtmlTag(CaduceusTemplateEntity):
	def __init__(self, tag, attribs, isEmptyTag = False):
		CaduceusTemplateEntity.__init__(self)
		self._tag = tag
		self._attribs = attribs
		self._isEmptyTag = isEmptyTag
	
	def render(self, dictGlob, dictLoc, results):
		htmlAttribs = ""
		for attr in self._attribs:
			htmlAttribs += ' %s="%s"' % (attr[0], attr[1])
		
		if self._isEmptyTag:
			return "<%s%s />" % (self._tag, htmlAttribs)
		else:
			content = CaduceusTemplateEntity.render(self, dictGlob, dictLoc, results)

			if self._tag == "title":
				results.setTitle(content)			
			
			return "<%s%s>%s</%s>" % (self._tag, htmlAttribs,
								   content, self._tag)

	def _matchTag(self, tag):
		return tag == self._tag