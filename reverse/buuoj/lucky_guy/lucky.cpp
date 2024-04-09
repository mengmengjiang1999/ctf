

#include<iostream>
#include <cstring>

using namespace std;
int main(){

char* f2;
long long s = 9180147350284624745LL;
strcat(&f2, (const char *)&s);
memset(&s, 0, 0x28uLL);
    strcat((char *)&s, &f2);
    printf("%s", &s);
    for (int j = 0; j <= 7; ++j )
    {
        char v1; // al
        if ( j % 2 == 1 ){
        cout<< *(&f2 + j);
        // v1 = *(&f2 + j) - 2;
        }
        else{
        // v1 = *(&f2 + j) - 1;
        }
        // *(&f2 + j) = v1;
    }
strcat(&f2, (const char *)&s);
strcat((char *)&s, &f2);
printf("%s", &s);
return 0;
}