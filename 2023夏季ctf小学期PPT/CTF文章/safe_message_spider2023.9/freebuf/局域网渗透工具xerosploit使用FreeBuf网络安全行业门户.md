## 概念

Xerosploit是局域网一款渗透测试工具包，它的主要功能就是执行中间人攻击。它本身自带有多种功能不同的模块，这些模块具有多种功能，除了中间人攻击之外，Xerosploit还可以进行端口过滤以及拒绝服务攻击等。

## kali下载

git clone https://github.com/LionSec/xerosploi

![1574425083154-4ccadcf4-72ea-4f4f-b1d6-029a999e62cb.png](https://image.3001.net/images/20220113/1642042374_61df9406dca9f4a3d8740.png!small)

## kali安装

cd xerosploit && sudo python install.py &&进入xerosploit中在执行“./install.py”

![1574425098009-878b8348-3f93-469d-81dd-d4d7e02dd420.png](https://image.3001.net/images/20220113/1642042375_61df9407d6d5781dfbf9d.png!small)

## 启动软件

sudo
xerosploi![1574425450353-01eb7bd2-5b11-40db-91df-016f0298fb1e.png](https://image.3001.net/images/20220113/1642042376_61df94086ffee406e22ba.png!small)

## 查看帮助（help）

![1574425495172-e0ca760e-ec90-418d-bf04-cedb9f055f03.png](https://image.3001.net/images/20220113/1642042377_61df9409ca74024efea8d.png!small)

## 扫描（scan）这里出来好多ip

这里是有有两种办法

第一直接写对方ip那就是攻击一个ip

第二如果写all那就全部机子

如果写192.168.9.1,192.168.2 这样写就攻击两个机子

![1574425734182-9a4adb09-51b7-47a6-a67c-8f4b70440485.png](https://image.3001.net/images/20220113/1642042378_61df940aba8894416707b.png!small)

### 这里地址是靶机 的地址

![1574425863938-a8b3dbeb-db31-41b2-9e2a-2d3c3d1a6420.png](https://image.3001.net/images/20220113/1642042380_61df940c1679c39f14b4b.png!small)

### 输入帮助信息

![1574425894760-633e0d18-b33e-42c5-a26f-1a64ed614da3.png](https://image.3001.net/images/20220113/1642042381_61df940d056ab76f9c88c.png!small)

翻译一下  
pscan：端口扫描  
dos：对目标进行dos攻击  
ping：对目标进行ping是否存活  
injecthtml：将html注入到目标访问的网站中  
injectjs：将javascript注入到目标访问的网站中  
rdownload：替换目标下载的文件  
sniff：嗅探目标的流量信息  
dspoof：将所有http流量重定向到特定ip  
yplay：在目标的浏览器中后台播放视频（还得fq）  
replace：替换目标访问网站的所有图片  
driftnet：查看目标访问网站的所有图片  
move：让目标访问网站变得抖动  
deface：将目标访问网站的所有页面替换成自己定义的html代码

## 我们这里使用pscan这个模块（端口扫描）

然后写back命令（返回）

![1574425938732-5197b6ae-7c1e-41bb-bb75-34675393bc8b.png](https://image.3001.net/images/20220113/1642042382_61df940e4a5faa6274d90.png!small)

剩下的命令就自己探索把..

​

