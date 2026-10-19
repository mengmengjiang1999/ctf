作者：[Chu](http://mp.weixin.qq.com/s/8C3jbfMy3sKCSdul4Y8Pcg "Chu")  
来源：微信公众号：sh3ll

#### 1\. 前言

老板前一段给买了几款路由把玩，研究了下 D-Link DIR 629、DIR 823 这两款板子。

发现在 soap.cgi 中存在几处栈溢出，均可以远程利用，并且其他型号的路由也有对 soap 这一部分代码的复用。

#### 2\. 逆向分析与漏洞挖掘

因为是想挖几个能远程利用的洞，首先去看了 HTTP 服务，也就是 /htdocs/cgibin。

D-Link HTTP 服务由cgibin提供，并通过软链接的文件名进入到不同的处理分支：

![](https://images.seebug.org/content/images/2018/01/65862539-6d9f-46af-8238-16e822f8d54c.jpg-w331s)

在各个 cgi 处理函数中，会通过 cgibin_parse_request 来解析用户输入，其函数原型大致如下：

![](https://images.seebug.org/content/images/2018/01/c672c581-05fe-4b64-9c95-4e2aa8ff0002.jpg-w331s)

参数 `save_param_func` 用于传入解析/存储 HTTP 请求的具体 handler，读取 HTTP 请求后使用该 handler
具体处理用户输入。在 soapcgi_main（0x00418E28）中传入了漏洞函数
`vulnerable_sprintf_parser（0x0041893C）`：

![](https://images.seebug.org/content/images/2018/01/8967aee7-7a14-49ac-9670-b06304ae0480.jpg-w331s)

跟进 `vulnerable_sprintf_parser` 可以发现程序未进行边界检查便将全局变量 `g_http_soapaction` 通过
sprintf 写到栈上：

![](https://images.seebug.org/content/images/2018/01/e3e79a92-06fd-4b01-a1f5-235a5d12e8ed.jpg-w331s)

`g_http_soapaction` 来自于 `soapcgi_main` 中对 HTTP Header SOAPACTION 字段的解析：

取 HTTP_SOAPACTION：

![](https://images.seebug.org/content/images/2018/01/6883e741-4c11-4657-8c52-187e2955979c.jpg-w331s)

取 # 后的值：

![](https://images.seebug.org/content/images/2018/01/6b8ecc8a-e74f-414b-95ef-c9c72f806ce4.jpg-w331s)

至此漏洞原理已经明了：soapcgi_main 中未进行边界检查便将 HTTP Header 中的 SOAPACTION 字段存储至栈上，导致栈溢出。

#### 3\. 漏洞利用

基础信息：

![](https://images.seebug.org/content/images/2018/01/798e84c4-37bf-44ce-9c1c-fc8604e9f4a3.jpg-w331s)

MIPS 大端序，开启了 NX，未开启 ASLR、PIE，只需要做个 ROP。

溢出的崩溃现场如下：

![](https://images.seebug.org/content/images/2018/01/d4e17b01-9ace-41c7-9187-dd4cfff9ce6b.jpg-w331s)

S2-S3、SP 指向的内存可控，要编写 ROP 只能在这几个寄存器上做文章，最终用 ropper 在 uClibc 中找了个很不错的 gadget：

![](https://images.seebug.org/content/images/2018/01/6875eb29-a8c8-4dcf-bbb2-fb88c01490a0.jpg-w331s)

现在需要做的就是找到 libc 加载的实际基址。

在隔壁开锁王师傅的指导下把板子拆开，接上串口：

![](https://images.seebug.org/content/images/2018/01/ed865392-3acf-4315-a57e-086649845834.jpg-w331s)

成功获取到 shell：

![](https://images.seebug.org/content/images/2018/01/3728afd5-22b5-4687-b927-af7f67a97618.jpg-w331s)

拿到 shell 后读 /proc/pid/maps 就可以获取到libc的加载基址。

最终编写 ROP 如下：

![](https://images.seebug.org/content/images/2018/01/8d04e99f-b34c-405c-ada0-655aa9abb78a.jpg-w331s)

攻击演示：

![](https://images.seebug.org/content/images/2018/01/5bebe6c9-e12e-4e73-a2e2-9480153d0568.jpg-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/504/>

