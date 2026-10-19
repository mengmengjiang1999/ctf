**随着绝地求生、荒野行动等游戏大火，不少玩家会下载各种加速器用来加速游戏，而这些利用玩家求胜心理传播的加速器等外挂，却很快成了木马活跃的温床。近期，360安全中心发现一款借助“荒野行动”外挂扩散的驱动级木马十分活跃，传播量迄今已超10万次。**

该加速器运行后界面显示正常，但是后台会静默注入桌面进程，下载各种恶意木马运行。木马会通过修改驱动结构体隐藏自身文件及驱动对象，创建进程回调对浏览器实施监控，借机劫持并篡改玩家所有浏览器的主页。值得注意的是，该木马的查杀难度极高，能够关机回写自身服务项，确保自身在开机最初运行，并做多重注册表保护。

下面是对该加速器恶意行为详细分析。

## 安装改首页驱动部分

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221203163451.png!small)  
图1

而后在线程函数中检测恶意驱动设备是否存在:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221203291218.png!small)  
图2

打开查找设备名:

![Clipboard
Image.png](https://image.3001.net/images/20180327/1522120337400.png!small)  
图3

读取驱动下载配置:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221203459305.png!small)  
图4

然后解密配置, 检测改主页驱动安装云标记是否打开。

打开是1，并且根据操作系统x86 x64分别使用不同地址。

下载安装驱动:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221203546723.png!small)  
图5

调用 URLDownloadToFileW 下载驱动文件:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221203628074.png!small)  
图6

启用该驱动:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221203691354.png!small)  
图7

## 改主页驱动

### 2.1驱动入口函数

判断是否支持的系统:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221203771357.png!small)  
图8

是否已经加载上:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221203853596.png!small)  
图9

判断是否为第一次随机名加载:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221203936280.png!small)  
图10

如果是随机名加载,则重新加载驱动并且将自身设置为System Reserved组:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221204015494.png!small)  
图11

调用ZwLoadDriver重新加载该驱动:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221204082788.png!small)  
图12

重新加载自身后创建符号链接:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221204169266.png!small)  
图13

而后注册关机回调，初始化浏览器进程数组，进程回调(用来判断浏览器改主页)。

![Clipboard
Image.png](https://image.3001.net/images/20180327/1522120423435.png!small)  
图14

通过进程名称获取进程Pid:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221204313301.png!small)  
图15

而后注册DriverReinitializationRoutine。

### 2.2 初始化保护函数

首先锁定自身文件，防止被杀软读取，保存驱动全路径并且隐藏自身驱动对象:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221204401404.png!small)  
图16

查询系统所有模块:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221204482443.png!small)  
图17

挑选其中的系统模块然后复制其中驱动文件名和驱动文件路径:

![Clipboard
Image.png](https://image.3001.net/images/20180327/1522120456201.png!small)  
图18

之后系统就会多出两个一模一样的驱动文件。

然后注册文件MiniFilter注册表回调保护自身注册表和禁止杀软模块加载:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221204649122.png!small)  
图19

注册文件过滤防止模块加载:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221204703556.png!small)  
图20

注册注册表回调保护服务项目:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221204794792.png!small)  
图21

然后创建系统线程等待桌面进程启动后保护自身注册表项目:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221204873484.png!small)  
图22

等待桌面进程启动后保护注册表项目:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221204974675.png!small)  
图23

注册表回调发现一旦设置或者删除自身注册表项目就返回拒绝并且通过开关控制。

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221205055039.png!small)  
图24

文件过滤中:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221205151240.png!small)  
图 25

判断是否为浏览器进程:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221205313471.png!small)  
图26

如果是这些进程中且为以下模块则返回STATUS_NO_SUCH_FILE。

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221205397948.png!small)  
图27

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221205494270.png!small)  
图28

### 2.3 修改浏览器主页

主要是在进程回调中实。判断是否为浏览器进程,然后通过修改命令行方式强行跳转:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221205578320.png!small)  
图29

判断浏览器进程:

![Clipboard
Image.png](https://image.3001.net/images/20180328/15222056008039.png!small)  

图30

通过遍历浏览器进程名数组实现:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221205724725.png!small)  
图31

浏览器进程列表为:

  
![Clipboard
Image.png](https://image.3001.net/images/20180328/15222056105858.png!small)  
图32  

获取进程命令行:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221205914332.png!small)  
图33

通过获取PEB中相关结构实现:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221205984969.png!small)  
图34

获取进程命令行:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221206059853.png!small)  
图35  

而后 SafeChangeProcessCommandLine 修改浏览器进程命令行:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221206126520.png!small)  
图36

判断哪些窗口名或者是进程命令行跳过然后拼接命令行参数:

![Clipboard
Image.png](https://image.3001.net/images/20180327/1522120620534.png!small)  
图37  

实现浏览器主页修改:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221206278396.png!small)  
图38

修改命令行函数:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221206344901.png!small)  
图39

### 2.4 关机回调

会清理调所有其他的注册表回调，并且重新回写自身服务项目。

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221206426742.png!small)  
图40

先摘除自身保护:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221206493846.png!small)  
图41

而后根据系统硬编码摘除其他的注册表回调便于将自身写入:

![Clipboard
Image.png](https://image.3001.net/images/20180327/1522120656693.png!small)  
图42

然后重新写入注册表项目:

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221206644082.png!small)  
图43

## 中毒现象和查杀

主页被修改

![Clipboard
Image.png](https://image.3001.net/images/20180327/1522120675532.png!small)  
图44

多了两个一样的模块:

![Clipboard
Image.png](https://image.3001.net/images/20180327/1522120682839.png!small)  
图45

近期在上述站点下载过软件的玩家，都有可能被该驱动木马感。建议玩家一旦发现浏览器主页被反复篡改现象时，尽快使用安全软件对设备进行扫描查杀。

360安全卫士于国内率先实现对该顽固驱动木马的查杀清理，在此也提醒玩家尽量不要使用外挂，更不要听信外挂诱惑关闭杀软，给恶意木马可趁之机。

![Clipboard
Image.png](https://image.3001.net/images/20180327/15221206906882.png!small)  
图46

 ***本文作者：360安全卫士，转载请注明来自FreeBuf.COM**

