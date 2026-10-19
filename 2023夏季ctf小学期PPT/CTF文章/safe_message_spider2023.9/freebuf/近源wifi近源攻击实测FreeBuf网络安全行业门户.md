![image](https://image.3001.net/images/20211215/1639555494_61b9a1a6d7a7f011c8afb.jpg!small)  
作者:墨客@涂鸦智能安全实验室

## 0x01 前言

模拟一下wifi近源攻击的真实场景

## 0x02 工具介绍

### 菠萝派

WiFi Pineapple
是由国外无线安全审计公司Hak5开发并售卖的一款无线安全测试神器。有许多有趣的模块。比如可以抓取到目标正在浏览的网址、图片的DWall绵羊墙；用来制作钓鱼页面的Evil
Portal；用来记录键盘输入内容的HTTP Proxy等等。

### kali linux

## 0x03 攻击规划

1.近源进行wifi搜索并爆破wifi密码  
2.伪装内网登陆页面进行钓鱼  
3.取消验证攻击使受害者连接我们的恶意wifi  
4.dns攻击使正常访问指向我们的钓鱼页面

## 0x04 执行计划

### 1.wifi爆破

利用kali的airodump对wifi发起嗅探，开启无线网卡的监听模式  
`airmon-ng start wlan0`//按照自己的无线网卡名  
`airodump-ng wlan0mon`  
![image](https://image.3001.net/images/20221215/1671088204_639ac84c7f447bf528e39.png!small)  
进行握手包抓取并伪造  
`airodump-ng -c 8 --bssid 78:11:DC:03:F6:F6 -w wifipcap/moke
wlan0mon`c是信道值，mac地址为目标wifi的mac地址 w为写入的文件  
等到有人连接该AP时，就能抓到握手包  
![image](https://image.3001.net/images/20221215/1671093912_639ade980de9d44d5ad64.png!small)  
使用我们预先准备好的字典对口令进行爆破.若存在弱口令，爆破起来还是非常快的。这里取其中一个爆破成功的wifi作为例子  
`aircrack-ng -a2 -b 78:11:DC:03:F6:F6 -w 111.txt moke-01.cap`  
![image](https://image.3001.net/images/20221215/1671093942_639adeb6948bc28e883c2.png!small)  
这一步以后，我们就可以成功进入目标的办公网了，进入办公网发现目标存在统一登录页面

### 2.伪造钓鱼页面

现在可以拿出我们的Pineapple了，利用它可以起一个恶意AP，我们可以选择创建和破解AP同名的AP来欺骗，也可以选择创建一个无密码的诱导性AP进行钓鱼。在这里，我创建了一个xxx-VIP的无密码网络用来测试  
![image](https://image.3001.net/images/20211215/1639555764_61b9a2b4b1e374c5f50b4.jpg!small)

我们开启菠萝派的evil
portal模块，这个模块会给你创建一个demo页面，任何人连接我们的wifi时，都会弹出该认证页面，通过该页面，我们可以将用户输入的信息获取并存储。  
![image](https://image.3001.net/images/20211215/1639555670_61b9a256ebe09695982dc.png!small)  
然后我们自己可以修改、上传编写好的钓鱼网站页面，传递的参数等，成品是下面这样的。我们在这里传递了用户输入的用户名、密码、ip、mac、主机名。捕获传递的参数

![image](https://image.3001.net/images/20211215/1639555791_61b9a2cfc52d1a7d91184.jpg!small)  
下图为构建好的钓鱼页面，为吸引人取名为加速网络  
![image](https://image.3001.net/images/20211215/1639555810_61b9a2e2bb971cb5bfa68.jpg!small)![image](https://image.3001.net/images/20211215/1639555831_61b9a2f726d1bfeb81b1c.jpg!small)  
将传递的参数内容存储到本地

![image](https://image.3001.net/images/20211215/1639555866_61b9a31a8a95a73771f7b.png!small)  
现在我们已经做了一个伪造的登录页面，测试了一下。功能是ok的  
![image](https://image.3001.net/images/20211215/1639555906_61b9a34205d2190d9adc9.jpg!small)

### 3.DNS欺骗

下一步就是要做一下DNS欺骗，让用户访问某些站点时，指到我们的钓鱼网站页面，下图为访问其它网站时跳转到了我们的钓鱼页面。在hosts文件中我们加入一些域名指向我们大菠萝的ip，如下图所示  
`dnsspoof -i br-lan -f hosts`  
![image](https://image.3001.net/images/20211217/1639726426_61bc3d5ab8b9cb62525e5.jpg!small)

### 4.Deauth使正常用户重连wifi

取消验证洪水攻击，通常被简称为Deauth攻击，是无线网络拒绝服务攻击的一种形式，它旨在通过欺骗从AP到客户端单播地址的取消身份验证帧来将客户端转为未关联的/未认证的状态。我们可以使用大菠萝或者kali下的mdk3，对指定wifi频道发送取消验证，让目标wifi下线，这样就可以重新搜索认证了！不过这样会影响正常wifi的使用，影响较大。所以这里在家里进行演示。亲测可以让在连设备掉线  
![image](https://image.3001.net/images/20211215/1639555934_61b9a35e232f79c3d65d3.png!small)

### 0x05耐心等待

最后就是耐心等待了，如果有个别人安全意识不是很强，连上此类wifi输入密码后，就能获取到相应权限。

![image](https://image.3001.net/images/20211215/1639555950_61b9a36e0e1ce51d65c2c.jpg!small)

## 总结

近源往往是一个企业比较薄弱的部分，也是红队攻击重要的一环。禁止私搭wifi，提高员工安全意识，禁止使用弱口令等行为可以较大程度上提升企业安全性

