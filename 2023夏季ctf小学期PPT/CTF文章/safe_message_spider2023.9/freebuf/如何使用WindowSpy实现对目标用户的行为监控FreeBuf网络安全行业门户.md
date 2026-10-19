![](https://image.3001.net/images/20230602/1685678064_647967f0736c4e80d0e37.png!small)

## 关于WindowSpy

WindowSpy是一个功能强大的Cobalt Strike
Beacon对象文件，可以帮助广大研究人员对目标用户的行为进行监控。该工具的主要目标是仅在某些目标上触发监视功能，例如浏览器登录页面、敏感文件、vpn登录等。目的是通过防止检测到重复使用监视功能（如屏幕截图）来提高用户监视期间的隐蔽性。

除此之外，该工具还能够大大节省红队研究人员在筛选用户监控数据时所要花费的时间。

## 工具运行机制

![](https://image.3001.net/images/20230602/1685678077_647967fdbe13586357105.png!small)

每次检测到Beacon之后，BOF都会在目标上自动运行。BOF附带了一个硬编码的字符串列表，这些字符串在窗口标题中很常见，例如登录、管理员、控制面板、vpn等。我们可以自定义此列表并重新编译。它枚举可见的窗口，并将标题与字符串列表进行比较，如果检测到其中任何一个，它将触发WindowSpy.cn中定义的名为spy()的本地aggressorscript函数。默认情况下，它会进行屏幕截图。我们可以根据需要自定义此功能，例如按键记录、WireTap、网络摄像头等。

spy()函数支持接收一个参数，即$1（触发该行为的Beacon ID）。

## 工具安装

首先，广大研究人员需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/CodeXTF2/WindowSpy.git

接下来，将项目中的WindowsSpy.cna脚本加载进Cobalt Strike即可。

### 源码构建

首先，在Visual Studio中打开WindowSpy.sln解决方案文件。

然后针对目标BOF（x64/x86）构建代码即可。

## 工具使用

加载完成之后，每当检测到Beacon时该工具都会自动运行，并相应地触发对应的操作。

## 项目地址

 **WindowSpy** ：【[ _GitHub传送门_](https://github.com/CodeXTF2/WindowSpy)】

