**[ꓘamerka](https://github.com/woj-ciech/kamerka)是一个用于构建交互式摄像头地图的python脚本。其原理是调用Shodan
API来查找摄像头，再使用Geopy进行定位和测距，并最终通过Folium来将这些内容绘制成图。**

## 背景

一直以来我就有个想法，就是将Shodan
API中的摄像头可视化为交互式的摄像头地图。这其中有部分的摄像头是开放式的，这意味着你不需要任何的黑客技术就能轻松的获取访问权限。此外，一些摄像头的所处位置也很有趣。如果你幸运的话，可能摄像头拍到的内容将会帮助你进行OSINT调查或照片定位。想象一下，你正好需要通过某张图片来寻找位置，而你发现开放式摄像头正好指向了这个位置或是附近的某处，我相信这应该会给你很大的帮助和提示。

![0_TZ_IZ3YCjhyyy8Zk.jpg](https://image.3001.net/images/20181116/1542330221_5bee176d8d7ef.jpg!small)

## ꓘamerka

依赖项安装：

    
    
    Shodan
    
    Geopy
    
    Foilum
    
    Colorama
    
    
    pip install -r requirements.txt

 **注：** 请修改第14行的 **API_KEY** 。

ꓘamerka脚本主要依赖于Shodan API，GeoPy和Folium库。

Shodan允许我们根据经纬度和指定半径来发现任何可能的设备。例如我们想查找摄像头命令如下：

    
    
    geo:37.235,-115.811111,5 device:webcam

Geopy则允许你根据地址或特定建筑进行搜索。另外，它还可以测量相机和初始目标之间的距离。

Folium是一个优秀的GIS（地理信息系统）库，它为我们提供了许多方便的选项，看起来也非常的酷。来自Shodan的结果将被传递给Folium，以创建具有指向每个网络摄像头的标记地图。标记有两种颜色
- 红色表示摄像头可能需要某种形式的身份验证，并且不会返回200
OK代码，而绿色表示已打开或显示一些登录面板。如果在一个地方有许多标记，则标记将被分组。如果你要查看摄像头的IP，型号和距离等信息只需点击相应的标记即可。

## 使用示例

    
    
    root@kali: python kamerka.py --address "White House"
    
    White House, 1600, Pennsylvania Avenue Northwest, Golden Triangle, Washington, D.C., 20500, USA
    Found 81 results
    IP: xxx.xxx.xxx.xxx
    Coordinates: 38.xxx,-77.xxx
    -----------------------------------    IP: xxx.xxx.xxx.xxx
    Coordinates: 38.xxx,-77.xxx
    -----------------------------------    IP: xxx.xxx.xxx.xxx
    Coordinates: 38.xxx,-77.xxx
    -----------------------------------    ...
    -----------------------------------    IP: xxx.xxx.xxx.xxx
    Coordinates: 38.xxx,-77.xxx
    -----------------------------------    Saving map as White House.html

## 政府大楼

一些重要的楼层或建筑，特别是与政府相关的建筑物，如市政厅，军事基地或训练营。这些地方的摄像头应该做好必要的保护，而不应该出现开放式的摄像头。我在网上找到了[一篇非常有趣的关于摄像头OSINT的文章](http://www.hisutton.com/OSINT_Webcams.html)，该作者正在追踪潜艇。由于摄像头配置错误，可能导致一些机密信息的意外泄漏。

你可以通过地址进行搜索：

    
    
    kamerka.py –address “White House” –radius 2

##
![1_gvDyn4r4e5LxPo146neDZQ.png](https://image.3001.net/images/20181116/1542330249_5bee17895bfdb.png!small)

## 监控 & 侦察

此外，这些摄像头还可帮助你监控社区或在红队评估之前用于侦察。当然，这也取决于你的运气，并不是所有摄像头都是可以公开访问的，且大多数摄像头都是在室内使用 -如商店，仓库等。

第二种方式是通过坐标进行搜索：

    
    
    kamerka.py –coordinates “” –dark

以下坐标来自最新的维基解密，显示了一个较为隐秘的亚马逊仓库附近的摄像头。

![1_qDOEOoI1OqwTQvTjOUct1Q.png](https://image.3001.net/images/20181116/1542330270_5bee179e4b008.png!small)

 **注：** 暗色主题可以通过“-dark”标志进行设置。如果你在渲染OpenStreetMap时出现问题，则应使用暗色主题。  

## 总结

作为新一代的信息技术，物联网的安全还未引起大多数人的关注。许多个人或组织始终将安装的摄像头保持开放状态，或长久的不更新。这些摄像头常常会被添加到僵尸网络中用于Ddos攻击，或是被用于非法监控和隐私窃取。你可以搜索世界范围内任何敏感位置是否有开放式的摄像头。在此也提醒大家，如果你不是设备的所有者，请不要进行任何非授权的测试行为，否则将可能面临法律的风险！

 ***参考来源：[medium](https://medium.com/@woj_ciech/%EA%93%98amerka-build-interactive-map-of-cameras-from-shodan-a0267849ec0a)
，FB小编secist编译，转载请注明来自FreeBuf.COM**

