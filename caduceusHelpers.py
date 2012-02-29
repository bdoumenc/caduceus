import shutil
import os

class CaduceusHelper:

	@staticmethod
	def getRelativePath(target, base):
		"""
		Return a relative path to the target from either the current dir or an optional base dir.
		Base can be a directory specified either as absolute or relative to current dir.
		"""
		if not os.path.exists(target):
			raise OSError, 'Target does not exist: '+ target
	
		if not os.path.isdir(base):
			raise OSError, 'Base is not a directory or does not exist: '+ base
		
		if target == base:
			return ""
	
		base_list = (os.path.abspath(base)).split(os.sep)
		target_list = (os.path.abspath(target)).split(os.sep)
	
		# On the windows platform the target may be on a completely different drive from the base.
		if os.name in ['nt','dos','os2'] and base_list[0] <> target_list[0]:
			raise OSError, 'Target is on a different drive to base. Target: '+target_list[0].upper()+', base: '+base_list[0].upper()
	
		# Starting from the filepath root, work out how much of the filepath is
		# shared by base and target.
		for i in range(min(len(base_list), len(target_list))):
			if base_list[i] <> target_list[i]: break
		else:
			# If we broke out of the loop, i is pointing to the first differing path elements.
			# If we didn't break out of the loop, i is pointing to identical path elements.
			# Increment i so that in all cases it points to the first differing path elements.
			i+=1
	
		rel_list = [os.pardir] * (len(base_list)-i) + target_list[i:]
		return os.path.join(*rel_list)

	@staticmethod
	def getHtmlRelativePath(target, base):
		""" Copy a caduceus resource file inside output generation path.
		@param outputPath: Absolute path for gnerated output
		@param resFilename: Resourse file name to copy
		"""
		relativePath = CaduceusHelper.getRelativePath(target, base)
		return relativePath #.replace("\\", "/")
			
	@staticmethod
	def copyResource(caduceusPath, outputPath, resFilename):
		""" Copy a caduceus resource file inside output generation path.
		@param caduceusPath: Absolute path of caduceus generator
		@param outputPath: Absolute path for gnerated output
		@param resFilename: Resourse file name to copy
		"""
		CaduceusHelper.ensurePathExists(os.path.join(outputPath, "caduceus"))
		
		shutil.copyfile(os.path.join(caduceusPath, "resources", resFilename),
						os.path.join(outputPath, "caduceus", resFilename))
		
	@staticmethod
	def getHtmlPathToResource(htmlFilePath, outputPath, resFilename):
		""" Copy a caduceus resource file inside output generation path.
		@param outputPath: Absolute path for gnerated output
		@param resFilename: Resourse file name to copy
		"""
		relativePath = CaduceusHelper.getHtmlRelativePath(htmlFilePath, outputPath)
		return "%scaduceus/%s" % (relativePath, resFilename)

		
	@staticmethod
	def ensurePathExists(path):
		try:
			os.makedirs(path)
		except OSError:
			pass
