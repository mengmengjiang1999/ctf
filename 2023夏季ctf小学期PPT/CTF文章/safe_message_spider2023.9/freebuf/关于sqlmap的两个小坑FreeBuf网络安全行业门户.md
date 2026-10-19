**0x00 概述**

近日在利用sqlmap注入测试时遇到一个奇怪的现象，高版本sqlmap无法检测出注入，但是低版本的可以测出注入，并且能跑出数据不是误报，经过对比测试和查看sqlmap源码，发现两个小坑。

 **0x01 情景重现**

注入点形式：json  
……”whereparams”:[{“name”:”keyWord”,”value”:”test”}]}  
可注入参数：value  
sqlmap命令：  
python sqlmap.py -r sqlpk.txt –flush-session -vv  
sqlmap v1.2.11无法注入

![image.png](https://image.3001.net/images/20181121/1542784116_5bf5047409835.png!small)  
  

sqlmap v1.2成功注入

![image.png](https://image.3001.net/images/20181121/1542784132_5bf50484becc7.png!small)  

同理v1.2.10无法注入，v1.1.12可以注入

经过分析，两坑如下：  
（1）v1.2.11(/v1.2.10/v1.2.9/master)的boundaries.xml没有了针对模糊查询(%)的测试，而v1.2(/v1.1.12/1.1.4/1.2.2)则有。  
（2）v1.2.11(/v1.2.10/1.2.9/master)必须手动设置json的某个参数为*才能对这个参数进行注入（即使选了y-inject
inside），否则payload直接跟在json后导致无法注入，而v1.2(/v1.1.12)则可以默认回车(y)即可对json的某个参数注入。

 **0x02 详细测试**

坑点（1）：  
先了解sqlmap的payload组成：

![image.png](https://image.3001.net/images/20181121/1542784153_5bf5049903f33.png!small)

//图片来源[https://www.freebuf.com/colum...](https://www.freebuf.com/column/161797.html)

看看v1.2的测试payload:

![image.png](https://image.3001.net/images/20181121/1542784175_5bf504af445df.png!small)

  

使用了payload：%‘ and 5731=5731 and ‘%’=’  
这是挺常见的搜索框注入  
看看V1.2的boundaries.xml：

![image.png](https://image.3001.net/images/20181121/1542784194_5bf504c2d3a62.png!small)  

而v1.2.11的boundaries.xml没有对模糊查询的注入测试！  
[https://github.com/sqlmapproj...](https://github.com/sqlmapproject/sqlmap/blob/master/xml/boundaries.xml)  
于是添加模糊查询的注入测试到v1.2.11的该文件中，并手动添加*到注入参数（如value），即可成功注入！  
附上添加后的版本：  
[https://github.com/theLSA/sql...](https://github.com/theLSA/sqlmap/tree/dev)

![image.png](https://image.3001.net/images/20181121/1542784209_5bf504d10ad40.png!small)  

pr得到答复是因为误报太多所以移除了相关payload，但是将会有限的恢复。  
[https://github.com/sqlmapproj...](https://github.com/sqlmapproject/sqlmap/pull/3372)

坑点（2）：  
对比v1.2和v1.2.11的payload：

![image.png](https://image.3001.net/images/20181121/1542784223_5bf504dfeece3.png!small)  
  

可以看出v1.2.11直接将payload接在json末尾了。  
在注入参数value手动添加*  
%22whereparams%22%3A%5B%7B%22name%22%3A%22keyWord%22%2C%22value%22%3A%22*%22%7D%5D%7D  
即可成功注入！

 **0x03 结语**

  1. 个人建议添加模糊查询的测试payload，误报还是好过漏报，况且是很常见的模糊查询注入。
  2. 遇到json参数尽量加手动*(针对某些版本的sqlmap)。
  3. 利用sqlmap测试的时候建议加上-vv。
  4. 不能过于依赖工具，尽量工具+手工测试比较保险。

#  

