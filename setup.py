from distutils.core import setup
setup(	name='caduceus',
		version='1.0',
		description='Caduceus generator',
		author='Alexandre Prudent',
		author_email='padragn@gmail.com',
		url='http://',
		py_modules=['caduceus', 'caduceusHelpers', 'transform/'],
		packages=['transform', 'report'],
		data_files=[('resources', ['resources/*.*']),]
		)