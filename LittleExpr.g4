grammar LittleExpr;

keyword : KEYWORD;

//Basic statment
assign_stmt: assign_exp SEMICOLON;
assign_expr: IDENTIFIER COLEQ expr;
read_stmt: READ OPENPAR id_list CLOSEPAR;
write_stmt: WRITE OPENPAR id_list CLOSEPAR;
return_stmt: RETURN expr;

//EXPRESIONS
expr: expr_prefix factor
expr_prefix       -> expr_prefix factor addop | empty
factor            -> factor_prefix postfix_expr
factor_prefix     -> factor_prefix postfix_expr mulop | empty
postfix_expr      -> primary | call_expr
call_expr         -> id ( expr_list )
expr_list         -> expr expr_list_tail | empty
expr_list_tail    -> , expr expr_list_tail | empty
primary           -> ( expr ) | id | INTLITERAL | FLOATLITERAL
addop             -> + | -
mulop             -> * | /

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