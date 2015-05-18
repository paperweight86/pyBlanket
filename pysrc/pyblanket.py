"""
	pyBlanket by Paperweight86
	Version: Prototype 1
	Description: Takes an AST digest from pyClump and C++ library project then generates 
	a wrapper for the given language. Currently only intends to support c#.
"""

import json, pprint, pystache
import pyclump

class Transform:
	
	def __init__(self):
		self.stuff = None

	def Transform( self, input ):
		pass

class Pipeline:

	def __init__(self):

		self.steps = []

	def AddStep( self, step ):

		self.steps.push_back(step)

	def ClearSteps( self ):

		self.steps = []

	def ExecuteSteps( self ):

		for step in self.steps:
			step.Transform(output)


dumpPath = r'C:\Projects\dump.json'
projPath = r'C:\Projects\oldstructure\src\tod\Tod.vcxproj'
namespaces = ['tod']
pyclump.DumpAST(projPath, namespaces, dumpPath)

f = open(r'C:\Projects\dump.json', 'r')
data = f.read()
meta = json.loads(data)
f.close()

# TODO: transform dump.json into dump.cppcli.json into dump.<class>.h/dump.<class>.cpp/dump.csproj/dump.sln
for clas in meta:

	if clas['subtype'] == 'factory':
		clas['subtype'] = 'static class'
	elif clas['subtype'] == 'class':
		clas['subtype'] = 'ref class'

	clas['projectname'] = 'tod'

f = open(r'..\templates\cppcli.pst', 'r')
template = f.read()
f.close()

outputFolder = "..\examples\tod"

for clas in meta:
	print pystache.render(template, clas)
