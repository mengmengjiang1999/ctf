## **一、简介**

**如今，黑客越来越多的通过修改开源的病毒源码来实现快速的病毒开发，如Mirai、qbot等公开了源码的病毒，常被黑客用于二次开发，用以攻击。前不久，一起针对巴基斯坦的APT攻击中，发现黑客所使用的攻击样本是通过开源僵尸网络病毒LiteHttp改造而来的，与后者的行为基本一致。分析开源恶意软件源码，能让我们更直接地了解恶意软件的工作原理，从而设计出更好的防护策略，下面，我们就来本地搭建LiteHttp并对其源码进行简单分析。**

LiteHttp是一个使用C#编写的开源僵尸网络恶意软件，项目地址：

<https://github.com/zettabithf/LiteHTTP>

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546241_5cf4c981dfdd6.png!small)

项目有3个目录，Bot是病毒程序的代码，Panel是控制端的代码，使用PHP编写，Builder是一个生成器，用于快速生成病毒程序。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546247_5cf4c98708b7f.png!small)

生成器运行后如下图，只要填入控制端的Url以及加解密密钥，就能自动生成一个病毒程序，这样就省去了修改病毒源码重新编译的步骤。Builder的代码就是对Bot的一个封装，下面重点分析Bot和Panel的代码。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546252_5cf4c98c5934a.png!small)

控制端只需要将Panel文件夹复制到PHP网站目录下即可运行，不过运行之前要先导入Upload_to_database.sql初始化LiteHttp需要的数据库。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546258_5cf4c99263c40.png!small)

数据库初始化完毕后，访问Panel下的login路径即可进行登陆控制端，初始的账户名和密码均为admin。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546262_5cf4c996ae2ae.png!small)

Dashboard显示了上线主机的概况，下发恶意命令的功能在Tasks标签处。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546267_5cf4c99b1f95f.png!small)

 **二、源码分析**

### 2.1 代码流程

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546270_5cf4c99ea79ae.png!small)

### 2.2 主函数

程序一开始会创建两个线程，分别用于执行核心攻击操作，以及持久化攻击操作。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546274_5cf4c9a26af32.png!small)

### 2.3 持久化攻击函数

持久化攻击操作比较简单，就是在注册表下创建一个自启动项“Catlyst Control Center”，实现每次开机自动运行。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546277_5cf4c9a5b465c.png!small)

### 2.4 核心攻击函数

接下来看核心攻击函数的代码，主要做了3个主要操作：

> [1] 收集主机信息，使用预先约定的密钥进行加密，然后将加密后的信息以Http的方式上传至控制端服务器。
>
> [2] 接受控制端的控制码并执行相应的操作。
>
> [3] 上传执行的结果。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546280_5cf4c9a8b2753.png!small)

### 2.5C&C通信函数

与C&C通信的代码在类Communication中，通过POST的方式将加密后的主机信息上传到控制端服务器，这里有一点值得注意，发送数据包前会将Http头中的UserAgent修改为一个随机字符串，这个是控制端用来识别肉鸡的标识。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546284_5cf4c9ac8b2a0.png!small)

### 2.6 恶意操作执行函数

主要的核心恶意操作在函数processTask中，通过代码我们可以发现，控制码是阿拉伯数字，接收的控制码和执行参数都是通过base64加密的，首先需要对它们进行base64解密。主要的操作大致有4个：下载&执行可执行文件、访问网站、清除异己、更新&卸载病毒程序。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546290_5cf4c9b2c1b35.png!small)

##  **三、平台演示**

在运行病毒程序前，要现在Settings.cs中填入32位的加解密密钥。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546295_5cf4c9b706620.png!small)

同时，在Panel的\inc\config.php中的$deckey中也填入上一步的密钥，代码中是使用AES-CBC算法进行加密的，密钥必须相同才能保证解密出的数据一致。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546298_5cf4c9ba5b6d7.png!small)

调试病毒代码的通信模块，通过下图蓝色部分我们可以看到post的数据为一堆加密后的主机信息。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546302_5cf4c9be21c33.png!small)

第一次运行时发现了一个bug，当病毒程序尝试与控制端服务器通信时，服务器返回了一个404，这时就觉得纳闷了，路径没错呀，为什么会返回404，这里就得到Panel源码中去找答案了。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546307_5cf4c9c34ba55.png!small)

打开page.php，发现原来是只要控制端接收的数据不对，就会跳转到404页面，而通过调试，最后确认了是如下蓝色部分的代码判断失败，这段代码是用来判断参数opsys（肉鸡操作系统）是否为英文和数字的组合，而我们中国地区的windows系统名带有中文，所以判断失败，把这段代码去掉就能成功执行下去了。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546314_5cf4c9ca2a203.png!small)

运行病毒程序后，在控制端的Dashboard中可以看到一台主机上线，由于我的IP是内网地址，所以控制端没有解析出IP的地理位置。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546317_5cf4c9cd4f03d.png!small)

随后，我们就能在Tasks标签页下对该主机进行相应的恶意操作了，下发恶意命令，状态栏中会显示任务执行的状态。

![开源僵尸网络平台LiteHttp源码分析](https://image.3001.net/images/20190603/1559546320_5cf4c9d081bbe.png!small)

 **参考链接：<http://it.rising.com.cn/dongtai/19587.html>**

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

