***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文作者：r0yanx，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 前言

 **最近为甲方做渗透测试发现了一个远程命令执行漏洞，可以通过恶意参数传递执行bash命令，本文回顾一下漏洞的挖掘过程。**

## 发现

1、通过nessus扫描器的Sitemap模块，发现了可疑目录：

![可疑目录](https://image.3001.net/images/20180925/1537854662_5ba9ccc696c08.png!small)

2、根据sitemap的目录信息，打开URL:<http://x.x.x.x:28076/file/>，发现存在未授权访问漏洞：

![授权访问漏洞](https://image.3001.net/images/20180925/1537851924_5ba9c214ef824.png!small)

3、逐个查看里面的文件，找到了一些比较有意思的JSP：

![比较有意思的JSP](https://image.3001.net/images/20180925/1537852007_5ba9c267a3584.png!small)

4、蒙了一下dirFiles.jsp的
参数，使用"path"作为参数名可列出目录、文件信息，URL：[http://x.x.x.x:28076/file/dirFiles.jsp?path=](http://x.x.x.x:28076/file/dirFiles.jsp?path=.)。

![目录和文件信息](https://image.3001.net/images/20180925/1537854721_5ba9cd01caf62.png!small)

5、同样的方法，发现show.jsp存在任意文件读取漏洞，URL：<http://x.x.x.x:28076/file/show.jsp?path=/etc/passwd>。

![任意文件读取漏洞](https://image.3001.net/images/20180925/1537852761_5ba9c55932316.png!small)

6、结合上面的目录信息和任意文件读取漏洞，对JSP文件简单审计一下，发现logContentNewest.jsp会调用一个bash脚本，便猜想能否使用它构造命令执行：

![构造命令执行](https://image.3001.net/images/20180925/1537852699_5ba9c51b75ce3.png!small)

## 测试

logContentNewest.jsp正常执行是这样的，可自定义path参数的值，如/etc/passwd，来查找这个文件里面的内容：

![文件内容](https://image.3001.net/images/20180925/1537853175_5ba9c6f721717.png!small)

分析logContentNewest.jsp和
被调用的sh脚本，得知path参数最终会传入sh脚本的FILE_PATH变量，然后调用下面的判断逻辑。从下面代码我们可以看到，函数的功能是判断FILE_PATH变量的值是否存在，而这个变量的值目前是可控的。

![变量的值目前是可控的](https://image.3001.net/images/20180925/1537853533_5ba9c85d3d26d.png!small)

最初想通过添加双引号闭合if条件判断参数注入命令，没有成功。

    
    
    payload：/etc/passwd" ];ls;then echo 1;fi;if [ -e "123.txt;

![判断参数注入命令](https://image.3001.net/images/20180925/1537853720_5ba9c9185b22c.png!small)

从上图可以看到，payload的双引号不见了，在自己的Linux测试一下，发现bash在这种情况下会过滤双引号，因此排除了存在过滤双引号的可能。

![存在过滤双引号的可能](https://image.3001.net/images/20180925/1537853766_5ba9c946515d8.png!small)

经过多次测试，最终可用反引号``或者$()进行命令执行，如`ifconfig`：

    
    
    payload："`ifconfig`"

命令结果的回显是因为判断不存在FILA_PATH文件名的文件后，会把变量值返回

    
    
    echo "the file($FILE_PATH) dose not exist!"

拓展知识：Linuxbash中可以使用反引号``、$()等方式将bash命令的执行结果保存到变量中，如a=$(ifconfig)：

![保存到变量](https://image.3001.net/images/20180925/1537853850_5ba9c99ad7497.png!small)

结果显示不完整，只能看到返回的第一行的结果，没关系，可以简单优化一下：

    
    
    payload："`ifconfig |xargs`"

拓展知识：xargs可以将stdin中以空格或换行符进行分隔的数据，形成以空格分隔的参数（arguments），传递给其他命令。因为以空格作为分隔符，所以有一些文件名或者其他意义的名词内含有空格的时候，xargs可能会误判。简单来说，xargs是给其他命令传递参数的一个过滤器，是构建单行命令的重要组件之一。
但是这里仅仅只是通过xargs的特性让它把多行内容转换成一行来更好地显示结果，当然也可以使用其他方法来实现：

![使用其他方法来实现](https://image.3001.net/images/20180925/1537854006_5ba9ca36e8047.png!small)

在看看nmap内网扫描的结果，同样的漏洞组件在内网中还发现了很多...

![漏洞组件](https://image.3001.net/images/20180925/1537854211_5ba9cb03eedd9.png!small)

## 小结

漏洞是由于程序调用bash脚本传参时没有做过滤，通过$(cmd)这样的方式来执行命令并将结果存入变量中，在脚本判断文件不存在时会返回文件名，造成了回显。

漏洞修复方法：

> 严格控制文件名参数值，先判断文件名或文件路径是否合法可修复漏洞。

 ***本文作者：r0yanx，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

