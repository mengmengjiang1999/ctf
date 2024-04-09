#include"base64.h"
#include<iostream>

int main(){
    char base64Char[65];
    cin>>base64Char;

    // cout<<base64Char<<endl;;

    string cipher;
    cin>>cipher;

    // cout<<cipher<<endl;

    char* message=new char(cipher.length()+1);
    message= base64Encode(cipher.c_str(),cipher.length()+1,base64Char);

    cout<<message;
    return 0;
}