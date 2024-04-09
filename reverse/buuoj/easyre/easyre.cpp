//
//  main.cpp
//  ctf
//
//  Created by chenzm on 2023/9/3.
//  Copyright © 2023 chenzm. All rights reserved.
//

#include <cstdio>

using namespace std;

int main(int argc, const char **argv, const char **envp)
{
  char v4; // [esp+12h] [ebp-2Eh]
  char v5; // [esp+13h] [ebp-2Dh]
  char v6; // [esp+14h] [ebp-2Ch]
  char v7; // [esp+15h] [ebp-2Bh]
  char v8; // [esp+16h] [ebp-2Ah]
  char v9; // [esp+17h] [ebp-29h]
  char v10; // [esp+18h] [ebp-28h]
  char v11; // [esp+19h] [ebp-27h]
  char v12; // [esp+1Ah] [ebp-26h]
  char v13; // [esp+1Bh] [ebp-25h]
  char v14; // [esp+1Ch] [ebp-24h]
  char v15; // [esp+1Dh] [ebp-23h]
  int v16; // [esp+1Eh] [ebp-22h]
  int v17; // [esp+22h] [ebp-1Eh]
  int v18; // [esp+26h] [ebp-1Ah]
  char v19[2]; // [esp+2Ah] [ebp-16h]
  char v20; // [esp+2Ch] [ebp-14h]
  char v21; // [esp+2Dh] [ebp-13h]
  char v22; // [esp+2Eh] [ebp-12h]
  int v23; // [esp+2Fh] [ebp-11h]
  int v24; // [esp+33h] [ebp-Dh]
  int v25; // [esp+37h] [ebp-9h]
  char v26; // [esp+3Bh] [ebp-5h]
  int i; // [esp+3Ch] [ebp-4h]

  v4 = 42;
  v5 = 70;
  v6 = 39;
  v7 = 34;
  v8 = 78;
  v9 = 44;
  v10 = 34;
  v11 = 40;
  v12 = 73;
  v13 = 63;
  v14 = 43;
  v15 = 64;
  printf("Please input:");
  scanf("%s", &v19);
  if ( v19[0] != 65 || v19[1] != 67 || v20 != 84 || v21 != 70 || v22 != 123 || v26 != 125 ){
    printf("23333\n");
  }
    // return 0;
  v16 = v23;
  v17 = v24;
  v18 = v25;
  // ACTF{aaaaaaaaaaaa}
  for ( i = 0; i <= 11; ++i )
  {
    if ( *(&v4 + i) != *((char *)&v16 + i) - 1 ){
      printf("%s ",*(&v4 + i));
      printf("%s\n",*((char *)&v16 + i) - 1 );
    }
      // return 0;
  }
  printf("You are correct!");
  return 0;
}
