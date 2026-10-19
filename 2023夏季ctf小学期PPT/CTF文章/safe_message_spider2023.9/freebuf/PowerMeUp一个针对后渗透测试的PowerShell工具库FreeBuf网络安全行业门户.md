![](https://image.3001.net/images/20230517/1684312013_64648fcda9d768c9f4320.jpeg!small)

## 关于PowerMeUp

PowerMeUp是一个针对后渗透测试的PowerShell工具库，除此之外，它还是一个支持自定义开发的反向Shell，广大研究人员可以根据自己的需求向其中添加功能模块或删除不需要的部分。

值得注意的是，该工具还支持执行后渗透利用和横向移动等渗透测试任务，并且Windows Defender当前还无法检测到这个反向Shell。

## 功能介绍

> 1、反向Shell支持；
>
> 2、BSOD蓝屏关机；
>
> 3、禁用Windows Defender；
>
> 4、获取目标计算机信息；
>
> 5、禁用输入；（需要管理员权限）
>
> 6、禁用监视器Monitor；
>
> 7、排除文件扩展；（需要管理员权限）
>
> 8、排除文件夹；（需要管理员权限）
>
> 9、排除进程；（需要管理员权限）
>
> 10、获取USB历史记录；
>
> 11、获取GPS地理位置信息；
>
> 12、获取WiFi凭证；
>
> 13、Ifconfig；
>
> 14、获取运行的反病毒产品清单；
>
> 15、获取外部IP地址；
>
> 16、网络扫描（IP、开放端口）；
>
> 17、重启电脑；
>
> 18、获取屏幕截图；
>
> 19、获取系统时间；
>
> 20、获取网络摄像头列表；

## 工具下载

广大研究人员可以直接使用下列命令将该项目源码克隆至本地：

    
    
    $ git clone https://github.com/ItsCyberAli/PowerMeUp.git

## 工具使用

在使用该工具之前，我们需要在目标设备PC上执行powerreverse.ps1文件。

接下来，修改powerreverse.ps1中热的LHOST和LPORT参数：

    
    
    $LHOST = "你的C2 IP"
    
    $LPORT = 端口号（不需要使用双引号或单引号括起来）

启动一个Netcat监听器，或你自己在VPS或C2上部署的监听器：

    
    
    $ nc -l -p <port you chose>

![](https://image.3001.net/images/20230517/1684312062_64648ffe7948c3c8aeb63.png!small)

## 工具演示视频

 **视频地址** ：【[ _点我观看_](https://user-images.githubusercontent.com/111126641/196739945-28fa69e0-c0c5-46da-954c-ce15eaf03a96.webm)】

## 项目地址

 **PowerMeUp** ：【[ _GitHub传送门_](https://github.com/ItsCyberAli/PowerMeUp)】

