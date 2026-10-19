![](https://image.3001.net/images/20210131/1612081695_60166a1fa688954583426.jpg!small)

## 写在前面的话

在一次[ _红队分析_](https://www.blackarrow.net/red-team/)中，我们成功以非特权用户的身份在一个外围网页中实现了命令执行。本文将介绍并分析漏洞（[
_CVE-2018-1685_](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-1685)）以及该漏洞的利用方式，该漏洞允许攻击者读取目标主机中的任意文件，但目前还没有针对该漏洞的公开细节。除此之外，我们还会介绍一种技术，在加入了活动目录域的Linux设备（通过Kerberos）中将这种类型的漏洞（任意文件读取）转换为完整的系统渗透并实现任意命令执行。

## 权限提升

我们的测试设备是一台近期刚刚更新的Red
Hat服务器，因此我们无法利用内核漏洞来实现提权。经过一系列常规检测之后，我们发现了一些带有SUID的root级别可执行程序：

    
    
    /home/db2test/sqllib/adm:
    
     total 5.3M
    
     drwxr-sr-x.  2 db2test db2test  112 Oct  8 10:29 .
    
     drwxrwsr-t. 19 db2test db2test 4.0K Oct  8 10:32 ..
    
     -r-sr-xr-x.  1 db2test db2test 152K Oct  8 10:29 db2audit
    
     -r-sr-xr-x.  1 root    db2test  19K Oct  8 10:29 db2cacpy
    
     -r-xr-xr-x.  1 db2test db2test 195K Oct  8 10:29 db2cap
    
     -r-sr-x---.  1 root    db2test  32K Oct  8 10:29 db2iclean
    
     -r-sr-x---.  1 root    db2test  87K Oct  8 10:29 db2licm
    
     -r-xr-xr-x.  1 db2test db2test 120K Oct  8 10:29 db2set
    
     -r-sr-sr-x.  1 db2test db2test 4.7M Oct  8 10:29 db2trc  

“db2test”用户貌似跟一个DB2测试安装油管，即一个IBM的数据库管理系统。搜索引擎求助一番之后，我们发现了一个关于这些可执行程序（db2cacpy）的安全公告（由厂商发布）。

 **CVE-2018-1685漏洞描述：**

![](https://image.3001.net/images/20210131/1612081729_60166a41e4ab260717f5e.png!small)

 **解决方案和缓解策略：**

![](https://image.3001.net/images/20210131/1612081736_60166a48715e70e3ef585.png!small)

虽然厂商并没有披露关于该漏洞的任何技术细节，但我们可以找到两个有意思的地方：

> 该漏洞允许本地用户读取系统中的任意文件；
>
> 在解决方案中，厂商提到删除这部分代码将会导致添加数据库时无法向/etc/services中添加端口；

了解到这些内容之后，我们就可以继续下一步了。

## CVE-2018-1685：漏洞捕捉

首先，为了分析漏洞，我们在本地下载了这些可执行程序。除此之外，我们还需要下载大约10个DB2代码库来让工具正确运行。

经过初始的静态分析之后，我们就可以拆分其各种行为了。代码接收两个命令行参数，并会在程序继续执行之前对它们执行相应的检测。

### 第一个检测

第一个检测是以某种混淆方式进行的，判断第一个参数是否跟存储在cleartext中的密钥相匹配：

![](https://image.3001.net/images/20210131/1612081753_60166a5955828646e7d79.png!small)

### 第二个检测

在第二个检测中，将会判断第二个参数是否是以字符串“/tmp/services.”开头的，这很可能是因为另外的DB2组件是以这种模式来生成文件的：

![](https://image.3001.net/images/20210131/1612081764_60166a64896b084481cf0.png!small)

## 漏洞分析

如果这两个检测都通过了，工具将会把指定的文件拷贝到/etc/services，并重写该文件。下面给出的是这个过程的简化版伪代码：

    
    
    func main(argc, argv[]) {
    
       init_db2()
    
       if (argc is 3)
    
       {
    
          if (argv[1] equals HARDCODED_KEY) {
    
             if (argv[2] startsWith "/tmp/services.") {
    
                copy_file(argv[2], "/etc/services")
    
             }
    
          }
    
       }
    
    }

那么，我们该如何利用这个读取任意文件漏洞呢？没错，就是通过路径遍历！如果我们在/tmp中创建一个名为“services.”的目录（或以这个字符串开头的），我们就可以触发/tmp/services./../../etc/shadow的拷贝行为，并通过第二个检测。

我们可以点击【[这里](https://github.com/blackarrowsec/redteam-research/tree/master/CVE-2018-1685/)】获取到漏洞利用PoC代码，它还会在漏洞利用完成之后恢复原来的/etc/services文件。需要注意的是，第一个检测中的密钥可能会根据DB2的版本或安装配置的不同而有所变化。

![](https://image.3001.net/images/20210131/1612081836_60166aac88c252c15edd8.png!small)

## 从任意读取到以root权限实现命令执行

由于我们的测试设备是一台通过Kerberos加入活动目录域的Linux服务器，因此我们首先要检测/tmp中是否存在有效的TGT（ccache文件），以便实现数据复用。但是，这些数据都已经过期了。因此，我们需要寻找另一种不需要用户交互的途径，即keytab文件。

keytab文件中包含了计算机账号的密钥（Red Hat中默认为/etc/krb5.keytab），你可以使用这个密钥来伪造TGS服务令牌。

为了从keytab中提取出密钥，我们使用了我们的DB2漏洞利用代码以及这个【[
_脚本_](https://github.com/sosdave/KeyTabExtract)】：

![](https://image.3001.net/images/20210131/1612081850_60166aba155acfa1f4a7b.png!small)

接下来，使用impacket中的[
_ticketer.py_](https://github.com/SecureAuthCorp/impacket/blob/master/examples/ticketer.py)工具，我们可以创建一个针对服务器中SSH服务的TGS，并以域用户命名，而这个域用户拥有设备上的管理员权限：

![](https://image.3001.net/images/20210131/1612081858_60166ac228230020b4c49.png!small)

最后，我们可以使用生成的令牌来通过SSH与设备进行连接，并使用Kerberos完成身份验证。然后，以root权限执行任意命令：

![](https://image.3001.net/images/20210131/1612081864_60166ac8680e55bb6315c.png!small)

## 总结

在这篇文章中，我们学习了如何去利用一个众所周知但并未披露技术细节的安全漏洞，这也就是为什么我们一直在强调必须尽快为每一个应用程序安装安全补丁的原因！

