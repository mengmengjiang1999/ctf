**今天给大家推荐的是一款名叫Huntpad的Notepad应用程序，Huntpad由Syhunt公司开发，这是一款专为渗透测试人员以及漏洞hunter们提供的实用程序，它自带了一套常用注入字符串生成器、哈希生成器、编码器、解码器以及HTML和文本修改功能等等，而且还支持多种编程语言的代码高亮。  
**

![1.png](https://image.3001.net/images/20180512/15261160965456.png!small)

### 工具下载

Huntpad：【[点我下载](http://www.syhunt.com/pub/downloads/huntpad-1.0-win32.exe)】

## 工具介绍

Huntpad从Syhunt
Sandcat的QuickInject插件中借鉴了很多功能，跟QuickInject类似，Huntpad的核心任务也集中在文件包含漏洞、XSS漏洞和SQL注入漏洞的身上，并且还带有下列额外的附加功能：

1\. 代码高亮：支持HTML、JavaScript、CSS、XML、PHP、Ruby、SQL、Pascal、Perl、Python和VBScript。

2\. SQL注入功能：

> a) 过滤器绕过：特定数据库字符串转义（CHAR&CHR），将字符串转换为引用字符串，将空格转义为注释标签或换行。
>
> b)
> 过滤器绕过（MySQL）：字符串拼接，百分号混淆，整形替换。（例如：'26'转换为'ceil(pi()*pi())*(!!!pi()+true)+ceil(@@version)'）
>
> c) UNION语句生成。
>
> d) 针对MySQL、MSSQL、Oracle及PostgreSQL等多款数据库实现快速注入。

3\. 文件包含：

> a) 快速Shell代码上传及生成。
>
> b) PHP字符串转义（chr）。

4\. 跨站脚本XSS功能：

> a) 过滤器绕过：JavaScript字符串转义（String.fromCharCode），CSS转义。
>
> b) 提供了各种用于测试XSS漏洞的测试语句（alert语句）。

5\. 哈希功能：

a) 哈希生成器：MD5, SHA-1, SHA-2 (224, 256, 384 & 512), GOST, HAVAL (various),MD2,
MD4, RIPEMD (128, 160, 256 & 320), Salsa10, Salsa20, Snefru (128 &256), Tiger
(various) & WHIRLPOOL

6\. 编码器/解码器：

> a) URL编码/解码。
>
> b) 十六进制编码/解码：将字符串或整形值转换为十六进制（支持多种输出格式）。
>
> c) Base64编码/解码。
>
> d) CharCode转换：将字符串转换为charcode（例如'abc'转换为'97,98,99'）。
>
> e) IP混淆：将IP地址转换为dword或十六进制值。
>
> f) JavaScript编码：类似JJEncode。

7\. HTML功能：

> a) HTML转义。
>
> b) HTML实体编码/解码：十进制和十六进制HTML实体编码/解码。
>
> c) JavaScript字符串转义。

8\. 文本修改功能：大小写转换、字符串反向操作、添加/替换斜杠等。

9\. 基于时间的盲注代码。

10\. CRC计算：CRC16, CRC32, CRC32b等等。

11\. 缓冲区溢出字符串生成。

12\. 随机字符串/数组生成功能。

 ***
参考来源：[syhunt](http://www.syhunt.com/en/index.php?n=Products.SyhuntHuntpad)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

