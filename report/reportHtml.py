import os
import shutil
from caduceusHelpers import CaduceusHelper
from transform.templateEntity import CaduceusResults, CaduceusTemplateResults
from transform.template import CaduceusTemplate
from time import gmtime, strftime

class ReportHtml:
	def __init__(self, caduceusResult, rootPath, caduceusPath):
		self._result = caduceusResult
		self._rootPath = rootPath
		self._caduceusPath = caduceusPath
		self._reportPath = self._rootPath
		self._reportFilePath = os.path.join(self._reportPath, "caduceus-report.html")
		
	def generate(self):
		content = self._pageHeader()
		content += self._getAssertionsOverall(self._result)
		content += self._getAllErrors(self._result.getTemplateResults())
		content += self._getAllFailures(self._result.getTemplateResults())
		content += self._pageFooter()

		outputFile = open(self._reportFilePath, 'w')
		try:
			outputFile.write(content)
			
			CaduceusHelper.copyResource(self._caduceusPath, self._rootPath, "caduceus-mini.png")
			CaduceusHelper.copyResource(self._caduceusPath, self._rootPath, "success.png")
			CaduceusHelper.copyResource(self._caduceusPath, self._rootPath, "failure.png")
			CaduceusHelper.copyResource(self._caduceusPath, self._rootPath, "favicon.ico")
		finally:
			outputFile.close()
	
	def _pageHeader(self):
		cssPath = CaduceusHelper.getHtmlPathToResource(self._reportPath, self._rootPath, "caduceus.css")
		logoPath = CaduceusHelper.getHtmlPathToResource(self._reportPath, self._rootPath, "caduceus-mini.png")
		
		img = ['success.png', 'failure.png'][self._result.hasFailed()]
		resultImgPath = CaduceusHelper.getHtmlPathToResource(self._reportPath, self._rootPath, img)
		favicoPath = CaduceusHelper.getHtmlPathToResource(self._reportPath, self._rootPath, "favicon.ico")

		html = "<html>\n<head>\n"
		html += '    <link rel="stylesheet" href="%s" type="text/css" />\n' % cssPath
		html += '    <link rel="shortcut icon" href="%s">' % favicoPath
		html += '</head>\n<body class="caduceus">\n'
		html += ReportHtml._createTag("div",
										[
										ReportHtml._createTag("img", None, {"src" : resultImgPath, "class": "result"}),
										ReportHtml._createTag("h1", "Execution Report"),
										ReportHtml._createTag("img", None, {"src" : logoPath, "class": "caduceus_logo"}),
										ReportHtml._createTag("br", None, {"style" : "clear: both"})
										],
										{"class": "caduceus_report_head"}
									)
		html += '<div class="caduceus_report">\n'
		return html
	
	def _pageFooter(self):
		footer  = "\n\t</div>\n"
		footer += ReportHtml._createTag("div",
										ReportHtml._createTag("span", "-- Generated %s --" % strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())),
										{"class": "caduceus_report_foot"}
									)										
		footer += "</body>\n</html>"
		return footer

	def _getCellCountClass(self, count, bError):
		if bError and (count > 0):
			return "count wrong"
		return "count"

	def _getAssertionsOverall(self, results):
		
		table = ""	
		rows = ""
		for tmpltResult in results.getTemplateResults():
			title = tmpltResult.getTitle() or "Untitled"
			url = CaduceusHelper.getHtmlRelativePath(tmpltResult.getTemplatePath(), self._reportPath)
			
			count = tmpltResult.getAssertionCount()
			failureCount = tmpltResult.getAssertionTypeCount(CaduceusTemplateResults.FAILURE)
			errorCount = tmpltResult.getAssertionTypeCount(CaduceusTemplateResults.ERROR)
					
			row  = ReportHtml._createTag("td", '<a href="%s">%s</a>' % (url, tmpltResult.getTitle()))
			row += ReportHtml._createTag("td", count, {'class': self._getCellCountClass(count, False)})
			row += ReportHtml._createTag("td", failureCount, {'class': self._getCellCountClass(failureCount, True)})
			row += ReportHtml._createTag("td", errorCount, {'class': self._getCellCountClass(errorCount, True)})
			
			rows += ReportHtml._createTag("tr", row)

		count = results.getAssertionCount()
		failureCount = results.getAssertionTypeCount(CaduceusTemplateResults.FAILURE)
		errorCount = results.getAssertionTypeCount(CaduceusTemplateResults.ERROR)

		row  = ReportHtml._createTag("td", "Total")
		row += ReportHtml._createTag("td", count, {'class': self._getCellCountClass(count, False)})
		row += ReportHtml._createTag("td", failureCount, {'class': self._getCellCountClass(failureCount, True)})
		row += ReportHtml._createTag("td", errorCount, {'class': self._getCellCountClass(errorCount, True)})
		rows += ReportHtml._createTag("tr", row, {'class': "total"})

		table = ReportHtml._createTable(["Page", "Assertions", "Failures", "Errors"], rows)

		return ReportHtml._createTag(	"div",
									   [ReportHtml._createTag("h2", "Pages tests results"), table])

	def _getAllErrors(self, tmpltResults):
		
		table = ""
		rows = ""
		for tmpltResult in tmpltResults:
			title = tmpltResult.getTitle() or "Untitled"
			url = CaduceusHelper.getHtmlRelativePath(tmpltResult.getTemplatePath(), self._reportPath)
			
			for errors in tmpltResult.getErrors():
				rows += "        <tr>\n        "
				rows += '<td><a href="%s#%s">%s - %s</a></td>' % (url, errors[0], tmpltResult.getTitle(), errors[0])
				rows += '<td class="message"><pre>%s</pre></td>' % errors[1]
				rows += '\n'
				rows += "       </tr>\n"

		if rows:
			table = ReportHtml._createTable(["Link", "message"], rows)
			return ReportHtml._createTag(	"div",
										   [ReportHtml._createTag("h2", "All errors"), table])
			
		return ""

	def _getAllFailures(self, tmpltResults):
		
		table = ""
		rows = ""
		for tmpltResult in tmpltResults:
			title = tmpltResult.getTitle() or "Untitled"
			url = CaduceusHelper.getHtmlRelativePath(tmpltResult.getTemplatePath(), self._reportPath)
			
			for errors in tmpltResult.getFailures():
				rows += "        <tr>\n        "
				rows += '<td><a href="%s#%s">%s - %s</a></td>' % (url, errors[0], tmpltResult.getTitle(), errors[0])
				rows += '<td class="message"><pre>%s</pre></td>' % errors[1]
				rows += '\n'
				rows += "       </tr>\n"

		if rows:
			table = ReportHtml._createTable(["Link", "message"], rows)
			return ReportHtml._createTag(	"div",
										   [ReportHtml._createTag("h2", "Tests failures"), table])
		return ""
	
	@staticmethod
	def _createTag(tag, content, attribs = None):
		attribs = attribs or {}
		htmlAttrib = ""
		for (attrib, value) in attribs.items():
			htmlAttrib += ' %s="%s"' % (attrib, value)

		if content is None:
			return "<%s%s />\n" % (tag, htmlAttrib)
		elif isinstance(content, list):
			return "<%s%s>%s</%s>\n" % (tag, htmlAttrib, "\n".join(content), tag)
		else:
			return "<%s%s>%s</%s>\n" % (tag, htmlAttrib, content, tag)

	@staticmethod
	def _createTable(headList, htmlRows, attribs = None):
		headRow = ""
		for item in headList:
			headRow += ReportHtml._createTag("th", item)
		
		return ReportHtml._createTag("table",
									 ReportHtml._createTag("tr", headRow) + htmlRows)

		

