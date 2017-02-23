lexer grammar LineLexer;

LINE : .+? EOL ;
BLANK : EOL ;
fragment EOL : '\n' ;
