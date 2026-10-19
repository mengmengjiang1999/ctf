FLAGS= -g -shared -o 
INCLUDE= -I$(CUBESYSPATH)/include -I$(CUBE_PATH)/include -I$(CUBE_TCM_PATH)/include -I$(CUBE_TCM_PLUGIN)/include -I$(CUBEAPPPATH)/include
CFLAGS= -g -c -fPIC -DUSER_MODE $(INCLUDE)
CC=gcc
CCP=g++
PLUGIN=key_server_return
PLUGIN_OBJ=
TEST_LIB= -L$(CUBELIBPATH)/lib -lmessage -lmemdb -lconnector -lstruct -lcrypto_func -lpthread
LOCALLIB=-L$(CUBE_TCM_PATH)/locallib/bin -ltcm
 
main: lib$(PLUGIN).so
lib$(PLUGIN).so:  $(PLUGIN).o $(PLUGIN_PROC_OBJ) $(INIT_DB_OBJ)
	$(CC) $(FLAGS) lib$(PLUGIN).so $(PLUGIN).o $(PLUGIN_OBJ) $(TEST_LIB) $(LOCALLIB)
	mv lib$(PLUGIN).so $(CUBEAPPPATH)/plugin
	cp $(PLUGIN).cfg $(CUBEAPPPATH)/plugin
$(PLUGIN).o: $(PLUGIN).c $(PLUGIN).h
	$(CC) $(CFLAGS) $(PLUGIN).c
clean:
	rm -f lib$(PLUGIN).so
	rm  *.o *~
