lexer grammar ParagraphLexer;
options { superClass=app.antlr.custom.CustomLexer; }

PARAGRAPH : LINE+ ;
BLANK : EOL+ -> skip ;
fragment LINE : ~'\n'+ (EOL | EOF) ;
fragment EOL : '\n' ;

