lexer grammar LineLexer;

LINE : ~'\n'+ (EOL | EOF) ;
BLANK : EOL ;
fragment EOL : '\n' ;

