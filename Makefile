all: group compiler

group:
	echo "Manish Gupta (gupta158), James Alliger (jalliger)"

compiler: 
	@chmod +x setupScript
	@chmod +x Micro
	@./setupScript Install

clean:
	@chmod +x setupScript
	@./setupScript Clean
