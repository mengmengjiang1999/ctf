## **IIS6.0** **解析漏洞复现**

IIS解析漏洞

 **目录解析漏洞** **(IIS6.0)**
：在IIS6.0的网站目录中创建有*.asp形式的目录，该文件夹下的所有文件都会以asp脚本格式进行解析。/xx.asp/xx.jpg(xx.asp是文件夹)  
下面以Windows Server2003搭建的环境演示：

实验环境：VM16虚拟机中

在网站的主目录下新建一个1.asp文件夹

![1614958488_60424f981f20c1031809f.png!small](https://image.3001.net/images/20210305/1614958488_60424f981f20c1031809f.png!small)

在1.asp目录下创建asp的图片马

把asp的一句话用winhex写入图片

![1614958498_60424fa2ca8c5bbdfb735.png!small](https://image.3001.net/images/20210305/1614958498_60424fa2ca8c5bbdfb735.png!small)

![1614958510_60424fae30a4d4f334e8d.png!small](https://image.3001.net/images/20210305/1614958510_60424fae30a4d4f334e8d.png!small)

我们进行访问，看是否能解析

![1614958519_60424fb7d97e888a98bec.png!small](https://image.3001.net/images/20210305/1614958519_60424fb7d97e888a98bec.png!small)

解析成功，进行蚁剑连接

![1614958527_60424fbf9ab15251a5dfa.png!small](https://image.3001.net/images/20210305/1614958527_60424fbf9ab15251a5dfa.png!small)

 **文件解析漏洞** **(IIS6.0)**
：在IIS6.0的网站中，存在有这样格式的文件*.asp;.jpg，其中代表着任意字符，这种格式文件会以asp脚本格式进行解析，也就是说会解析成*.asp，分号后面的不会去管，因为URL一般以分号结尾

还是在Windows Server 2003中实验

把图片马，名字改为11.asp;.jpg

![1614958633_60425029aeb80a746ec20.png!small](https://image.3001.net/images/20210305/1614958633_60425029aeb80a746ec20.png!small)

进行访问，看是否能解析

![1614958651_6042503b0a44271e7bf77.png!small](https://image.3001.net/images/20210305/1614958651_6042503b0a44271e7bf77.png!small)

解析成功，蚁剑连接

![1614958658_60425042179e2b18c25f0.png!small](https://image.3001.net/images/20210305/1614958658_60425042179e2b18c25f0.png!small)

