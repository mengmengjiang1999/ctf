## Ewomail及gophish环境问题

这里使用Ewomail+gophish，那么我们先来看看它的两个实验环境问题，当然实战中Ewomail还是很少用的

### Ewomail

邮箱搭建成功如下：

![1667832880_63691c30c3e8f903ec740.png!small?1667832881303](https://image.3001.net/images/20221107/1667832880_63691c30c3e8f903ec740.png!small?1667832881303)

  

在后端先创建两个邮箱

  

然后我们在前端页面登陆账号

![1667832916_63691c54adb450ba5272d.png!small?1667832917425](https://image.3001.net/images/20221107/1667832916_63691c54adb450ba5272d.png!small?1667832917425)

  

但是登陆时候发现域不允许

![1667832932_63691c64d9bcf84c620b1.png!small?1667832933385](https://image.3001.net/images/20221107/1667832932_63691c64d9bcf84c620b1.png!small?1667832933385)

  

解决方法：

在开启Ewomail的服务器上面的/etc/hosts中加入如下内容：

  

    
    
      
    

127.0.0.1 mail.qiezi.shop qiezi.shop smtp.qiezi.shop imap.qiezi.shop

![1667833253_63691da557ab4a107ef73.png!small?1667833254435](https://image.3001.net/images/20221107/1667833253_63691da557ab4a107ef73.png!small?1667833254435)

  

然后发送邮件

![1667833296_63691dd0efdf46fab01eb.png!small?1667833297582](https://image.3001.net/images/20221107/1667833296_63691dd0efdf46fab01eb.png!small?1667833297582)

![1667833321_63691de910c41db91c490.png!small?1667833321958](https://image.3001.net/images/20221107/1667833321_63691de910c41db91c490.png!small?1667833321958)

  

那么我们上hdh号再看看

![1667833360_63691e106b130e125f46e.png!small?1667833360968](https://image.3001.net/images/20221107/1667833360_63691e106b130e125f46e.png!small?1667833360968)

  

可以看到成功收到邮件

  

### gophish

  

然后我们来介绍gophish

  

测试连接

![1667833471_63691e7f7604922f5af41.png!small?1667833472005](https://image.3001.net/images/20221107/1667833471_63691e7f7604922f5af41.png!small?1667833472005)

报错如上图，可以看到是因为DNS解析不到mtp.qiezi.shop  
解决方法https://blog.csdn.net/weixin_43064185/article/details/112379032  
也就是加域名hosts

![1667833490_63691e92963088bc2ddc9.png!small?1667833491154](https://image.3001.net/images/20221107/1667833490_63691e92963088bc2ddc9.png!small?1667833491154)

  

我们更改如下：

/etc/hosts文件：

![1667833561_63691ed97c223f28ada28.png!small?1667833561945](https://image.3001.net/images/20221107/1667833561_63691ed97c223f28ada28.png!small?1667833561945)

  

/etc/resolv.conf文件：

![1667833603_63691f031f400e9791b47.png!small?1667833603549](https://image.3001.net/images/20221107/1667833603_63691f031f400e9791b47.png!small?1667833603549)

  

再次测试：

![1667833688_63691f58b296f0e32756a.png!small?1667833689550](https://image.3001.net/images/20221107/1667833688_63691f58b296f0e32756a.png!small?1667833689550)

  

可以看到成功ping通，我们回网页看看

![1667833715_63691f73a1c8eec3db8d6.png!small?1667833716140](https://image.3001.net/images/20221107/1667833715_63691f73a1c8eec3db8d6.png!small?1667833716140)

  

新的报错，应该是我们的本机服务器25端口没有开放，我查了下果真没开放

![1667833829_63691fe5a676a98737857.png!small?1667833830290](https://image.3001.net/images/20221107/1667833829_63691fe5a676a98737857.png!small?1667833830290)

  

那么我们需要开启25端口，那么我们就需要搭建一个25端口的邮箱服务，我们选Postfix邮件服务器

![1667833913_636920395882f2f835d08.png!small?1667833913863](https://image.3001.net/images/20221107/1667833913_636920395882f2f835d08.png!small?1667833913863)

  

可以看到没有25端口

我们安装Postfix服务

  

    
    
    sudo apt update
    sudo DEBIAN_PRIORITY=low apt install postfix

  

参考链接：<https://blog.csdn.net/oMcLin/article/details/107904184>

  

  

安装成功后

![1667834015_6369209fe28e696f5a838.png!small?1667834016367](https://image.3001.net/images/20221107/1667834015_6369209fe28e696f5a838.png!small?1667834016367)

  

我们看到25端口开了

那么我们继续连接测试，可以看到发不过去，因为我们Ewomail搭建的用的是阿里云服务器，那么25端口是开放不了的，我们的gophish是搭建在另一台非国内服务器上的，所以Ewomail对外不能接受和发送邮件

![1667834054_636920c60a620d37e5d2c.png!small?1667834054649](https://image.3001.net/images/20221107/1667834054_636920c60a620d37e5d2c.png!small?1667834054649)

  

那么我们试试qq的

![1667834290_636921b280b3122f3d3bc.png!small?1667834290845](https://image.3001.net/images/20221107/1667834290_636921b280b3122f3d3bc.png!small?1667834290845)

  

可以看到成功发送，但是qq那边没有收到，应该是被拦掉了

试试匿名邮箱

![1667834329_636921d9ef07ad9bf3f61.png!small?1667834330430](https://image.3001.net/images/20221107/1667834329_636921d9ef07ad9bf3f61.png!small?1667834330430)

  

![1667834412_6369222cbc55aa1babd42.png!small?1667834413198](https://image.3001.net/images/20221107/1667834412_6369222cbc55aa1babd42.png!small?1667834413198)

  

成功收到，

  

  

## gophish的使用

  

我们来介绍gophish的使用

  

![1667834490_6369227a14ce8efd9bbf0.png!small?1667834490625](https://image.3001.net/images/20221107/1667834490_6369227a14ce8efd9bbf0.png!small?1667834490625)

我们以跳转网易邮箱登陆页面为例子

![1667834548_636922b4b4ec7526e2fba.png!small?1667834549223](https://image.3001.net/images/20221107/1667834548_636922b4b4ec7526e2fba.png!small?1667834549223)

  

可以看到刚才我们导入的网易邮箱登陆页面已经生成，然后选择抓取加载的数据，抓取密码，下面的Redirect
to是如果密码错误跳转到哪里（我们演示错误跳转到百度）

保存如下：

![1667834576_636922d0b01e5d2f3617a.png!small?1667834577341](https://image.3001.net/images/20221107/1667834576_636922d0b01e5d2f3617a.png!small?1667834577341)

  

然后我们写邮件，

![1667834636_6369230cc8fad765735aa.png!small?1667834637332](https://image.3001.net/images/20221107/1667834636_6369230cc8fad765735aa.png!small?1667834637332)

![1667834673_6369233115b0e7f15c0e2.png!small?1667834673660](https://image.3001.net/images/20221107/1667834673_6369233115b0e7f15c0e2.png!small?1667834673660)

  

加入钓鱼链接（我们这里以百度为例，点击链接即可跳转到百度）

我试了一下不能通过Ewomail向外面邮箱发送，还是因为阿里云禁用了25端口，只能本地给自己发送，那么我们就发送给test@qiezi.shop，向外发送的话用gophish即可

![1667834717_6369235dc8dafcc3857c8.png!small?1667834718378](https://image.3001.net/images/20221107/1667834717_6369235dc8dafcc3857c8.png!small?1667834718378)

![1667836837_63692ba5e634fe634156e.png!small?1667836839128](https://image.3001.net/images/20221108/1667836837_63692ba5e634fe634156e.png!small?1667836839128)

  

然后我们点击导出eml文件

然后我们打开eml文件，然后如下进行操作

![1667834797_636923ad18a13a2ee3dbf.png!small?1667834797879](https://image.3001.net/images/20221107/1667834797_636923ad18a13a2ee3dbf.png!small?1667834797879)

  

可以看到![1667834830_636923ce3b9db2d95e33e.png!small?1667834830687](https://image.3001.net/images/20221107/1667834830_636923ce3b9db2d95e33e.png!small?1667834830687)

  

钓鱼术语自动导入进去，保存即可

![1667834843_636923db45e2d5184e7ce.png!small?1667834843841](https://image.3001.net/images/20221107/1667834843_636923db45e2d5184e7ce.png!small?1667834843841)

  

然后我们来进行钓鱼目标

![1667834901_6369241549330368988fd.png!small?1667834901940](https://image.3001.net/images/20221107/1667834901_6369241549330368988fd.png!small?1667834901940)

  

这里可以导入全部目标，我们只写我们的一个

![1667834879_636923ffa1869db1915e9.png!small?1667834880421](https://image.3001.net/images/20221107/1667834879_636923ffa1869db1915e9.png!small?1667834880421)

  

这里我们钓鱼对象配置完成了，之前的钓鱼配置也设置好了，如下

![1667834921_6369242948302d92f134e.png!small?1667834921747](https://image.3001.net/images/20221107/1667834921_6369242948302d92f134e.png!small?1667834921747)

  

钓鱼页面也做好了，如下：

![1667834936_6369243813c2568418bd7.png!small?1667834936513](https://image.3001.net/images/20221107/1667834936_6369243813c2568418bd7.png!small?1667834936513)

  

钓鱼内容也做好了，如下：

![1667834953_6369244917c34fcdaa593.png!small?1667834953503](https://image.3001.net/images/20221107/1667834953_6369244917c34fcdaa593.png!small?1667834953503)

  

那么我们开始发送，配置如下：

![1667834996_636924746a33cf5e908a1.png!small?1667834996924](https://image.3001.net/images/20221107/1667834996_636924746a33cf5e908a1.png!small?1667834996924)

  

这里配置gophish配置的vps的ip:8888，是因为是404页面

![1667835060_636924b4573d31c391ec0.png!small?1667835060702](https://image.3001.net/images/20221107/1667835060_636924b4573d31c391ec0.png!small?1667835060702)

  

  

可以用来将钓鱼页面走这个网站

![1667835092_636924d45b0b0ced207bc.png!small?1667835092854](https://image.3001.net/images/20221107/1667835092_636924d45b0b0ced207bc.png!small?1667835092854)

  

可以看到发送成功

![1667835166_6369251eed446e6b6ebbb.png!small?1667835167405](https://image.3001.net/images/20221107/1667835166_6369251eed446e6b6ebbb.png!small?1667835167405)

  

可以看到成功收到，我们点击链接

![1667835209_63692549b7628ae8f2e2b.png!small?1667835210230](https://image.3001.net/images/20221107/1667835209_63692549b7628ae8f2e2b.png!small?1667835210230)

  

跳转到了钓鱼页面也就是我们的网易邮箱登陆页面，

我们在网站输入账号密码试试能否成功登陆

![1667835228_6369255cee0c813b06dc7.png!small?1667835229442](https://image.3001.net/images/20221107/1667835228_6369255cee0c813b06dc7.png!small?1667835229442)

错误账户密码跳转到百度页面

![1667835272_63692588c8dbeca7cfea6.png!small?1667835273287](https://image.3001.net/images/20221107/1667835272_63692588c8dbeca7cfea6.png!small?1667835273287)

  

可以看到点击且提交了数据，我们可以看到提交的内容

![1667835368_636925e88b960f0bc87f3.png!small](https://image.3001.net/images/20221107/1667835368_636925e88b960f0bc87f3.png!small)

  

可以看到点击且提交了数据，我们可以看到提交的内容

  

到这里就完整的gophish使用结束了

  

## 伪造发件人

当SPF没有或者配置不当时候将可被利用

  

![1667835902_636927feb7574ef33646d.png!small?1667835903170](https://image.3001.net/images/20221107/1667835902_636927feb7574ef33646d.png!small?1667835903170)

可以看到未配置好SPF

![1667835691_6369272b2d5be1f4697a9.png!small?1667835693196](https://image.3001.net/images/20221107/1667835691_6369272b2d5be1f4697a9.png!small?1667835693196)

可以看到成功利用

![1667836091_636928bb85df25bf1b2ad.png!small?1667836092779](https://image.3001.net/images/20221107/1667836091_636928bb85df25bf1b2ad.png!small?1667836092779)

可以看到qq无法成功利用，因为其配置好了v=spf1

