OBJS=thostmduserapi_wrap.o
INCLUDE=-I./ -I/usr/local/include/python3.8
TARGET=libthostmduserapi_wrap.so
CPPFLAG=-shared -fPIC -v
CC=gcc
LDLIB=-L. -lthostmduserapi
$(TARGET) : $(OBJS)
	$(CC) $(CPPFLAG) $(INCLUDE) -o $(TARGET) $(OBJS) $(LDLIB) ./libiconv.so.2.6.0
$(OBJS) : %.o : %.cpp
	$(CC) -c -fPIC -v $(INCLUDE) $< -o $@
clean:
	-rm -f $(OBJS)
	-rm -f $(TARGET)
install:
	cp $(TARGET) /usr/local/lib