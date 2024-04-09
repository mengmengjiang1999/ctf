#include"base64.h"
#include<cstdio>
#include<iostream>

using namespace std;
int main(){
    string cipher;cin>>cipher;
    char* message=new char(cipher.length()+1);
    message= base64Encode(cipher.c_str(),cipher.length()+1);
    printf("%s",message);
    return 0;
}