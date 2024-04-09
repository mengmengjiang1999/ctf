# #include<cstdio>
# using namespace std;

# int func()
# {
#   int result; // eax
#   int v1; // [esp+14h] [ebp-44h]
#   int v2; // [esp+18h] [ebp-40h]
#   int v3; // [esp+1Ch] [ebp-3Ch]
#   int v4; // [esp+20h] [ebp-38h]
#   char v5; // [esp+24h] [ebp-34h]
#   char v6; // [esp+25h] [ebp-33h]
#   char v7; // [esp+26h] [ebp-32h]
#   char v8; // [esp+27h] [ebp-31h]
#   char v9; // [esp+28h] [ebp-30h]
#   int v10; // [esp+29h] [ebp-2Fh]
#   int v11; // [esp+2Dh] [ebp-2Bh]
#   int v12; // [esp+31h] [ebp-27h]
#   int v13; // [esp+35h] [ebp-23h]
#   char v14; // [esp+39h] [ebp-1Fh]

#   char v15; // [esp+3Bh] [ebp-1Dh]
#   char v16; // [esp+3Ch] [ebp-1Ch]
#   char v17; // [esp+3Dh] [ebp-1Bh]
#   char v18; // [esp+3Eh] [ebp-1Ah]
#   char v19; // [esp+3Fh] [ebp-19h]
#   char v20; // [esp+40h] [ebp-18h]
#   char v21; // [esp+41h] [ebp-17h]
#   char v22; // [esp+42h] [ebp-16h]
#   char v23; // [esp+43h] [ebp-15h]
#   char v24; // [esp+44h] [ebp-14h]
#   char v25; // [esp+45h] [ebp-13h]
#   char v26; // [esp+46h] [ebp-12h]
#   char v27; // [esp+47h] [ebp-11h]
#   char v28; // [esp+48h] [ebp-10h]
#   char v29; // [esp+49h] [ebp-Fh]
#   char v30; // [esp+4Ah] [ebp-Eh]
#   char v31; // [esp+4Bh] [ebp-Dh]
#   int i; // [esp+4Ch] [ebp-Ch]

# 

#   v15 = 81;
#   v16 = 115;
#   v17 = 119;
#   v18 = 51;
#   v19 = 115;
#   v20 = 106;
#   v21 = 95;
#   v22 = 108;
#   v23 = 122;
#   v24 = 52;
#   v25 = 95;
#   v26 = 85;
#   v27 = 106;
#   v28 = 119;
#   v29 = 64;
#   v30 = 108;
#   v31 = 0;

print(chr(65))
print(chr(67))
print(chr(84))
print(chr(70))
print(chr(123))
print(chr(125))

print((0+51)%26)

print(97-79)
print(122-79)

# 如果是大写字母那么右移一位
# 如果是小写字母那么左移一位

flag=''

v=[81,115,119,51,115,106,95,108,122,52,95,85,106,119,64,108]
for i in v:
    if i>64 and i<=90:
        # flag+=chr((i-65)+51)
        flag+=chr((i-65-14)%26+65)
    elif i> 96 and i <= 122 :
        # flag+=chr((i-97)+79)
        flag+=chr((i-97-18)%26+97)
    else:
        flag+=chr(i)
print(flag)

# 97-79=18

# flag{CmqmdftGdqf}

# ACTF{Cmq3md_ft4_Gdq@f}
# flag{Cae3aX_Zh4_GXe@Z}
#   printf("Please input:");
#   scanf("%s", &v5);
#   result = v5;
#   if ( v5 == 65 )
#   {
#     result = v6;
#     if ( v6 == 67 )
#     {
#       result = v7;
#       if ( v7 == 84 )
#       {
#         result = v8;
#         if ( v8 == 70 )
#         {
#           result = v9;
#           if ( v9 == 123 )
#           {
#             result = v14;
#             if ( v14 == 125 )
#             {
#               v1 = v10;
#               v2 = v11;
#               v3 = v12;
#               v4 = v13;
#               for ( i = 0; i <= 15; ++i )
#               {
#                 if ( *((char *)&v1 + i) > 64 && *((char *)&v1 + i) <= 90 )
#                   *((char *)&v1 + i) = (*((char *)&v1 + i) - 51) % 26 + 65;
#                 if ( *((char *)&v1 + i) > 96 && *((char *)&v1 + i) <= 122 )
#                   *((char *)&v1 + i) = (*((char *)&v1 + i) - 79) % 26 + 97;
#               }
#               for ( i = 0; i <= 15; ++i )
#               {
#                 result = (char)*(&v15 + i);
#                 if ( *((char *)&v1 + i) != (char)result )
#                   return result;
#               }
#               result = printf("You are correct!");
#             }
#           }
#         }
#       }
#     }
#   }
#   return result;
# }