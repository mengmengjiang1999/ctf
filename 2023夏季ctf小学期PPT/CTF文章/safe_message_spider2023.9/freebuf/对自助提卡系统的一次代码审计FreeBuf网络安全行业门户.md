起因：

这是很早的文章了，当初团队师傅想看H片，奈何不想花钱购买，然后审计了H站自助提卡系统，并收获了80G种子

此文章为团队师傅原创，参与过原创发表，原文地址：https://www.freebuf.com/vuls/178744.html  

前言

并非有意愿要审计该站，前面的走的黑盒没有过于精彩部分就不在贴上了，对于此系统站你们懂的，多说无益，这套程序是开源的，像这种自助提卡系统相信大家已经不在陌生了，很多违法网站通过这种平台方式提卡密的相当于购买邀请码，源码是小伙伴提供的，采用的是php+mysql进行开发的24小时自动售卡平台，废话就不多说了。

相关环境

源码信息：你猜啊

漏洞类型：Forwarded-For注入

搭建成功之后如下 ：

看到如下页面是不是有似曾相识的感受：

![879321_2YGWYWUK9H****A.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_2YGWYWUK9H****A.jpg)  

上图是安装过后的首页，就是一个提卡网，继续吧继续！

![879321_AUGJ5HU6YCJU6TE.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_AUGJ5HU6YCJU6TE.jpg)  

这是首页文件，进去首先判断了install目录下的lock文件是否不存在并且判断是否有index.php文件，如果满足以上条件就跳转到install目录下的index.php，我们跟进install/index.php文件：

![879321_FXZJG5FRPS22XTH.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_FXZJG5FRPS22XTH.jpg)  

![879321_GHY**WJBZEKKNPA.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_GHY**WJBZEKKNPA.jpg)  

这里我们只看判断是否安装过程序，判断是否存在lock文件并且step不等于5的情况下就执行判断语句中的代码，当然这里如果header函数后没有exit就会存在重装漏洞。

我们接着看index.php，光是index.php文件就用413行代码，代码都不规范，所以我们先看看其它文件，看看api.php文件：

![879321_6UAW3GP957TFZ4Q.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_6UAW3GP957TFZ4Q.jpg)  

这里很明显我们看到了SQL注入，首先判断是否设置了$_POST[“dh”]再判断$_POST[“dh”]不为空则将该参数拼接到SQL语句中，看到这里就可以判断出该程序存在联合查询注入，可是$config哪来的，这个文件也没包含其它的文件啊！！！怎么办呢？那么我们就来找找index文件中是否包含了api.php，search一下

![879321_XAD4AMBRERDCUBW.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_XAD4AMBRERDCUBW.jpg)  

可以看到在294行这里包含了api.php文件，我们构造下放入sqlmap中玩一玩

Python sqlmap.py -u “http://localhost:8081/index.php” --batch --dbms=”mysql”
--data=”dh=a”

![879321_MRUQFA43Z63DJF7.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_MRUQFA43Z63DJF7.jpg)  

这里可以看到注入类型确实是联合查询，我们接着尝试下这个提卡网是否存在SQL注入

Python sqlmap.py -u "http://xxxx.pw/index.php" --batch --dbms="mysql"
--data="dh=a"

![879321_D24RR32NXR3KNKM.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_D24RR32NXR3KNKM.jpg)  

我们尝试本地站点的时候毫无问题，可是为啥这个提卡网就存在问题了呢？很明显这个网站可能是升级或者二开过的，我们接着看看其它点，进入./pay/pay.php文件

![879321_TUVEYUCSJQ96ZEQ.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_TUVEYUCSJQ96ZEQ.jpg)  
![879321_9X9ZD469PFRHWNU.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_9X9ZD469PFRHWNU.jpg)

![879321_59JYMQ9XF3TA9FB.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_59JYMQ9XF3TA9FB.jpg)  
![879321_YCJVAPRKWNPY6YC.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_YCJVAPRKWNPY6YC.jpg)

  
![879321_NPGZMGHCN8985DG.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_NPGZMGHCN8985DG.jpg)

  

代码过多就不一一贴图出来了，主要构成漏洞的代码就在这其中，我们从38行开始看着走

这里判断$_GET[“type”]等于delete的时候则执行40-49行的代码，41将获取到的ip拼接到sql语句中，我们看看ip函数：

![879321_5TP36FDMR5TCDNQ.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_5TP36FDMR5TCDNQ.jpg)  
![879321_KJVCPVQE3QQQ7CE.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_KJVCPVQE3QQQ7CE.jpg)

这里可以看到程序获取ip可以从客户端的头参数中获取，分别为HTTP_X_FORWARDED_FOR，HTTP_CLIENT_IP，这个函数真的仅仅是获取外部传递的参数的，一点也没有过滤，我们看到了这里就可以嘿嘿嘿了，基本上这个网站拿下了，我们接着看看，回到41行，再看下边的，我们不宜在这里进行SQL注入，因为接着会将查询到的值又进行下一个SQL语句的拼接，这样返回值就不准确，用工具的过程就很难判断了，我们跳出这里的判断，看看51-54行分别判断了$_GET['type']，$_GET['money']，$_GET['title']，$_GET['pwd']这几个参数存不存在，所以我们这里可以这样构造get参数:type=a&money=1&title=adssad&pwd=123

我们接着看下边的，第58-65行，首先是判断了type是否等于zfb，若不等于则退出当前程序并打印Tip:Type
error!，所以我们还得接着改改get参数：

type=zfb&money=1&title=adssad&pwd=123

接下来，可以看到67行中再次将获取到的ip拼接到了SQL语句中，我们这样来，在67行的下边打印出当前执行的SQL语句

![879321_97A29T6DBWG69W3.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_97A29T6DBWG69W3.jpg)  

好了，现在我们打开burp进行抓包，然后伪造ip进行一系列的嘿嘿嘿了，因为./pay/index.php中包含了pay.php，所以我们对index.php进行注入就好

复现：

访问http://localhost:8081/pay/index.php?type=zfb&money=1&title=adssad&pwd=123

![879321_3XUGDUXSX3XXYMA.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_3XUGDUXSX3XXYMA.jpg)  

可以看到这是一个很正常的页面了，并且打印出了SQL语句，我们抓包

![879321_CXD4Q26R5GFX856.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_CXD4Q26R5GFX856.jpg)  

![879321_R4J59KHM5EP33HS.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_R4J59KHM5EP33HS.jpg)  

正常页面：

![879321_Y6AEJDBN4GXUFJG.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_Y6AEJDBN4GXUFJG.jpg)  

错误页面：

![879321_SXMNJCNY53WQRU8.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_SXMNJCNY53WQRU8.jpg)  

好的，现在看到了吧！我们放到SQLmap中跑一下看看，我们将这个数据包保存到文本中，并且标注注入位置

![879321_H3EHNY2ECJYV8DG.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_H3EHNY2ECJYV8DG.jpg)  

Python sqlmap.py -r test.txt --batch --dbms="mysql"

![879321_5W5ZB9YYKUZ2JEY.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_5W5ZB9YYKUZ2JEY.jpg)  

我们对那个网站测试一番，访问：http://xxxxx.pw/pay/index.php?type=zfb&money=1&title=adssad&pwd=123

![879321_6MNQTHA52MKJ32Y.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_6MNQTHA52MKJ32Y.jpg)  

可以看到缺少spid参数我们加上继续访问：

http://xxxxxx.pw/pay/index.php?type=zfb&money=1&title=adssad&pwd=123&spid=1

![879321_MRRDADZFR3PXCFX.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_MRRDADZFR3PXCFX.jpg)  

把该数据放到文本中，接着进行测试：

![879321_QGFGVQRGRAPWT2U.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_QGFGVQRGRAPWT2U.jpg)  

Python sqlmap.py -r test.txt --batch --dbms="mysql"

![879321_XV46H8HM2PD5DYJ.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_XV46H8HM2PD5DYJ.jpg)  

成功挖掘到了该网站的漏洞，继续。。。。

![879321_WE7CWARQMVESNRT.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_WE7CWARQMVESNRT.jpg)  

Python sqlmap.py -r test.txt --batch -D yulinxscom --tables

![879321_3JCQ8SSC7W5YJSN.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_3JCQ8SSC7W5YJSN.jpg)  

Python sqlmap.py -r test.txt --batch -D yulinxscom -T admin --dump

![879321_R93S52HYTEPQX37.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_R93S52HYTEPQX37.jpg)  

成功拿到了管理账号及密码。。。。。接着来

默认后台：http://xxxxx.pw/admin.php

![879321_P2G2RTZRCNJE93J.jpg](https://zhuanlan.kanxue.com/upload/attach/20200204/879321_P2G2RTZRCNJE93J.jpg)  

由于之前进去过一次，让他亏损了点钱，现在后台的名字也改了 。

写在结尾

跟此网站的搭建人聊了会，从去年11月份搭建平台以来已获利普通人一年的薪资。为了养家糊口，冒此风险也是不容易，切勿为了蝇头小利以身试法，就这样做个记录，到此为止吧。

文中提及技术细节，仅作交流，请勿用于非法活动！！

  
  

