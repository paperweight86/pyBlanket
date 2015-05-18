"""
	pyBlanket by Paperweight86
	Version: Prototype 1
	Description: Takes an AST digest from pyClump and C++ library project then generates 
	a wrapper for the given language. Currently only intends to support c#.
"""

import json, pprint, pystache

f = open(r'C:\Projects\dump.json', 'r')
data = f.read()
meta = json.loads(data)
f.close()

first = meta[0]
pprint.pprint(first)

# TODO: transform dump.json into dump.cppcli.json into dump.<class>.h/dump.<class>.cpp/dump.csproj/dump.sln
for clas in meta:

	if clas['subtype'] == 'factory':
		clas['subtype'] = 'static class'
	elif clas['subtype'] == 'class':
		clas['subtype'] = 'ref class'

template = """
#pragma unmanaged
#include "{{filepath}}"
#pragma managed

namespace Dump.Wrapper
{
	public {{subtype}} {{name}}
	{
		
	}
}

"""

for clas in meta:
	print pystache.render(template, clas)
