原创AgeloVito合天智汇

## 0x01 前言  

​
在参考了各家waf对于多种姿势检测“冰蝎”的文章之后，产生了改造冰蝎的想法，目前主要的检测手段为针对冰蝎的流量特征进行匹配，所以我们的反侦探手段为改变冰蝎的流量特征以达到绕过的目的，由于@rebeyond大佬没有开源冰蝎代码，所以得反编译。那么思路来了，第一：反编译冰蝎，得到大概的源代码。第二：重新构建项目，让我们反编译后得到的代码跑起来。第三：针对检测规则进行绕过。

## 0x02 反编译冰蝎  

​ 目前反编译java应用的相关工具主要有三种 JD-GUI、luyten、jadx。

### 一、jd-gui  

​ JD-GUI是一个独立的图形实用程序，用于显示“ .class”文件的Java源代码。您可以使用JD-GUI浏览重建的源代码，以立即访问方法和字段。

​ 相关介绍：

![v2-a4b6f8baa1503d0171d536cc9cc8e0f2_hd.p](https://pic3.zhimg.com/80/v2-a4b6f8baa1503d0171d536cc9cc8e0f2_hd.png)

![v2-5ff9ec3cda1b725d5ade6848fdabfae0_hd.p](https://pic1.zhimg.com/80/v2-5ff9ec3cda1b725d5ade6848fdabfae0_hd.png)

​ 下载地址：<http://java-decompiler.github.io/>

​ 目前最新的版本为：jd-gui-1.6.6.jar

### 二、luyten  

​
相关介绍：Luyten是一款很强大的反编译工具包，是一款github的开源工具，软件功能非常强大，界面简洁明晰、操作方便快捷，设计得很人性化。且能够反编译有些jd-gui无法反编译的文件。

![v2-1e095e0d0045706019573cdc0a94f49b_hd.p](https://pic1.zhimg.com/80/v2-1e095e0d0045706019573cdc0a94f49b_hd.png)

​ 下载地址：<https://github.com/deathmarine/Luyten/releases>

### 三、jadx  

​
相关介绍：jadx是一款深受Android开发人员喜爱的反编译利器，同时支持命令行和图形界面，能以最简便的方式完成apk的反编译操作。工具支持apk、dex、jar、aar等格式的文件，可以通过File
- Open file选择文件或者直接将文件拖进窗口中，可以算得上一键反编译了，非常简单易用。

![v2-8a3c2cc26462da04465eff38122a59c8_hd.p](https://pic2.zhimg.com/80/v2-8a3c2cc26462da04465eff38122a59c8_hd.png)

​ 下载地址：<https://github.com/skylot/jadx/releases>

### 四、Import Jar As Project  

​ Import Jar As Project 是一款eclipse插件，用于将.jar或.war作为项目导入到Eclipse
IDE中，即使您没有通过反编译jar来获取源代码。

​ 官网地址：<https://github.com/helospark/import-jar-as-project>

![v2-a8312c293728b1bbf678a72cb5f446b4_hd.p](https://pic4.zhimg.com/80/v2-a8312c293728b1bbf678a72cb5f446b4_hd.png)

​
对于具体如何反编译Behinder.jar到在eclipse中运行起来Behinder的详细过程本文不累述，因为这是耗时的体力活，我们要解决很多问题，很多没有java基础的童鞋也看不懂。这里只讲大概思路，首先我们可以通过Import
Jar As
Project插件将Behinder.jar导入eclipse，这样在ecplise中就创建了一个存在一堆报错的Behinder项目，然后再利用上文提到的三款反编译软件对Behinder.jar进行反编译，将每个文件以及每个java类中的方法进行对比，修改eclipse项目中的对应代码，在运用eclipse的相关报错信息进行有关反编译代码的排错，修改。这里解释一下为什么要用三款反编译软件，因为各自的优缺点不一样，反编译出来的代码也是不一样的，所以得综合尝试。

​ 在没有进行任何修改的情况下导入eclipse后的情况如图所示：

![v2-7be0b17440a56da4c0df04a0338c6115_hd.p](https://pic4.zhimg.com/80/v2-7be0b17440a56da4c0df04a0338c6115_hd.png)

​ 可以看到，基本每个java文件都存在错误。

### 五、最终效果  

​ 在长达两个工作日的不断排错后，终于成功的跑起来了我们反编译后的代码

![v2-e7c4ccce6833a80940b511f9550064ac_hd.p](https://pic1.zhimg.com/80/v2-e7c4ccce6833a80940b511f9550064ac_hd.png)

​ 出于对原作者的尊重，这里不放出项目文件。

复制下方链接做实验，反编译工具的使用：

[实验:反编译工具的使用(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID9d6c0ca797abec2016050410555500001)

## 0x03 对抗分析  

​ 网上对冰蝎流量检测的文章主要是以下三篇：

第一：“基于流量侧检测冰蝎webshell交互通讯”

链接：https://blog.csdn.net/qq_36334464/article/details/99978193

第二：“流量加密又怎样？ 多种姿势检测“冰蝎””

链接：https://www.freebuf.com/articles/web/216133.html

第三：“那些年我们堵住的洞 – OpenRASP纪实”

链接：https://anquan.baidu.com/article/855

​ 检测手段：按照“静态特征”编写两类规则：1.密钥传递规则。2.加密通讯规则。

如果同一个url或者源IP在数秒内内同时命中了这两种规则，那么可以非常肯定的确认是冰蝎了。注意，此处是同一个URL或者源IP，而不是同一个TCP会话，密钥传递和加密通讯未必是同一个TCP会话（源端口会变化）。

​ 对抗思路：既然是同时命中两种规则，是 ”与" 的关系，那么我们只需要让第一个条件 “密钥传递规则” 不被waf匹配到就行了。

​ 密钥传递规则主要包括如下几个方面：

### 弱特征1：密钥传递时URL参数  

![v2-6ea6218dcf06a78a305c8b7da95c5ef5_hd.p](https://pic2.zhimg.com/80/v2-6ea6218dcf06a78a305c8b7da95c5ef5_hd.png)

​ 对抗思路：增加随机数量的随机参数和随机值，修改冰蝎的随机数规则

![v2-9f74b3830d8ca3f03dc738085ae01c1d_hd.p](https://pic3.zhimg.com/80/v2-9f74b3830d8ca3f03dc738085ae01c1d_hd.png)

### 弱特征2：加密时的URL参数  

​ 在加密通讯过程中，没有URL参数。是的，没有参数本身也是一种特征。

​ 对抗思路：在加密通讯的请求上增加 随机数量的随机参数和随机值 的URL参数

![v2-96375dfc594aca8db34351a09c27fab0_hd.p](https://pic3.zhimg.com/80/v2-96375dfc594aca8db34351a09c27fab0_hd.png)

### 强特征3：Accept字段（可绕过）  

​
Accept是HTTP协议常用的字段，但冰蝎默认Accept字段的值却很特殊，我也没有想明白为什么要设置这么一个奇怪的值。这个特征存在于冰蝎的任何一个通讯阶段。

Accept: text/html,image/gif, image/jpeg, *; q=.2, */*; q=.2

​
这里对于原作者的（没有想明白），我给出一下解释，冰蝎可以自定义请求头，如果在没有自定义请求头的情况下，Accept的值是使用java代码发送请求时没有设置Accept时自带的。

setRequestProperty("Accept", "*/*");

![v2-c9896146367c935211c1d0b5d912d695_hd.p](https://pic2.zhimg.com/80/v2-c9896146367c935211c1d0b5d912d695_hd.png)

​ 对抗思路：虽然这个强特征用户是可以通过自定义绕过的，我还是在代码里面改了

![v2-8413ce8d97799011f03e0850093f118a_hd.p](https://pic4.zhimg.com/80/v2-8413ce8d97799011f03e0850093f118a_hd.png)

### 强特征4：UserAgent字段（可绕过）  

​ UserAgent也是可以自定义的

![v2-5f3bb526b039bec3bb59c639***f57f8_hd.p](https://pic1.zhimg.com/80/v2-5f3bb526b039bec3bb59c639***f57f8_hd.png)

​ 对抗思路：虽然可以自定义，我还是修改了自带的，因为我平时自己使用的时候也没有填写的习惯......

![v2-66b0824a84286e7e336777b30010d07e_hd.p](https://pic3.zhimg.com/80/v2-66b0824a84286e7e336777b30010d07e_hd.png)

### 强特征5：传递的密钥  

​ 加密所用密钥是长度为16的随机字符串，小写字母+数字组成。密钥传递阶段，密钥存在于Response Body中，如图。

![v2-ce79a519835e89f89f19b7189f96925c_hd.p](https://pic2.zhimg.com/80/v2-ce79a519835e89f89f19b7189f96925c_hd.png)

![v2-8a1e393a93420e882a6d94fa8bb3dea8_hd.p](https://pic3.zhimg.com/80/v2-8a1e393a93420e882a6d94fa8bb3dea8_hd.png)

​ 对抗思路：其实最稳妥的方式就是 删减传递秘钥
的过程，将秘钥硬编码在客户端和服务器端，具体的做法有，一、每次打开冰蝎的时候生成一个秘钥，然后生成带密钥硬编码的服务器端（jsp、asp、php...）。二、将秘钥存放在某个文件中如（key.ini）由用户自定义，Behinder.jar去读取key，服务器端中的秘钥让用户手动修改。

但是，我不喜欢这种模式，或者说我懒，因为这样的话，需要修改的代码就太多了,包括java代码，jsp，jspx，php，aspx，asp脚本文件。不仅耗时而且对冰蝎的侵入式修改较大。

转变思路，我们可以看到冰蝎原来的请求顺序是一：客户端请求秘钥，服务器端返回秘钥，第二，客户端拿到秘钥然后发送POST请求。waf也是针对这个顺序进行匹配的。所以我们只需要打乱这个顺序让waf无法匹配到这个规律从而不会去进行下一步的探测就行了。基于这个想法我加入了在每次客户端get请求秘钥的中间插入
随机数量的get 请求http://xxx.xxx.xxx/。当然请求的当然是当前域名或者ip

​ 原请求顺序：

![v2-a3d7349ad1aed266bd0086bbca78a925_hd.p](https://pic3.zhimg.com/80/v2-a3d7349ad1aed266bd0086bbca78a925_hd.png)

​ 打乱请求顺序：

![v2-b764a00abcaca66c99306b4bda991a91_hd.p](https://pic2.zhimg.com/80/v2-b764a00abcaca66c99306b4bda991a91_hd.png)

到这里，基本上waf也认识不了啥了，更别说后续的会去拿到密钥去动态分析。

实验推荐：应用防火墙WAF

[课程:应用防火墙WAF(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=C9d6c0ca797abec2017041916505100001)

点击上方链接

### 针对 OpenRASP  

​ 原文章是这么说的：

​ 演练期间见到最多的就是冰蝎动态后门了，其中JSP版本通过自定义ClassLoader + defineClass方法来实现eval特性。

new U(this.getClass().getClassLoader()).g(c.doFinal(new
sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()))).newIns
tance().equals(pageContext);

​ 因为流量是AES双向加密的，对绕过WAF和IDS会比较有效。但部署在应用内部的OpenRASP，还是能够看到后门操作（安装 999-event-logger 插件即可看到日志）:

[event-logger] Listing directory content:/ [event-logger] Execute command:
whoami java.lang.ProcessBuilder.start ...
net.rebeyond.behinder.payload.java.Cmd.RunCMD
net.rebeyond.behinder.payload.java.Cmd.equals

​
合天网安实验室的《AES加密算法分析》，让你学习理解对称加密算法AES的原理，使用CrypTool对特定明文/密文使用AES进行加解密，体会AES算法的加解密过程。

[实验:AES加密算法分析(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID7256-c8c6-49fe-84fd-86ed71c56daf)

同样，我们依然可以通过命令执行的堆栈识别冰蝎：

java.lang.ProcessBuilder.start
...net.rebeyond.behinder.payload.java.Cmd.RunCMD
net.rebeyond.behinder.payload.java.Cmd.equals

​ 因此，无论服务端的JSP如何变形，只要客户端代码不变，我们通过校验堆栈就可以检测冰蝎动态后门。目前最新版的JS插件 2019-0703-1600
已经支持防护。

​ 对抗思路：OpenRASP 已经说得很明白了，也很务实，很欣赏这种务实的态度，不然安全行业怎么发展呢，不像某些waf收费贵的一X，流批吹的凶，结果
唠跨松。跑题了。。。

​ 我们也不需要做大改，只需要改变冰蝎的包结构就行了，我就直接去掉了net.rebeyond.behinder这三层包。

![v2-700c1aae14af835f1985d062e89d34fd_hd.p](https://pic2.zhimg.com/80/v2-700c1aae14af835f1985d062e89d34fd_hd.png)

![v2-b92c2724b8b67e0fd5bbac6686cfaf98_hd.p](https://pic1.zhimg.com/80/v2-b92c2724b8b67e0fd5bbac6686cfaf98_hd.png)

## 0x04 成果检验  

环境：apache-tomcat-7.0.96 + rasp-2019-12-17

![v2-78edf6b9357ad4b9d70caae826975ee4_hd.p](https://pic1.zhimg.com/80/v2-78edf6b9357ad4b9d70caae826975ee4_hd.png)

​ 打开webshell

![v2-880351117eaa82a9be8f538a383cf4c6_hd.p](https://pic4.zhimg.com/80/v2-880351117eaa82a9be8f538a383cf4c6_hd.png)

​ 对应的请求

![v2-fd5b2e4839c3fc6a7ef2e05a4ea3a719_hd.p](https://pic2.zhimg.com/80/v2-fd5b2e4839c3fc6a7ef2e05a4ea3a719_hd.png)

### 命令执行  

![v2-2c6f116d0329d2c2f65a3e997f6ce55e_hd.p](https://pic1.zhimg.com/80/v2-2c6f116d0329d2c2f65a3e997f6ce55e_hd.png)

### 虚拟终端  

![v2-95ed65b2af42e9b91b052ea5708b2d07_hd.p](https://pic3.zhimg.com/80/v2-95ed65b2af42e9b91b052ea5708b2d07_hd.png)

### 文件管理  

![v2-317aa6186f8bc81f3a7c95317218d7b6_hd.p](https://pic3.zhimg.com/80/v2-317aa6186f8bc81f3a7c95317218d7b6_hd.png)

### 数据库管理  

![v2-0cb3c3271eaef2745690024298b7e525_hd.p](https://pic3.zhimg.com/80/v2-0cb3c3271eaef2745690024298b7e525_hd.png)

### 下载地址  

链接：<https://pan.baidu.com/s/1wd8AreiyudZUHNgFbS2b2A>提取码：a9ef

仅供参考学习，切勿用作非法用途。

## 0x05 总结  

​ 由于是反编译出来的代码，有许多bug，例如此版本不支持tomcat6 asp aspx，反弹shell功能无法成功。

期间也得到了@rebeyond大佬的指点，非常感谢。原作者也说了年后会再次更新，敬请期待。

Author：AgeloVito

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

