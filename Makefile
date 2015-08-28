all: group compiler

group:
	echo "Manish Gupta (gupta158), James Alliger (jalliger)"

compiler: helloworld

helloworld: helloworld.c
	$(CC) -o $@ $<

clean:
	rm helloworld