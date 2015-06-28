
A tool for iteratively developing Parsing Expression Grammars to parse
dockets[^1] and collapse them back into xml that reflects the parse tree.

Workflow:

1. Collect texts that need to be parsed. helper.py contains methods for
helping to collect texts to be parsed.  Texts should go in a directory
`texts/name\_of\_thing\_to\_be\_parsed/.`

2. Create your grammar in grammars/. See the grammars already present for examples.  

3. CustomNodeVisitorFactory is a class that creates a default NodeVisitor,
which parsimonious needs to transform the parse tree into something useful.
The Factory takes a list of terminals and nonterminals in a grammar and returns a
NodeVisitor class that collapses a parse tree into xml such that the tags
of the xml are the nonterminals of the grammar. The factory also takes
custom methods to override the default ones.
4. Write a script to test the grammar in tests/.
5. Make beautiful xml files out of raw text.




[^1] This could be a more general tool for developing Parsing Expression Grammars,
but I have focused on using it to parse dockets, so the tests and helper functions
all focus of parsing dockets.

