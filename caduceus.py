#!/usr/bin/env python
import os
import sys
import shutil
from optparse import OptionParser
from caduceusHelpers import CaduceusHelper
from transform.templateParser import CaduceusTemplateParser
from transform.templateEntity import CaduceusResults, CaduceusTemplateResults
from report.reportHtml import ReportHtml
from report.reportJUnit import ReportJUnit

class Caduceus:
	REPORT_HTML = 0
	REPORT_JUNIT = 1
	
	def __init__(self, path, outputPath, reports):
		
		self.path = os.path.abspath(path)
		self.rootPath = self.path
		self.outputPath = os.path.abspath(outputPath)
		self.caduceusPath, _filename = os.path.split(os.path.abspath(__file__))
		self._reports = reports
		
		self.results = CaduceusResults()

	def run(self):
		
		if os.path.isfile(self.path):
			print "Ouput must be a directory !"
			#path, filename = os.path.split(self.path)
			#self._processFile(path, filename, self.outputPath)
			return
		
		if os.path.isdir(self.path):
			self._processDirectory(self.path, self.outputPath)
			
			# copy css file to output path
			CaduceusHelper.copyResource(self.caduceusPath, self.outputPath, "caduceus.css")
			
		# Print statistics
		print "Assertions: %d" % self.results.getAssertionCount()
		print "Success: %d" % self.results.getAssertionTypeCount(CaduceusTemplateResults.SUCCESS)
		print "Failures: %d" % self.results.getAssertionTypeCount(CaduceusTemplateResults.FAILURE)
		print "Errors: %d" % self.results.getAssertionTypeCount(CaduceusTemplateResults.ERROR)
		
		# Generate execution report
		if self._reports[self.REPORT_HTML]:
			report = ReportHtml(self.results, self.outputPath, self.caduceusPath)
			report.generate()
		
		if self._reports[self.REPORT_JUNIT]:
			report = ReportJUnit(self.results, self.outputPath, self.caduceusPath)
			report.generate()
        return self.results.failures == 0 and self.results.errors == 0
			
	def _processDirectory(self, path, outPath):
		print "  Processing path %s..." % path
		entries = os.listdir(path)
		for entry in entries:
			entryFullPath = os.path.join(path, entry)
			
			if os.path.isfile(entryFullPath):
				self._processFile(path, entry, outPath)
			elif os.path.isdir(entryFullPath) and (entry != ".svn"):
				self._processDirectory(entryFullPath, os.path.join(outPath, entry))
			else:
				print "Not handling %s" % entryFullPath
				
				
	def _processFile(self, filePath, fileName, outFilePath):
		inputFullPath = os.path.join(filePath, fileName)
		inputBasenamePath, ext = os.path.splitext(inputFullPath)
		outputFullPath = os.path.join(outFilePath, fileName)
		
		if ext == ".html":
			if fileName[0] != "_":
				print "  Processing file %s..." % inputFullPath
			
				template = CaduceusTemplateParser.parseTemplateFile(inputFullPath, self.rootPath, self.caduceusPath)	
				if template:
					CaduceusHelper.ensurePathExists(outFilePath)
					
					outputFile = open(outputFullPath, 'w')
					try:
						# Load controller for file
						dictGlob = {}
						dictLoc = {}
						
						try:
							controllerName, _ext = os.path.splitext(fileName)
							controllerName = controllerName + "Test"
							
							sys.path.append(os.path.dirname(inputFullPath))
							exec ("from %s import %s" % (controllerName, controllerName)) in dictGlob, dictLoc

							# We must copy local dictionnary into global, to allow some symbols resolution
							dictGlob.update(dictLoc)
							
							# Instanciate a controller in parsing context 
							exec ("__caduceus_controler__ = %s()" % controllerName) in dictGlob, dictLoc
							
							# Bind all controller public methods as global methods 
							for key in dir(dictLoc[controllerName]):
								if key[0] != "_":
									proc = eval("__caduceus_controler__.%s" % key, dictGlob, dictLoc)
									dictLoc[key] = proc
						except IOError:
							print "Warning: No controller file for '%s'" % inputFullPath
						except ImportError:
							print "Warning: No controller file for '%s'" % inputFullPath
							
						# Render template using context
						tmplResults = CaduceusTemplateResults(outputFullPath)
						result = template.render(dictGlob, dictLoc, tmplResults)
						self.results.addTemplateResult(tmplResults)
						
						outputFile.write(result)
					finally:
						outputFile.close()
			else:
				print "  Skipping partial %s" % inputFullPath
		elif ext not in [".py", ".pyc"]:
			# File may be stylesheet, javasript or other resource
			# copy as it
			print "  Copy file %s..." % inputFullPath
			
			CaduceusHelper.ensurePathExists(outFilePath)		
			shutil.copyfile(inputFullPath, outputFullPath)

if __name__ == "__main__":
	parser = OptionParser()
    parser.add_option("-o", "--output", dest="outputPath", help="Output path", metavar="OUTPUT", default="")
	parser.add_option("-s", "--src", dest="srcPath", help="Base directory", metavar="INPUT", default=None)
	parser.add_option("-r", "--report-html", dest="reportHtml", help="Base directory", metavar="INPUT", default=True)
	parser.add_option("-j", "--junit", dest="reportJUnit", help="Base directory", metavar="INPUT", default=False)

	(options, args) = parser.parse_args()
	
	if options.srcPath and options.outputPath:
		caduceus = Caduceus(options.srcPath, options.outputPath,
							[options.reportHtml, options.reportJUnit])
        sys.exit([1, 0][caduceus.run()])
	else:
		parser.print_help()

