
"""
    pyClump by Paperweight86
    Version: Prototype 1
    Description: A small wrapper for libclang which takes a C++ vs project file for a library 
    and a given namespace, using the header files generates a json dump of the presumed 
    exposed classes. Basically a digest of the exposed part of the libs AST.
"""

import sys, os.path
import xml.etree.ElementTree as ET
import clang.cindex as cindex
import pprint
import json

# TODO: do we need this?
#def find_typerefs(node, typename):
#    """ Find all references to the type named 'typename'
#    """
#    if node.kind.is_reference():
#        if node.referenced.displayname == typename:#ref_node.spelling == typename:
#            print 'Found %s [line=%s, col=%s]' % (
#                typename, node.location.line, node.location.column)
#    # Recurse for children of this node
#    for c in node.get_children():
#        find_typerefs(c, typename)

global NAMESPACE_FILTER
global CLASSES
CLASSES = []
EXPORT = []
INDEX = []

def type_to_json(ty, typeDict):

    if typeDict is None:
        typeDict = {}

    # Handle pointer & reference types
    if ty.kind == cindex.TypeKind.POINTER or ty.kind == cindex.TypeKind.LVALUEREFERENCE:
        if typeDict.has_key("ref"):
            typeDict["ref"].append(str(ty.kind.name))
        else:
            typeDict["ref"] = [str(ty.kind.name),]
        return type_to_json(ty.get_pointee(), typeDict)
    elif ty.kind == cindex.TypeKind.RECORD:
        typeDict["type"] = ty.spelling
    elif ty.kind == cindex.TypeKind.ENUM:
        typeDict["type"] = ty.spelling
    else:
        typeDict["type"] = ty.kind.name

    if ty.is_const_qualified():
        if not typeDict.has_key("spec"):
            typeDict["spec"] = []
        typeDict["spec"].append("constant")

    return typeDict


def show_types(parentNode, node, curLevel):
    
    curLevel.append(node.displayname)

    global NAMESPACE_FILTER

    if node.kind in (cindex.CursorKind.CLASS_DECL, cindex.CursorKind.STRUCT_DECL, cindex.CursorKind.ENUM_DECL, cindex.CursorKind.NAMESPACE, cindex.CursorKind.NAMESPACE_REF, cindex.CursorKind.TRANSLATION_UNIT) :

        if node.kind in (cindex.CursorKind.CLASS_DECL, cindex.CursorKind.STRUCT_DECL) and not node.displayname in CLASSES and curLevel[-2] in NAMESPACE_FILTER:
            print " > ".join(curLevel)
            CLASSES.append(node.displayname)
            subtype = "";
            if node.displayname.startswith('I'):
                subtype = "interface"
            elif node.displayname.startswith('S'):
                subtype = "struct"
            else:
                subtype = "class"

            if node.displayname.endswith('Factory'):
                subtype = "factory"

            print subtype

            EXPORT.append(node)

            properties = []
            INDEX.append({
                "filepath":curLevel[0],
                "name":node.displayname,
                "subtype": subtype,
                "functions":[],
                "properties":properties
                })

            children = node.get_children()

            for c in children:
                show_types(node, c, curLevel)

        elif node.kind == cindex.CursorKind.ENUM_DECL and not node.displayname in CLASSES and curLevel[-2] in NAMESPACE_FILTER:
            print " > ".join(curLevel)

            subtype = "enum"

            print subtype

            CLASSES.append(node.displayname)

            EXPORT.append(node)

            properties = []
            INDEX.append({
                "filepath":curLevel[0],
                "name":node.displayname,
                "subtype": subtype,
                "functions":[],
                "properties":properties
                })

            children = node.get_children()

            for c in children:
                show_types(node, c, curLevel)

        elif node.kind in (cindex.CursorKind.NAMESPACE, cindex.CursorKind.NAMESPACE_REF, cindex.CursorKind.TRANSLATION_UNIT) :
            children = node.get_children()

            for c in children:
                show_types(node, c, curLevel)

    elif parentNode is not None and parentNode in EXPORT and node.kind in (cindex.CursorKind.CXX_METHOD,) and node.access_specifier == cindex.AccessSpecifier.PUBLIC:
        print " > ".join(curLevel) + " > " + node.result_type.spelling + " " + node.displayname
        
        if node.is_static_method():
            print "static"
        parameters = []
        for arg in node.get_arguments():
            parameters.append({
                    "name": arg.displayname,
                    "type": type_to_json(arg.type, None)
                })
        INDEX[-1]["functions"].append({
                "name": node.spelling,
                "type": type_to_json(node.result_type, None),
                "parameters": parameters,
            })

    elif parentNode is not None and parentNode in EXPORT and node.kind in (cindex.CursorKind.FIELD_DECL,) and node.access_specifier == cindex.AccessSpecifier.PUBLIC:
        INDEX[-1]["properties"].append({
                "name": node.displayname,
                "type": type_to_json(node.type, None)
            })

    elif parentNode is not None and parentNode in EXPORT and node.kind == cindex.CursorKind.ENUM_CONSTANT_DECL:

        INDEX[-1]["properties"].append({
                "name": node.displayname,
                "value": node.enum_value
            })
    
    #else:
    #    print parentNode.spelling
    #    print node.kind

    curLevel.pop()

def getFilesWithExtension(dir, exts):
    files = []
    for dirname, dirnames, filenames in os.walk(dir):
        for filename in [x for x in filenames if os.path.splitext(x)[-1] in exts]:
            files.append(os.path.join(dirname, filename))
    return files

def GetIncludeDirsFromVCProj( projPath ):

    projTree = ET.parse(projPath)

    compiled = projTree.findall('.//{http://schemas.microsoft.com/developer/msbuild/2003}ClCompile')
    included = projTree.findall('.//{http://schemas.microsoft.com/developer/msbuild/2003}ClInclude')
    incDirs = projTree.findall('.//{http://schemas.microsoft.com/developer/msbuild/2003}AdditionalIncludeDirectories')

    uniqueIncDirs = []
    for includeDir in incDirs:
        newIncs = includeDir.text.split(';')
        for incPath in newIncs:
            if not incPath in uniqueIncDirs and incPath != ".\\":
                uniqueIncDirs.append(incPath)

    basePath = os.path.dirname(projPath)

    searchDirs = [os.path.realpath(os.path.join(basePath, x)) for x in uniqueIncDirs]

    files = []
    for searchDir in searchDirs:
        files += getFilesWithExtension(searchDir, ['.cpp','.h', '.hpp'])

    #compiled = [os.path.realpath(os.path.join(basePath,x.get('Include'))) for x in compiled if not x.get('Include') is None]
    included = [os.path.realpath(os.path.join(basePath,x.get('Include'))) for x in included if not x.get('Include') is None]

    return included + files

def CheckForMissingFiles(files):

    missingfiles = []
    #missingfiles += [x for x in compiled if not os.path.exists(x)]
    missingfiles += [x for x in included if not os.path.exists(x)]

    if missingfiles:
        print "Some files are missing:\n" + "\n".join(missingfiles)
        exit(1)

def GenerateASTDump( files ):
    allFiles = list(set(files))
    index = cindex.Index.create()
    for cppfile in allFiles:
        tu = index.parse(cppfile, args=['-x', 'c++'])
        #print 'Reading', tu.spelling
        #find_typerefs(tu.cursor, 'Person')
        show_types(None, tu.cursor, [])
    return index

def DumpAST( inputFile, namespaceFilters, outputFile ):
    included = GetIncludeDirsFromVCProj(inputFile)

    global NAMESPACE_FILTER
    NAMESPACE_FILTER = namespaceFilters

    INDEX = []
    GenerateASTDump( included )

    f = open(outputFile, 'w')
    f.writelines(json.dumps(INDEX, sort_keys=True, indent=1))
    f.close()
