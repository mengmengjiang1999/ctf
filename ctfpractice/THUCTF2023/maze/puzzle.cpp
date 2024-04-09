#include<iostream>
#include<cstring>
using namespace std;

string maze="*** *******   *    ** * * ** ** *   ** ***** *** **   S*** ********* T";

static const string flag1="THUCTF{m1sc_1$_int3re5t!n9}";

int main(){
    int x=5;
    int y=4;
    string input;
    cin>>input;
    if(input.length()!=14){
        return 0;
    }else{
        for(int i=0;i<input.length();i++){
            if(input[i]=='a'){
                y-=1;
            }else if(input[i]=='s'){
                x+=1;
            }else if(input[i]=='w'){
                x-=1;
            }else if(input[i]=='d'){
                y+=1;
            }
            if(x<0||x>6||y<0||y>9){
                return 0;
            }
        }
        int z=10*x+y;
        if(maze[z]==' '){
            return 0;
        }else if (maze[z]=='T'){
            cout<<"you find the flag2! flag2 is THUCTF{"<<input<<"}";
        }
    }
    return 0;
}