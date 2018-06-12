import re
import os

def printNonVarPartOfParser(grammarFile, nonVarStringParts, pRuleList):
	for i, rule in enumerate(pRuleList):
		# This is done to make the parser case-sensitivity resistant
		parserLine = rule + " -> "
		for i, char in enumerate(nonVarStringParts[i]):
			if char == ' ' or char == ',' or char == '-':
				parserLine += "["+char+"] "
			else:
				parserLine += "["+char.upper()+char.lower()+"] "
		grammarFile.write(parserLine+"\n")

def printVarPartOfParser(grammarFile, varNames, varTypes):
	for i, varName in enumerate(varNames):
		parserLine = varName+" -> "
		if varTypes[i] == "string":
			parserLine += "[a-zA-Z0-9 -.,]:+"
		elif varTypes[i] == "int":
			parserLine += "[0-9]:+"
		grammarFile.write(parserLine+"\n")

def printTopPartOfParser(grammarFile, pRuleList, varNames, lastElementEmpty, number):
	parserLine = ""
	for i in range(0,len(pRuleList)):
		if i != len(pRuleList)-1:
			parserLine += pRuleList[i]+' '+varNames[i]+' '
		else:
			if (not lastElementEmpty):
				parserLine += pRuleList[i]
			else:
				parserLine += pRuleList[i]+' '+varNames[i]
	grammarFile.write("statement -> "+ parserLine + " {%"+"\n")
	grammarFile.write("\tfunction(data) {\n\t\treturn {"+"\n")
	grammarFile.write("\t\t\tstatementNo: "+str(number)+","+"\n")
	for i, varName in enumerate(varNames):
		if i < len(varNames)-1:
			grammarFile.write("\t\t\t"+varName+": "+"data["+str(2*(i+1)-1)+"],"+"\n")
		else:
			grammarFile.write("\t\t\t"+varName+": "+"data["+str(2*(i+1)-1)+"]"+"\n")
	grammarFile.write("\t\t};"+"\n")
	grammarFile.write("\t}"+"\n")
	grammarFile.write("%}"+"\n")

def generateParsingStatementsForRule(grammarFile, englishRule, number):
	# Stores $[name1](string)
	stringVarNames = re.findall(r'\$\[.*?\]\(.*?\)',englishRule)
	# Stores name1
	varNames = re.findall(r'\$\[(.*?)\]\(.*?\)',englishRule)
	varNamesOriginal = varNames
	# Add a prefix to varName to prevent conflicting variable names in parser problems
	varNames = ["english2cypher"+str(number)+varName for varName in varNames]
	# Stroes string
	varTypes = re.findall(r'\$\[.*?\]\((.*?)\)',englishRule)

	# Safety step to make typename case-sensitive lower-case
	varTypes = [varType.lower() for varType in varTypes]

	nonVarString = re.sub(r'(\$\[.*?\]\(.*?\))',',',englishRule)
	nonVarStringParts = nonVarString.split(',')

	# Corner case handling
	lastElementEmpty = False
	if len(nonVarStringParts[len(nonVarStringParts)-1]) == 0:
		nonVarStringParts.pop()
		lastElementEmpty = True

	pRuleList = []

	for i, part in enumerate(nonVarStringParts):
		pRuleList.append('string'+str(number)+str(i+1))

	printTopPartOfParser(grammarFile, pRuleList, varNames, lastElementEmpty, number)
	printNonVarPartOfParser(grammarFile, nonVarStringParts, pRuleList)
	printVarPartOfParser(grammarFile, varNames, varTypes)

	# Needed for generating parser code on javascript end
	return varNamesOriginal, varTypes

def generateJSParserFunction(cyphersFile, cypher, number, varNames, varTypes):
	
	prefix = 'english2cypher'+str(number)

	cyphersFile.write('if(result.statementNo=='+str(number)+'){\n')
	# cyphersFile.write('\tcase '+str(number)+':'+'\n')

	# First step is to replace all $[name1] etc to their value i.e 'val(name1)' if name1 is of type string
	for i, varName in enumerate(varNames):
		if varTypes[i] == 'string':
			cypher = cypher.replace("$["+varName+"]","\"\'+"+"result."+prefix+varName+"[0].join(\"\")"+"+\'\"")
		elif varTypes[i] == 'int':
			cypher = cypher.replace("$["+varName+"]","\'+"+"result."+prefix+varName+"[0].join(\"\")+\'")

	cyphersFile.write("\t\tcode += \'"+cypher.replace('\n','\\n\\\n')+"\';\n")
	cyphersFile.write("}\n")

rulesFileName = 'rules.txt'
rulesFile = open(rulesFileName, "r")

englishRules = []

for line in rulesFile:
	if len(line.strip()) > 2:
		# Remove newline characters in statements
		englishRules.append(line.strip('\n'))

if os.path.exists('./grammar.ne'):
    os.remove('./grammar.ne')

grammarFile = open('./grammar.ne', 'w')
grammarFile.write('main -> (statement):+'+'\n')

# Needed for generating parser code on javascript end
varDict = {}

for i, englishRule in enumerate(englishRules):
	lvarNames, lvarTypes = generateParsingStatementsForRule(grammarFile, englishRule, i+1)
	varDict[str(i+1)] = [lvarNames, lvarTypes]
	grammarFile.write('\n')

grammarFile.close()

cyphersFileName = 'cyphers.txt'
cyphersFile = open(cyphersFileName, "r")

cyphers = []

cypherPart = ''
for line in cyphersFile:
	if len(line.strip('\n')) > 2:
		cypherPart += line.strip('\n')+'\n'
	else:
		cyphers.append(cypherPart)
		cypherPart = ''

if cypherPart.strip('\n'):
	cyphers.append(cypherPart)


if os.path.exists('./enlish2cypher.js'):
    os.remove('./english2cypher.js')

cyphersFile = open('./english2cypher.js', 'w')
cyphersFile.write('function englishParser(searchTextBoxId, codeMirrorEditor){'+'\n')
cyphersFile.write('\tconst parser = new nearley.Parser(nearley.Grammar.fromCompiled(grammar));'+'\n')
cyphersFile.write('\tvar text = document.getElementById(searchTextBoxId).value;'+'\n')
cyphersFile.write('\tparser.feed(text);'+'\n')
cyphersFile.write('\tvar text = document.getElementById(searchTextBoxId).value;'+'\n')
cyphersFile.write('\tvar code = "";'+'\n')
cyphersFile.write('\tvar result = parser.results[0][0][0][0];'+'\n')

for i, cypher in enumerate(cyphers):
	[lvarNames, lvarTypes] = varDict[str(i+1)]
	generateJSParserFunction(cyphersFile, cypher, i+1, lvarNames, lvarTypes)
	cyphersFile.write('\n')

cyphersFile.write('\tcodeMirrorEditor.setValue(code);'+'\n')
cyphersFile.write('};')
cyphersFile.close()



