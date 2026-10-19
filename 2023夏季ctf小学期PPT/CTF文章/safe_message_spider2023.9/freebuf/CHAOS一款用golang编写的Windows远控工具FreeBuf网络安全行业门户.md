## **0x00 前言**

前些天看大佬写的
[APT攻击解析|如何布置鱼竿鱼钩鱼饵](http://www.freebuf.com/column/167257.html)，看到`CHAOS`这个工具便想自己测试一番。

##  **0x01 简介**

[`CHAOS`](https://github.com/tiagorlampert/CHAOS)
是一款用golang编写的Windows远控程序，它可以生成payload和远程控制Windows系统。

github：<https://github.com/tiagorlampert/CHAOS>

##  **0x02 安装**

> 以下过程，我是在kali上测试的。
    
    
    # 安装golang、upx等。
    $ apt install golang xterm git upx-ucl -y
    # 安装第三方库（如：截屏）
    $ go get github.com/kbinani/screenshot && go get github.com/lxn/win
    $ go install github.com/kbinani/screenshot && go install github.com/lxn/win
    # 下载CHAOS源码
    $ git clone https://github.com/tiagorlampert/CHAOS.git
    

安装第三方库的时候可能会报错，如图1：

![图1](https://image.3001.net/images/20180412/15235261573711.png!small)

这个可以不用管 :(

##  **0x03 使用方法**

    
    
    # 运行CHAOS.go
    $ go run CHAOS.go
    

启动界面，如图2：

![图2](https://image.3001.net/images/20180412/1523526174343.png!small)

选项解读：

    
    
    # 生成payload（一般来说都选1）
      [1] Generate
    # 设置并启用监听（前一个选项后续步骤也有次项）
      [2] Listen
    # 启用一个文件服务器（一般来说没什么用）
      [3] Serve
    # 退出
      [4] Quit
    

**选项1** 生成payload，如图3：

![图3](https://image.3001.net/images/20180412/15235261879512.png!small)

设置好本地IP、本地端口和文件名就可以生成一个payload了。

也可以选择加上UPX壳（不过感觉没什么用）。

后续还可以选择是否现在开启端口监听。

 **选项2** 开启端口监听 如图4：

![图4](https://image.3001.net/images/20180412/15235262087850.png!small)

设置好监听端口后就只要等待**上线了 （´Д`）。

 **选项3** 开启一个文件服务器 如图5：

![图5](https://image.3001.net/images/20180412/1523526221444.png!small)

别人就能从这下载生成的payload了 如图6：

![图6](https://image.3001.net/images/20180412/152352623142.png!small)

取得shell 如图7：

![图7](https://image.3001.net/images/20180412/15235262437789.png!small)

接下了就是自由发挥的时候了。你可以截屏、键盘记录、文件上传和下载、打开某个网页、设置是否开机自启动等等。。。

还可以添加用户 如图8：

![图8](https://image.3001.net/images/20180412/15235262697940.png!small)

win下cmd是gbk2312编码的，将kali终端换编码就能正常显示了。

##  **0x04 免杀性**

`CHAOS`生成payload加壳之后被发现的概率还更高（´Д`）。

但是不管加不加壳，360 百度杀毒 迈克菲 金山都不报毒 。

![图9](https://image.3001.net/images/20180412/15235263159181.png!small)

##  **0x05 后记**

新手第一篇文章，如有错误以及一些不妥处还望指正。拜谢。

另附上视频教程

链接：<https://pan.baidu.com/s/1T6mDh2mM0_pM66XXeeC6sA> 密码：6vt9

 *** 本文作者：Zeedger，转载注明来自Freebuf.com**  

