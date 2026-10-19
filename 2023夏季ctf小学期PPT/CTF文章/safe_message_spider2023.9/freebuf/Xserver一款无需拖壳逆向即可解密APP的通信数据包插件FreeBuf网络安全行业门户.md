##  **背景**

 **相信很多小伙伴在日常APP安全测试的过程中都会遇到数据包被加密的情况，如**

![](https://image.3001.net/images/20200603/1591180012_5ed77aec26d11.png!small)

对于像我这种不会拖壳、逆向的菜鸡来说，是很痛苦的，frida的hook老是不成功，写的代码总是运行不起来，别说有多痛苦了，最后找啊找，终于找到了一款xposed的插件Xserver（此处膜拜作者一万年）可以图形化及自动化的协助我们hook想要hook的方法，从而可以协助我们遇到数据加密的场景下对内容进行解密，从而帮助我们继续测试下去,（其实此工具能实现的绝对不止数据加解密，只是平常遇到较多的是这种而已）

(备注：我不是工具作者，我只是工具的搬运工，本文只是一篇工具使用科普而已。。。大佬勿喷)

##  **测试环境**

> WIN10
>
> 逍遥模拟器
>
> Xposed

##  **使用步骤**

由于Xserver 是一款基于Xposed的HOOK框架，所有Xposed的安装是必须的，针对逍遥模拟器，可直接在其应用商店安装即可，

> Xserver的安装地址<https://github.com/monkeylord/XServer>

安装完成后，进入Xserver，会提示模块未激活，

![](https://image.3001.net/images/20200603/1591180165_5ed77b85af681.png!small)

此时可以进入xposed里面看下是否进行了勾选

![](https://image.3001.net/images/20200603/1591180174_5ed77b8e32ffb.png!small)

![](https://image.3001.net/images/20200603/1591180180_5ed77b94d6b9d.png!small)

然后重启模拟器在进入就不会再有提示了，如果还不行，请重装xposed

一切就绪后先通过ADB连接模拟器

![](https://image.3001.net/images/20200603/1591180842_5ed77e2a799df.png!small)

紧接着，需要将Xervser的web端口转发到本地，默认是8000端口

![](https://image.3001.net/images/20200603/1591180849_5ed77e31c4639.png!small)

需要注意的是，如果转发了8000端口本地还访问不到，那可能因为某些原因它初始化的时候没有在8000上，所以这个时候需要通过找PID的值进行转发。

![](https://image.3001.net/images/20200603/1591180857_5ed77e3959277.png!small)

这样子就已经转发成功了，这时候进入Xserver选中待测试的APP

![](https://image.3001.net/images/20200603/1591180864_5ed77e40d0896.png!small)

然后回到桌面，打开被选中的待测试APP后，在本地访问127.0.0.1：8000，即可成功hook的web界面了

![](https://image.3001.net/images/20200603/1591181969_5ed782912796f.png!small)

接下来主要介绍两个功能，一个是trace，访问地址是<http://localhost:8000/tracer>

一个是hook，访问地址是<http://localhost:8000/invoke>

模拟器设置好burp代理，打开待测试的APP，抓包发现返回是加密的

![](https://image.3001.net/images/20200603/1591180888_5ed77e5865bff.png!small)

此处的思路是返回包被加密，那么程序里一定有一个函数或方法会对其进行解密,且一般的解密的函数命名都有decry之类的字符(只是一般情况下)，因此只需对对应的解密函数进行hook就好了，所以我们要做的就是首先加载APP的所有的方法

![](https://image.3001.net/images/20200603/1591180900_5ed77e640332a.png!small)

点击此按钮，加载APP所有的方法

![](https://image.3001.net/images/20200603/1591180914_5ed77e72935be.png!small)

可以看到成功加载了9W＋方法，然后盲猜对应的解密方法中有decry之类的字符，进行匹配

![](https://image.3001.net/images/20200603/1591180952_5ed77e98bf1ce.png!small)

可以看到总共有33个方法，那我们就直接**多所有的方法进行hook,这时回到APP，随意发起网络请求

![](https://image.3001.net/images/20200603/1591180960_5ed77ea09b7af.png!small)

从burp的返回中我们可以看到返回的内容是加密的

![](https://image.3001.net/images/20200603/1591180968_5ed77ea805407.png!small)

不过没关系，我们再去到hook的web界面中可以看到数据包已经被解密出来了，对应的加解密方法、解密密钥也在其中

![](https://image.3001.net/images/20200603/1591180979_5ed77eb3e9426.png!small)

图中的字符为unicode编码，此时只需要再转码一次即可

![](https://image.3001.net/images/20200603/1591181025_5ed77ee1efdfe.png!small)

说完tracer,就该说说invoke了，我对他的理解就是，可以直接脱离测试APP本身，直接通过Xserver进行调用前面hook的方法进行使用，如回到刚刚tracer那里，我们可以看到已经输出了APP中对应的解密方法，因此点击可直接进入此方法的view

![](https://image.3001.net/images/20200603/1591181033_5ed77ee9ec9ac.png!small)

此时我们只需要将对应的参数填进栏目里即可，此时的参数就是从trace中输出的相关参数，注意不要把#号也copy进去

![](https://image.3001.net/images/20200603/1591181045_5ed77ef544ecf.png!small)配置好参数后，点击invoke,即可看到burp中拦截到的请求

![](https://image.3001.net/images/20200603/1591181052_5ed77efc3648f.png!small)

此时将数据包放过去即可

![](https://image.3001.net/images/20200603/1591181058_5ed77f025fa49.png!small)

然后就能看到解密出来的数据包了~~不得不说，Xserver对我这种hook菜鸟来说真的是一大神器啊！

最后再次膜拜作者一万年

 **参考文章:**

> 1.<https://xz.aliyun.com/t/7669>
>
> 2.<https://blog.csdn.net/nini_boom/article/details/104400619>
>
>
> 3.[https://422926799.github.io/posts/ae6e67d.htm](https://422926799.github.io/posts/ae6e67d.html)

 ***本文作者： mouse2，转载请注明来自FreeBuf.COM**  
  

