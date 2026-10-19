***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **这篇文章为原创，非英文论坛翻译版本，看分析请看另一篇翻译文章，他一定没有复现，因为我试过poc，其中某个参数是错误的！
在这里，也提醒各位同行，请复现过，实际操作过，再来写文章，不要copy，连图片都一样，没有任何意义。**

首先，先将poc地址给下：<https://github.com/Rhynorater/CVE-2018-15473-Exploit>

这个poc下使用了docker作为虚拟机靶机。

首先，我们开始装docker,这里提醒各位，一定要看好自己的系统版本，在windows上装docker时，分专业版和家庭版，专业版的需要hyper-v这个破玩意儿支持，而家庭版本 docker-toolsbox 使用的是visualbox。

![image.png](https://image.3001.net/images/20190110/1547112222_5c370f1ece43e.png!small)

其次，安装好后不要直接输入命令，记住一定家庭版不要装hyper-v，专业版卸载了vbox再装，会起冲突。点开Docker Quickstart
Terminal 蓝色图标，创建default client。  

![image.png](https://image.3001.net/images/20190110/1547112347_5c370f9b06e61.png!small)

然后，输入 docker build -t cve-2018-15473 . ,这里提醒
一定要小写，否则会报错，文件夹名改成小写的。还有后面有个小点不要忘了。要切换到目录下

![image.png](https://image.3001.net/images/20190110/1547112581_5c371085a14a5.png!small)

然后，执行poc docker run cve-2018-15473 ip地址 随便来个用户名

![image.png](https://image.3001.net/images/20190110/1547112740_5c37112405f68.png!small)

然后，你会发现你报错了。哎呀妈呀，报错了，直接告诉大家答案，有兴趣可以到paramiko下的auth_handler下的AUTH_handler去看。 要将
_handler_table改为_client_handler_table,这样才能找到方法调用old_parse_auth,就正确了。

![image.png](https://image.3001.net/images/20190110/1547112903_5c3711c7ea218.png!small)![image.png](https://image.3001.net/images/20190110/1547112923_5c3711dbe84b2.png!small)下一篇，我尝试将此poc植入metasploit框架，会在第一时间公布rb文件，如果有大佬完成的话，欢迎共享。

 ***本文作者：522952110，转载请注明来自FreeBuf.COM**

