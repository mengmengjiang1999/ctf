靶标介绍：

ED01-CMS v20180505 存在任意文件上传漏洞

漏洞复现过程

1.打开场景

![1689044518_64acc6263b2c2e069104d.png!small](https://image.3001.net/images/20230711/1689044518_64acc6263b2c2e069104d.png!small)

2.漏洞利用

尝试注册不成功

![1689044580_64acc664ac61f0b3bef6c.png!small](https://image.3001.net/images/20230711/1689044580_64acc664ac61f0b3bef6c.png!small)

3.通过弱口令:admin/admin登录成功

![1689044591_64acc66f0739c09356a07.png!small](https://image.3001.net/images/20230711/1689044591_64acc66f0739c09356a07.png!small)

4.寻找上传点，对admin账号进行编辑，上传木马

![1689044599_64acc6775d282c33ed5f8.png!small](https://image.3001.net/images/20230711/1689044599_64acc6775d282c33ed5f8.png!small)

![1689044612_64acc684c6734499ddde5.png!small](https://image.3001.net/images/20230711/1689044612_64acc684c6734499ddde5.png!small)

5.使用burp抓包工具进行抓包修改png后缀为php后缀

![1689044622_64acc68eab65ef1f369c8.png!small](https://image.3001.net/images/20230711/1689044622_64acc68eab65ef1f369c8.png!small)

![1689044631_64acc69798a966ea36ff5.png!small](https://image.3001.net/images/20230711/1689044631_64acc69798a966ea36ff5.png!small)

6.右击图片，打开标签图片查看路径。

![1689044638_64acc69e993d9d526bf2f.png!small](https://image.3001.net/images/20230711/1689044638_64acc69e993d9d526bf2f.png!small)

7.复制路径http://eci-2ze2h1rmp2kibdc8ru3c.cloudeci1.ichunqiu.com/images/3.php连接中国蚁剑读取flag

![1689044658_64acc6b232b77f5de905f.png!small](https://image.3001.net/images/20230711/1689044658_64acc6b232b77f5de905f.png!small)

![1689044675_64acc6c3ae5c3e40e1243.png!small](https://image.3001.net/images/20230711/1689044675_64acc6c3ae5c3e40e1243.png!small)

![1689044686_64acc6ce0afd3527f9cc0.png!small](https://image.3001.net/images/20230711/1689044686_64acc6ce0afd3527f9cc0.png!small)

