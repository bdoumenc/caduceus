import os
from transform.templateEntity import CaduceusResults, CaduceusTemplateResults
from transform.template import CaduceusTemplate

class ReportJUnit:
	def __init__(self, caduceusResult, rootPath, caduceusPath):
		self._result = caduceusResult
		self._rootPath = rootPath
		self._caduceusPath = caduceusPath
		
	def generate(self):
		content = self._xmlHeader()
		content += self._xmlSuite(self._result)
		#content += self._getAssertionsOverall(self._result)
		#content += self._getAllErrors(self._result.getTemplateResults())
		#content += self._getAllFailures(self._result.getTemplateResults())
		content += self._xmlFooter()

		reportFullPath = os.path.join(self._rootPath, "caduceus-junit.xml")
		outputFile = open(reportFullPath, 'w')
		try:
			outputFile.write(content)
		finally:
			outputFile.close()
			
	def _xmlHeader(self):
		return '<?xml version="1.0" encoding="UTF-8"?>\n<testsuites>\n'
	
	def _xmlFooter(self):
		return "</testsuites>\n"
	
	def _xmlSuite(self, results):
		content = ""
		for tmpltResult in results.getTemplateResults():
			_path, filename = os.path.split(tmpltResult.getTemplatePath())
			
			content += '<testsuite name="%s" errors="%d" failures="%d" tests="%d" >\n' \
					% (filename,
					   tmpltResult.getAssertionTypeCount(CaduceusTemplateResults.ERROR),
					   tmpltResult.getAssertionTypeCount(CaduceusTemplateResults.FAILURE),
					   tmpltResult.getAssertionCount())
			for assertion in tmpltResult.getAssertions():
				content += self._xmlTestCase(assertion)
			content += "</testsuite>\n"
				
		return content
			
	def _xmlTestCase(self, assertion):
		if assertion[1] == CaduceusTemplateResults.FAILURE:
			content  = '<testcase name="%s" result="failure">' % (assertion[0])
			content += '\n\t<system-out><![CDATA[FAIL: %s]]></system-out>\n' % assertion[2]
		elif assertion[1] == CaduceusTemplateResults.ERROR:
			content  = '<testcase name="%s">' % (assertion[0])
			content += '\n<error>%s</error>\n' %assertion[2]
			content += '\n\t<system-out><![CDATA[FAIL: %s]]></system-out>\n' % assertion[2]
		elif assertion[1] == CaduceusTemplateResults.SUCCESS:
			content = '<testcase name="%s">' % (assertion[0])

		content += '</testcase>\n'
		return content
