**最近简单的了解了一下Volatility这个开源的取证框架，这个框架能够对导出的内存镜像镜像分析，能过通过获取内核的数据结构，使用插件获取内存的详细情况和运行状态，同时可以直接dump系统文件，屏幕截图，查看进程等等等等~~~**

## 安装

安装分为三步走：

>   1. 下载
>   2. 安装必要的python依赖文件
>   3. 安装本体
>

### 下载

你可以在[Release](https://link.jianshu.com/?t=https:/github.com/volatilityfoundation/volatility/releases)中找到对应你系统（Mac，Win，Linux）的源代码，当然也可以通过github去获取源码：

git clone <https://github.com/volatilityfoundation/volatility.git>

### 依赖

如果只是用Volatility本体，就不要安装这些依赖，但是如果想使用某些插件，就需要对这些以依赖进行安装·

Distorm3:牛逼的反编译库

`pip install distorm3`

Yara:恶意软件分类工具

`pip install yara`

PyCrypto:加密工具集

`pip install pycrypto`

PIL:图片处理库

`pip install pil`

OpenPyxl:读写excel文件

`pip install openpyxl`

ujson:JSON解析

`pip install ujson`

### 安装

如果你用的是独立的win、linux、mac执行文件，那就不必安装了。只要用python去执行就好。

若是下载了压缩文件，那你可以选择直接运行python主程序，也可以选择使用python setup.py
install的方式将Volatility以一个库的形式安装在系统的特定位置上，从而以后我们可以将Volatility作为一个库在其他脚本中去引用namespace。

## 0x02 使用

kali自带有volatility，于是我直接在kali山进行操作

我这里也直接用我这两天看的一道CTF的题目作为实例来操作吧

![01.png](https://image.3001.net/images/20200526/1590463174_5ecc8ac66167a.png!small)

Imageinfo

这个命令可以用来获取内存镜像的摘要信息，比如系统版本，硬件构架等

`volatility -f wuliao.data imageinfo`

通过Suggested Profile(s) 我们可以知道这个镜像文件的版本最有可能事Win7SP1x64

![02.png](https://image.3001.net/images/20200526/1590463181_5ecc8acd8f306.png!small)

可以使用–info参数来查看Volatility已经添加的profile和插件信息

![03.png](https://image.3001.net/images/20200526/1590463185_5ecc8ad15d178.png!small)

Kdbgscan

这个插件可以扫描文件的profile的值，通常扫描结果有多个，只有一个结果是完全正确的，kdbgscan和imageinfo都只适用于windows的镜像

![04.png](https://image.3001.net/images/20200526/1590463193_5ecc8ad93ff04.png!small)Pslist

`volatility -f wuliao.data --profile=Win7SPx64 pslist`

pslist可以直接列出运行的进程，如果进程已经结束，会在Exit列显示日期和时间，表明进程已经结束

![05.png](https://image.3001.net/images/20200526/1590463201_5ecc8ae181d67.png!small)Hivelist

列举缓存在内存中的注册表

`volatility -f wuliao.data --profile=Win7SP1x64 hivelist`

![06.png](https://image.3001.net/images/20200526/1590463244_5ecc8b0c0dbc9.png!small)filescan

扫描内存中的文件

`volatility -f wuliao.data --profile=Win7SP1x64 filescan`

![07.png](https://image.3001.net/images/20200526/1590463227_5ecc8afb9621b.png!small)

filescan 也可以结合grep命令来进行筛选，比如

`volatility -f wuliao.data --profile=Win7SP1x64 filescan |grep
"doc\|docx\|rtf"`

![08.png](https://image.3001.net/images/20200526/1590463254_5ecc8b16dd41d.png!small)

也可以

`volatility -f wuliao.data --profile=Win7SP1x64 filescan |grep "flag"`

![09.png](https://image.3001.net/images/20200526/1590463278_5ecc8b2e1b8f8.png!small)Dumpfiles

导出内存中缓存的文件

我直接导出上面搜索flag得到的flag.jpeg文件

`volatility -f wuliao.data --profile=Win7SP1x64 dumpfiles -Q
0x000000007f142f20 -D ./ -u`

![10.png](https://image.3001.net/images/20200526/1590463285_5ecc8b359d6a5.png!small)Cmdscan/cmdline

提取内存中保留的cmd命令使用情况

`volatility -f wuliao.data --profile=Win7SP1x64 cmdline`

###
![11.png](https://image.3001.net/images/20200526/1590463332_5ecc8b64b63cd.png!small)查看截图

`volatility -f wuliao.data --profile=Win7SP1x64 screenshot --dump-dir=./`

![12.png](https://image.3001.net/images/20200526/1590463363_5ecc8b83d0f6f.png!small)

### 查看系统用户名

`volatility -f wuliao.data --profile=Win7SP1x64 printkey -K
"SAM\Domains\Account\Users\Names"`

### 查看网络连接

`volatility -f wuliao.data --profile=Win7SP1x64 netscan`

![13.png](https://image.3001.net/images/20200526/1590463373_5ecc8b8d1db2b.png!small)

我真是个啥都不会，啥都要学的five啊

![2019062606.png](https://image.3001.net/images/20200526/1590463379_5ecc8b939bf57.png!small)
***本文作者:瑟瑟发抖咸鱼黄，转载请注明来自FreeBuf.COM**  

