#include<iostream>
#include<cstdio>
using namespace std;

int main(int argc, const char **argv, const char **envp)
{
  long long v3; // rax
  char v5[44]; // [rsp+0h] [rbp-440h]
  int v6; // [rsp+2Ch] [rbp-414h]
  char v7[16]; // [rsp+30h] [rbp-410h]
  char v8[1008]; // [rsp+40h] [rbp-400h]
  long long v9; // [rsp+430h] [rbp-10h]
  int j; // [rsp+438h] [rbp-8h]
  int i; // [rsp+43Ch] [rbp-4h]

  printf("Enter the String: ", argv, envp);
  scanf("%s", v8);
  for ( i = 0; v8[i]; ++i )
    ;
  if ( i == 12 )
  {
    puts("that's correct!");
    v9 = EVP_MD_CTX_new((long long)"that's correct!");// 
                                                // EVP_MD_CTX_new()
                                                // Allocates and returns a digest context.
    v3 = EVP_md5("that's correct!", v8);        // EVP_md5()
                                                // The MD5 algorithm which produces a 128-bit output from a given input.
    EVP_DigestInit_ex(v9, v3, 0LL);             // EVP_DigestInit_ex() 
                                                // int EVP_DigestInit_ex(EVP_MD_CTX *ctx, const EVP_MD *type, ENGINE *impl);
                                                // 
                                                // Sets up digest context ctx to use a digest type. type is typically supplied by a function such as EVP_sha1(), or a value explicitly fetched with EVP_MD_fetch().
                                                // 
                                                // If impl is non-NULL, its implementation of the digest type is used if there is one, and if not, the default implementation is used.
                                                // 
                                                // The type parameter can be NULL if ctx has been already initialized with another EVP_DigestInit_ex() call and has not been reset with EVP_MD_CTX_reset().
    EVP_DigestUpdate(v9, (long long)"12", 2LL);   // EVP_DigestUpdate()
                                                // (EVP_MD_CTX *ctx, const void *d, size_t cnt);
                                                // Hashes cnt bytes of data at d into the digest context ctx. This function can be called several times on the same ctx to hash additional data.
    v6 = 16;
    EVP_DigestFinal_ex(v9, v7, &v6);            // retrieves the digest value from ctx and places it in md
                                                // 把v9的值给v7，长度是v6
    EVP_MD_CTX_free(v9);
    for ( j = 0; j <= 15; ++j )                 // v7的值打乱给v5
      sprintf(&v5[2 * j], "%02x", (unsigned char)v7[j]);
    printf("csawctf{%s}\n", v5);
  }
  else
  {
    printf("that isn't correct, im sorry!", v8);
  }
  return 0;
}