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
		pass

	def Execute( self ):
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
			output = step.Execute()

def main():
	dumpPath = r'..\examples\dump.cpp.json'
	projPath = r'C:\Users\paperweight\Source\Repos\Tod\Tod.vcxproj'
	namespaces = ['tod']
	moduleNames = ['cppcli_blanket']
	modules = map(__import__, moduleNames)

	pyclump.DumpAST(projPath, namespaces, dumpPath)

	f = open(dumpPath, 'r')
	data = f.read()
	meta = json.loads(data)
	f.close()

	a = modules[0].Transform(meta)
	a.Execute()

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

	outputFolder = ".\examples"
	print meta
	for clas in meta:
		print pystache.render(template, clas)

if __name__ == "__main__":
    main()
