lexer grammar ParagraphLexer;

PARAGRAPH : LINE+ ;
BLANK : EOL+ -> skip ;
fragment LINE : ~'\n'+ (EOL | EOF) ;
fragment EOL : '\n' ;

