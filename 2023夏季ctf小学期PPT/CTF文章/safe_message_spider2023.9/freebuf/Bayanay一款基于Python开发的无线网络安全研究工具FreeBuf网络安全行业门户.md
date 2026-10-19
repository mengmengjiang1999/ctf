![](https://image.3001.net/images/20221007/1665115916_633fa70c8e19008fbb3ef.jpeg!small)

## 关于Bayanay

Bayanay是一款基于纯Python开发的无线网络安全研究工具，在该工具的帮助下，无论你身处何地，都可以轻松地对周围地区的无线网络安全状况进行研究与分析。

该工具可以通过使用HTML5的地理位置定位功能并结合Scapy获取到的SSID信息来对目标无线网络进行渗透测试与安全研究。

## 工具下载

该工具基于纯Python开发，因此该工具具备良好的跨平台特性。首先，我们需要在本地设备上安装并配置好Python环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/anil-yelken/wardriving.git

## 工具使用

项目提供的ssidBul.py已通过TP-LINK TL WN722N进行过测试。

其中的location.py脚本已在Selenium 3.11.0和Firefox
59.0.2上进行过测试，Firefox浏览器所需的geckodriver位于代码所在的目录中。

在使用该工具之前，我们需要在测试环境中创建并更改SSID和MAC名称及位置信息。

ssidBul.py和location.py必须同时运行。

## 工具使用样例

ssidBul.py的运行结果样例如下：

    
    
    20 March 2018 11:48PM|9c:b2:b2:11:12:13|ECFJ3M
    
     
    
    20 March 2018 11:48PM|c0:25:e9:11:12:13|T7068

下图显示的是location.py运行后地理位置信息获取授权弹窗截图：

![](https://image.3001.net/images/20221007/1665115942_633fa726168b8cdbdbb05.jpg!small)

下图显示的是工具脚本运行后最终获取到的地理位置信息：

![](https://image.3001.net/images/20221007/1665115947_633fa72bd035a4d6b1190.jpg!small)

konum.py脚本的运行结果如下所示：

    
    
    lat=38.8333635|lon=34.759741899|20 March 2018 11:47PM
    
     
    
    lat=38.8333635|lon=34.759741899|20 March 2018 11:48PM
    
     
    
    lat=38.8333635|lon=34.759741899|20 March 2018 11:48PM
    
     
    
    lat=38.8333635|lon=34.759741899|20 March 2018 11:48PM
    
     
    
    lat=38.8333635|lon=34.759741899|20 March 2018 11:48PM
    
     
    
    lat=38.8333635|lon=34.759741899|20 March 2018 11:49PM
    
     
    
    lat=38.8333635|lon=34.759741899|20 March 2018 11:49PM

数据收集阶段的任务完成直走，我们就可以通过运行wardriving.py脚本来获取如下所示的输出结果样例了：

    
    
    lat=38.8333635|lon=34.759741899|20 March 2018 11:48PM|9c:b2:b2:11:12:13|ECFJ3M
    
     
    
    lat=38.8333635|lon=34.759741899|20 March 2018 11:48PM|c0:25:e9:11:12:13|T7068

## 许可证协议

本项目的开发与发布遵循[ _GPL_ _-3.0_](https://github.com/anil-yelken/wardriving/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Bayanay** ：【[ _GitHub传送门_](https://github.com/anil-yelken/wardriving)】

## 参考资料

> [ _https://twitter.com/anilyelken06_](https://twitter.com/anilyelken06)
>
> [ _https://medium.com/@anilyelken_](https://medium.com/@anilyelken)

