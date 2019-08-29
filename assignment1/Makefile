build: main.cpp
	@g++ -o tnmp main.cpp -lpthread -lm -lX11
debug:
	@g++ -o tnmp main.cpp -g -lpthread -lm -lX11
run: build
	@./tnmp $(image)
