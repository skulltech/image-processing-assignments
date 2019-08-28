build: main.cpp
	@g++ -o tnmp reinhard.cpp -lpthread -lm -lX11
debug:
	@g++ -o tnmp reinhard.cpp -g -lpthread -lm -lX11
run: build
	@./tnmp $(image)
