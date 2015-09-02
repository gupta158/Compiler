grammar LittleExpr;

keyword : KEYWORD;


KEYWORD: PROGRAM
	   | BEGIN
	   | END
	   | FUNCTION
	   | READ
	   | WRITE
	   | IF
	   | ELSE
	   | FI
	   | FOR
	   | ROF
	   | CONTINUE
	   | BREAK
	   | RETURN
	   | INT
	   | VOID
	   | STRING
	   | FLOAT ;

IDENTIFIER: [a-zA-Z][a-zA-Z0-9]* ;

OPERATOR: MUL
		| ADD
		| SUB
		| DIV
		| EQU
		| NEQ
		| LT
		| LEQ
		| GT
		| GEQ
		| OPENPAR
		| CLOSEPAR
		| SEMICOLON
		| COMMA
		| COLEQ
		;

STRINGLITERAL: '"'('\\"' | ~['"'])*'"';

FLOATLITERAL: [0-9]*'.'[0-9]+;
INTLITERAL: [0-9]+;

PROGRAM: 'PROGRAM';
BEGIN: 'BEGIN';
END: 'END';
FUNCTION: 'FUNCTION';
READ: 'READ';
WRITE: 'WRITE';
IF: 'IF';
ELSE: 'ELSE';
FI: 'FI';
FOR: 'FOR';
ROF: 'ROF';
CONTINUE: 'CONTINUE';
BREAK: 'BREAK';
INT: 'INT';
VOID: 'VOID';
STRING: 'STRING';
FLOAT: 'FLOAT';
RETURN: 'RETURN';

MUL: '*';
ADD: '+';
SUB: '-';
DIV: '/';
EQU: '=';
NEQ: '!=';
LT: '<';
LEQ: '<=';
GT: '>';
GEQ: '>=';
OPENPAR: '(';
CLOSEPAR: ')';
SEMICOLON: ';';
COMMA: ',';
COLEQ: ':=';


WS: [ \r\t\n]+ -> skip ;

COMMENT: '--'~[NEWLINE]* '\r'? NEWLINE -> skip;

NEWLINE: '\n';

/*
	todo:
	define operators
	define literals
	define keywords in detail
	*/