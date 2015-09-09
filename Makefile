all: group compiler

group:
	@echo "Manish Gupta (gupta158), James Alliger (jalliger)"

compiler: 
	@chmod +x src/setupScript
	@chmod +x Micro
	@./src/setupScript Install

clean:
	@chmod +x src/setupScript
	@./src/setupScript Clean
