#include<stdlib.h>
#include<stdio.h>
#include<unistd.h>


int overflow(){
    char buffer[24];
    puts("hello world!\n");
    read(0,buffer,100);
    return 0;
}


void backdoor(){
    execve("/bin/sh",0,0);
}


int main(){
    setbuf(stdin,0);
    setbuf(stdout,0);
    setbuf(stderr,0);
    overflow();
}