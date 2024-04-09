#include<iostream>
#include<cstdio>
using namespace std;



int main(){

char *v3[3]; // [rsp+18h] [rbp-20h]

  v3[0] = "Dufhbmf";
  v3[1] = "pG`imos";
  v3[2] = "ewUglpt";
  for ( int i = 0; i <= 11; ++i )
  {
    printf("%c",v3[i % 3][2 * (i / 3)] -1);
    }
}

