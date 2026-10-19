**今天给大家介绍的是一款名叫ISeeYou的强大社工工具，该工具基于Bash和JavaScript开发，可帮助研究人员在进行社工技术测试或网络钓鱼培训过程中快速定位目标用户的确切地理位置。在拿到目标用户的地理位置坐标之后，研究人员就可以对目标用户展开基础的网络侦察活动，并执行进一步的测试。**

![1.png](https://image.3001.net/images/20190427/1556351155_5cc408b38762d.png!small)

### 注意

1、 在进行网络钓鱼测试时，该工具不需要任何其他的软件辅助。

2、 用户可以通过查看日志文件来解码地理位置坐标。

## 工具安装

    
    
    git clone <https://github.com/Viralmaniar/I-See-You.git>
    
    cd I-See-You
    
    chmod u+x ISeeYou.sh
    
    ./ISeeYou.sh

![2.png](https://image.3001.net/images/20190427/1556351180_5cc408cc4ad8b.png!small)

## 工具截图

运行ISeeYou.sh文件后，用户将看到如下图所示的界面：

![3.png](https://image.3001.net/images/20190427/1556351196_5cc408dcba7cc.png!small)

输入图中框出来的URL地址之后，按下回车键：

![4.png](https://image.3001.net/images/20190427/1556351207_5cc408e7822f8.png!small)

需要注意的是，这个URL地址是根据不同的用户随机生成的，所有生成的地址都为serveo.net域名下的子域名。我们可以在网络钓鱼活动中通过电子邮件或其他方式把这个URL地址发给你的目标用户，用户点击访问后将看到如下图所示的界面：

![5.png](https://image.3001.net/images/20190427/1556351217_5cc408f13d759.png!small)

当然了，你也可以根据自己的需要来修改这个Web页面。

当目标用户允许页面拥有地理位置访问权限后（需要想办法隐藏请求），我们将会收到目标用户的实际地理位置信息，其中的数字即为目标用户的经纬度数据。

![6.png](https://image.3001.net/images/20190427/1556351230_5cc408fec35e2.png!small)

大家可以访问<https://maps.google.com>或其他地图服务来将经纬度数据转码为地理位置。

![7.png](https://image.3001.net/images/20190427/1556351246_5cc4090eaf024.png!small)

## Xterm使用方法

Xterm允许我们选择需要从剪贴板拷贝过来的数据数量：

1、 添加或创建~/.Xresources文件；

2、 设置如下参数：

    
    
    XTerm*selectToClipboard:true

3、 运行下列命令：

    
    
    xrdb-merge ~/.Xresources

4、 重启xterm

## 项目地址

ISeeYou：【[GitHub传送门](https://github.com/Viralmaniar/I-See-You)】

 ***参考来源：[Viralmaniar](https://github.com/Viralmaniar/I-See-You)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

