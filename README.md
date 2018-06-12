# Convert English sentences to cypher queries

This repository contains code to generate a parser for converting english to [cypher](https://neo4j.com/developer/cypher-query-language/). The only input needed are english sentences and their corresponding cyphers. The generated parser is an [earley parser](https://en.wikipedia.org/wiki/Earley_parser). This is similar to the template phrases feature offered in [neo4j bloom](https://neo4j.com/blog/introducing-neo4j-bloom-graph-data-visualization-for-everyone/).

## Motivation

Though [neo4j](https://neo4j.com/)'s cypher language is intuitive and great for making requests on a neo4j database, often neo4j is running on the backend of your project/website and for making requests from the front-end one needs generate cypher queries. Since cypher is a query language and takes some time to learn, it would be easier if there was a tool to convert natural english sentences to cyphers. This would allow any consumer/common man to make queries to neo4j database (Note: These queries need to be of a pre-defined structure).

## TODO
- [x] Add case-insensitiveness for english queries.
- [x] Add support for cypher syntax highlighting using code mirror.
- [x] Add support for string and int data types.
- [ ] Add support for list of strings.
- [ ] Add support for auto-suggest in text-box.
- [ ] Write a blog post explaining everything.

## Setup/Installation

First install [nearley.js](https://nearley.js.org/) on your system using the following command:

```
npm install -g nearley
npm install --save nearley
```

Download the codemirror.zip file from [here](https://codemirror.net/codemirror.zip).

Enter rules (english sentences) in `rules.txt` and corresponding cyphers in `cyphers.txt` separated by a newline (having a newline in between is a must). An example has been explained in the next section.

Next, run the following commands:

```
python generate.py
nearleyc grammar.ne -o grammar.js
```

The first command would generate `grammar.ne` and `english2cypher.js` respectively. The second command would generate `grammar.js`.

Copy `english2cypher.js`, `node_modules` directory, `codemirror-5.38.0` directory and `grammar.js` to your website directory and add the following lines in `index.html`:

```
<script src="node_modules/nearley/lib/nearley.js"></script>
<script src="./english2cypher.js"></script>
<script src="./grammar.js"></script>

<!-- Codemirror for syntax highlighting -->
<link rel="stylesheet" href="./codemirror-5.38.0/lib/codemirror.css">
<link rel="stylesheet" href="./codemirror-5.38.0/theme/neo.css">
<script src="./codemirror-5.38.0/lib/codemirror.js"></script>
<script src="./codemirror-5.38.0/mode/cypher/cypher.js"></script>

<input class="input" type="text" placeholder="English Query" id="englishTextBoxId">

<button onclick="myFunction()">Convert 2 Cypher</button>

<input type="text" id="cypherBox" class="bar" wrap="hard" style="width:100%;  align:center;" class="form-control" >
<script>
  var codeMirrorEditor = CodeMirror.fromTextArea(document.getElementById("cypherBox"), {
    mode:'cypher',
    lineNumbers: true,
    lineWrapping: true,
    scrollbarStyle: "native",
    theme: 'neo'
});
  var code = 
``;
  codeMirrorEditor.setValue(code);
</script>

<script>
function myFunction(){
englishParser("englishTextBoxId", codeMirrorEditor);
};
</script>
```

**Note:** Styling is up to you. The above html file is just barebones and it would result in a website that would look like this:
![Default Appearance](https://github.com/gsssrao/english2cypher/appearance.png)

## Example

Consider the following example where a neo4j database has two kinds of nodes `person` and `company` with `name` as their properties and `WORKS` as the relationship. And now say that we want to do the following queries:

- Find all the companies a person is working with. This can have the following english phrase:

```
Companies that person $[personName](string) is working with
```
with the corresponding cypher:

```
MATCH (a:person)-[:WORKS]-(b:company)
WHERE a.name = $[personName]
RETURN a
```

- Find the people working for a given company. This can have the following english phrase:

```
All the people working for the company $[companyName](string)
```
with the corresponding cypher:
```
MATCH (a:person)-[:WORKS]-(b:company)
WHERE b.name = $[companyName]
RETURN a
```

- Find all the the people limit to 100. This can have the following english phrase:

```
All the people in the database limit to $[number](int)
```
with the corresponding cypher:
```
MATCH (a:person)
RETURN distinct a.name LIMIT $[number]
```

- Find all the companies. This can have the following english phrase:

```
All the companies in the database
```
with the corresponding cypher:
```
MATCH (b:company)
RETURN distinct b.name
```

**Note:** string can have the following characters `a-zA-Z0-9 -.,` whereas int can have only `0-9`






