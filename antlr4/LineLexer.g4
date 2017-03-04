lexer grammar LineLexer;
options { superClass=app.antlr.custom.CustomLexer; }

LINE : ~'\n'+ (EOL | EOF) ;
BLANK : EOL ;
fragment EOL : '\n' ;

