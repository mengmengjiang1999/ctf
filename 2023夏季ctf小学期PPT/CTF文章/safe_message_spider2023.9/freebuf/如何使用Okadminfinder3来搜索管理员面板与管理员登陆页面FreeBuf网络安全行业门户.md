**今天给大家介绍的是一款名叫Okadminfinder3的工具，广大研究人员可以在渗透测试的过程中，利用它来查找目标程序的管理员面板接口或管理员账户登录地址。**

![222222222222222.png](https://image.3001.net/images/20190429/1556552150_5cc719d64b799.png!small)  

OKadminFinder采用Python
3.x开发，是一款Apache2实用工具。如果你在渗透测试的过程中需要寻找网站的管理员入口或管理员界面，OKadminFinder就是你要的东西！虽然现在网络上有很多类似功能的工具，但这些工具无论是从效率上来看，还是从安全性上来看，或多或少都没有OKadminFinder优秀。值得一提的是，OKadminFinder还可以使用Tor来隐藏你的活动痕迹。

## 工具依赖

    
    
    1、 argparse v1.4.0
    
    2、 colorama v0.4.1
    
    3、 PySocks v1.6.8
    
    4、 tqdm v4.31.1
    
    5、 requests v2.21.0

## Linux配置

    
    
    sudo apt install tor
    
    sudo apt install python3-socks  (optional)
    
    pip3 install --user -r requirements.txt

## Windows配置

下载Tor Bundle：【[点我下载](https://dist.torproject.org/torbrowser/8.0.8/tor-win32-0.3.5.8.zip)】

然后运行下列命令完成依赖组件的安装：

    
    
    pip3 install -r requirements.txt

## 工具演示

视频地址：<https://asciinema.org/a/209959>

### Linux平台：

    
    
    git clone <https://github.com/mIcHyAmRaNe/okadminfinder3.git>
    
    cd okadminfinder3
    
    chmod +x okadminfinder.py
    
    python3 okadminfinder.py

### Windows平台：

下载并提取这个【[ZIP](https://github.com/mIcHyAmRaNe/okadminfinder3/archive/master.zip)】文档，然后运行下列命令：

    
    
    cd okadminfinder3
    
    py -3 okadminfinder.py

### Pentestbox：

你可以将下列代码添加至“C://Pentestbox/bin/customtools/customaliases”文件中，这样我们就可以直接使用命令“okadminfinder”来启动该工具了：

    
    
    okadminfinder=py-3 "%pentestbox_ROOT%/bin/Path/to/okadminfinder3/okadminfinder.py" $*

## 功能介绍

1、 支持超过500中管理员面板；

2、 支持Tor&代理；

3、 随机Agent；

4、 控制台支持参数控制，例如：

    
    
    okadminfinder.py -u example.com --proxy 127.0.0.1:8080

### 项目地址

Okadminfinder3：【[GitHub传送门](https://github.com/mIcHyAmRaNe/okadminfinder3/archive/master.zip)】

***参考来源：[mIcHyAmRaNe](https://github.com/mIcHyAmRaNe/okadminfinder3)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

