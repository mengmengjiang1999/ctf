#include<iostream>
#include<cstring>

int vuln()
{
  const char *v0; // eax
  char s_3C; // [esp+1Ch] [ebp-3Ch]
  char s_1c; // [esp+3Ch] [ebp-1Ch]
  char s_18; // [esp+40h] [ebp-18h]
  char s_11; // [esp+47h] [ebp-11h]
  char s_10; // [esp+48h] [ebp-10h]
  char s_9; // [esp+4Fh] [ebp-9h]

  printf("Tell me something about yourself: ");
  fgets(&s_3C, 32, edata);
  std::string::operator=(&input, &s_3C);
  std::allocator<char>::allocator(&s_11);
  std::string::string(&s_18, "you", &s_11);
  std::allocator<char>::allocator(&s_9);
  std::string::string(&s_10, "I", &s_9);
  replace((std::string *)&s_1c);
  std::string::operator=(&input, &s_1c, &s_10, &s_18);
  std::string::~string((std::string *)&s_1c);
  std::string::~string((std::string *)&s_10);
  std::allocator<char>::~allocator(&s_9);
  std::string::~string((std::string *)&s_18);
  std::allocator<char>::~allocator(&s_11);
  v0 = (const char *)std::string::c_str((std::string *)&input);
  strcpy(&s_3C, v0);
  return printf("So, %s\n", &s_3C);
}

int main(){
    vuln();
    return 0;
}