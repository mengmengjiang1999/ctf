![](https://image.3001.net/images/20200817/1597627167.jpg!small)

第一次接触tempestsdr是17年底的时候，当时大二，看到unicorn
team的微博上，雪碧师傅使用hackrf外加定向天线嗅探显示器的电磁泄露，真的是超酷，就一直想复现出来。从17年底复现到现在，由于各种各样的坑，今天终于复现出来了。

PS：本文仅用于技术讨论与分析，严禁用于任何非法用途，违者后果自负。

## 需下载的文件

    
    
    已经编译好的tempstsdr工具:<https://github.com/eried/Research/tree/master/HackRF/TempestSDR>  
    EXTIO DLLS: <https://drive.google.com/file/d/1cn3fuZyXTGDv9u2M-Xrilee1BWcQ1c5E/view>  
    sdrsharp下载: <https://www.rtl-sdr.com/tag/sdrsharp/>  
    zadig下载：<https://zadig.akeo.ie/>

## 硬件

    
    
    hackrf（这里也可以是RTL-SDR、或者AIRSPY等）、Lenovo台式机自带显示器

## 环境配置

    
    
    windwos10（这里用zadig安装好hackrf one的驱动，保证可以使用sdrsharp调用hackrf one 收听广播）

## 确定所要监听的显示器的参数

![](https://image.3001.net/images/20200817/1597627178.png!small)![1539192-20200816164957006-1930703974.png](https://image.3001.net/images/20200817/1597627545.png!small)

可以看出分辨率是1600*900，屏幕刷新率为60Hz

## 使用sdrshrap识别出显示器的辐射频率

在测试的电脑上打开tempest Test for
Windows.exe播放对应的测试视频后，这里我将频率调到409.987.500Mhz后可以收听到对应的“”致爱丽丝“的电子广播声，说明我得Lenovo显示器的辐射频率为409.987.500Mhz。（这里大家使用sdrshrp的使用应注意调整sdrsharp的增益等参数,使用NFW收听）

![1539192-20200816170235744-1096794300.png](https://image.3001.net/images/20200817/1597627546.png!small)

![](https://image.3001.net/images/20200817/1597627179.png!small)

###  **视频演示：**

（噪音警告）

# 使用编译好的tempestsdr嗅探屏幕信息

\TempestSDR_win32_openjdk-14.0.1\TempestSdr.exe

首先选择对应的硬件,这里还是建议将RX LNA和RX VGA两个参数调高一点。

![](https://image.3001.net/images/20200817/1597627180.png!small)

![](https://image.3001.net/images/20200817/1597627181.png!small)

开始嗅探显示器内容

![](https://image.3001.net/images/20200817/1597627369.jpg!small)

# 参考：

    
    
    [https://www.bilibili.com/video/BV1Vt4y1X7rF?from=search&seid=13257151988388533747](https://www.bilibili.com/video/BV1Vt4y1X7rF?from=search&seid=13257151988388533747)  
    <https://github.com/eried/Research/tree/master/HackRF/TempestSDR>  
    [https://unicorn.360.com/hackcube/forum.php?mod=viewthread&tid=51](https://unicorn.360.com/hackcube/forum.php?mod=viewthread&tid=51)

