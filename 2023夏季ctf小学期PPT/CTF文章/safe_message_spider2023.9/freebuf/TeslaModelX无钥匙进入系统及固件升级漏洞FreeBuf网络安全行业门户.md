## 一、背景

建立蓝牙连接并不容易，Model X的蓝牙系统只有在更换电池时才会“唤醒”几秒钟。研究人员从特斯拉Model
X回收网站（eBay）上购买修改过的BCM，发现该BCM具备发送蓝牙唤醒信号的功能，可以作为一个可连接的蓝牙设备，在以该设备为原点、半径高达5M的范围内向四周推送唤醒信号。

下图是随便找的eBay中BCM的销售信息([图片来源](https://www.ebay.com/itm/143333216828))

![](https://image.3001.net/images/20220904/1662280920_631464d8832217345a2bf.png!small)

攻击者购买Tesla Model X的key fob，了解到算法是RSA以及具体算法，并分析出响应机制，生成伪造的配对密钥。

逆向特斯拉Model X钥匙，发现可以通过特斯拉Model
X钥匙的BLE接口对BLE芯片上的软件(BLE的固件)进行远程更新。这种升级机制缺少必要的安全机制(比如数字签名),无法防篡改以及身份验证等，因此攻击者可以通过无线方式破解密钥链，甚至完全控制它，进而获得有效的解锁信息，以便解锁汽车。

有了解锁汽车的功能，就可以连接到诊断接口，将修改过的钥匙链与汽车配对，从而拥有永久的访问权限，开走汽车。

## 二、基础知识

### 1\. PKES:Passive Keyless Entry and Start汽车无钥匙进入与启动

特斯拉Model X钥匙与车机使用蓝牙低功耗(BLE)连接，车主可以接近车辆或按下按钮来自动解锁汽车。

本次故事里的研究人员所在的团队曾经完全逆向了Tesla Model
S中使用的PKES系统，研究发现该系统使用的是过时的DST40专用加密算法，因此破解Tesla Model
S中的PKES系统很可能为本次攻击提供很多经验基础。

### 2\. 挑战-响应协议

协议原理分析图（原创）

![](https://image.3001.net/images/20220904/1662281016_631465382fdb4ffeb233d.png!small)

### 3\. key Fob:密钥卡

### 4\. VIN：Vehicle Identification Number，车辆识别码。

VIN码概述图（[图片来源](https://car.autohome.com.cn/baike/detail_9_35_1298.html)）

![](https://image.3001.net/images/20220904/1662281055_6314655f0b03c5e50dfe0.png!small)

一般常见的位置是在：1、车辆前挡风玻璃的右下角、2、车辆防火墙上、3、B柱（前后门直接的立柱）铭牌上。

B柱示意图(1)（图片来源：百度图片）

![](https://image.3001.net/images/20220904/1662281076_631465749eba56ab50b19.png!small)

B柱示意图(2)（图片来源：百度图片）

![](https://image.3001.net/images/20220904/1662281108_63146594451f6dfdbe3fc.png!small)

特斯拉X的识别码位于

  * 带有X标志的塑料盖下(机翼)——打开车门，轻轻拉起盖子，让它跳出夹子
  * 汽车玻璃上
  * 贴纸出现在左侧立柱上
  * 出现在电脑中央的桌面上
  * 出现在通过手机控制车辆的应用程序中

Tesla VIN Decoder（[图片来源](https://www.youtube.com/watch?v=YNegDzQalEg&t=4s)）

![](https://image.3001.net/images/20220904/1662281132_631465ac3e173697c12c1.png!small)

Tesla Module X 的VIN码示例图（[图片来源](https://phohen.com/post-detail/where-is-the-vin-in-tesla---vin-locationcom---find-vin/1161382307)）

![](https://image.3001.net/images/20220904/1662281159_631465c7cd9e5af545dc1.png!small)

### 5\. OBDII Adapter:OBD(On Board Diagnostics车载自动诊断系统)接口

Tesla X OBDII
Adapter示意图(1)（[图片来源](https://www.youtube.com/watch?v=FjJhABJshD4)）

![](https://image.3001.net/images/20220904/1662281198_631465eed75acc416d00a.png!small)

Tesla X OBDII
Adapter示意图(2)（[图片来源](https://www.youtube.com/watch?v=FjJhABJshD4)）

![](https://image.3001.net/images/20220904/1662281233_6314661153be8bafc5705.png!small)

BCM车内控制电子元件的连线示意图（[图片来源](https://intellias.com/body-control-module-bcm-in-automotive/)）

![](https://image.3001.net/images/20220904/1662281258_6314662a22853342cba1d.png!small)

### 6\. BCM：Body Control Module车身控制模块

BCM一般功能（[图片来源](https://intellias.com/body-control-module-bcm-in-automotive/)）

![](https://image.3001.net/images/20220904/1662281281_6314664188e8b38ca49f5.png!small)

### 7\. CAN协议：Controller Area Network控制器局域网络

多主竞争式总线结构，广播通信。

  * 通信缺乏加密和无访问控制机制
  * 通信缺乏认证及消息校验机制，不能对攻击者伪造、篡改的异常消息进行识别和预警

[图片来源](https://zhuanlan.zhihu.com/p/45382277)

![](https://image.3001.net/images/20220904/1662281307_6314665b1e9196e7d7381.png!small)

### 8\. CAN屏蔽地

### 8.1 隔离的目的

为了保证总线网络的通讯稳定性，通讯接口通常会做隔离，可以保护设备及人身安全避免高压危险、可以消除地电势差的影响、可以消除路影响、提高系统间的兼容性。

### 8.2 CAN屏蔽地的作用

用于隔离接口模块，隔离作用以及抵御电场的干扰。

## 三、设备（PoC）

是通过一个自制的设备实现的，该设备由廉价设备制成:一台树莓派电脑，带有CAN屏蔽低，一个改装过的钥匙链和一辆报废汽车上的ECU和一个LiPo电池。

设备（PoC）示意图（[图片来源](https://zingnews.vn/hacker-danh-cap-xe-hoi-trong-90-giay-chi-voi-mot-thiet-bi-bluetooth-post1156443.html)）

![](https://image.3001.net/images/20220904/1662281328_6314667011d9d6a93c7c8.png!small)

## 四、攻击过程

阅读说明：

  * 攻击者的BCM称为” **攻击者BCM** “
  * Tesla Model X汽车中的BCM称为” **车机BCM** “
  * 攻击者组装的设备中含有的key fob称为” **攻击者key fob** “
  * 车主的key fob称为” **攻击者key fob** “
  * ” **攻击主板** “组装了树莓派电脑（称” **攻击电脑** “）、CAN屏蔽地、 **攻击者key fob** 、 **攻击者BCM** 、LiPo电池
  *  **攻击系统** ：手机（充当显示器）+ **攻击主板**
  * 攻击者使用到的python文件称” **攻击代码** “
  * 攻击者逆向key fob时生成的RSA配对密钥称 **“恶意密钥”**
  *  **RSA1** 是 **车机BCM** 生成的RSA密钥对， **车机BCM** 自存 **RSA1私钥** ，对外分享 **RSA1公钥**
  *  **RSA2** 是 **攻击系统** 生成的RSA密钥对， **攻击系统** 自存 **RSA2私钥** ，对外分享 **RSA2公钥**
  *  **用户口令** 和 **用户配对口令** 是一对， **用户口令** 存储于 **攻击系统** ， **用户配对口令** 存储于 **车机系统**

 **第一阶段：蓝牙连接传输固件代码，固件更新，为下一阶段攻击者key fob伪装成车主key fob打开汽车车门做准备**

  1. 攻击者靠近车辆，肉眼获得VIN码
  2. 以VIN码作为参数， **攻击电脑** 执行代码，使得 **攻击BCM** 可以模拟 **车机BCM** 的行为发送蓝牙唤醒信号

  *  **车机BCM** 的行为是：作为可连接的BLE设备不断向外推送蓝牙唤醒信号

  3. 攻击者5m以内靠近车主， **车主key fob** 误以为 **攻击者BCM** 就是 **车机BCM** ， **攻击者BCM** 通过低功耗蓝牙成功连接 **车主key fob** ，并且获得连接有效信息APPGITHASH、BLGITHASH、LFVERSION、HARDWAREID（验证过程中会用到的信息）

  * 根据背景中介绍到：“逆向特斯拉Module X钥匙，发现可以通过特斯拉Module X钥匙的BLE接口对BLE芯片上的软件(BLE的固件)进行远程更新。“
  * APPGITHASH:key fob的固件版本信息
  * BLGITHASH：未知
  * LFVERSION：Lexus Future version(自我推理)
  * HARDWAREID:厂商定义的标识符

  4. 攻击者30m以内推送恶意固件给目标钥匙扣，升级固件成功，获得 **车主key fob** 控制权，重新连接 **车主key fob** ，获得一次性认证解锁指令（包括全解锁、打开左机翼、打开右机翼，打开后备箱，关闭所有的指令）

  * 一次性认证解锁指令的获得是一次性还是永久性，是需要执行代码获得还是连接自动获取与具体 **攻击代码** 有关，一次性是指用于认证解锁是一次性的。
  * BLE有最大支持距离和控制数据速率范围，此处的时间与距离取决于具体的传输速度与传输数据量
  *  **攻击者key fob** 并没有完全伪装成 **车主key fob** （即并没有完全实现车主key fob的功能），因为之后的攻击过程中需要使用 **攻击者BCM** 模拟安全元件

 **第二阶段：配对恶意密钥，使用恶意密钥开走汽车**

  1. 攻击者靠近车， **攻击主板** 上的 **攻击者key fob** 自动连接 **车机BCM**
  2. 使用刚刚获得的解锁指令，解锁车门、打开左机翼、打开右机翼、打开后备箱
  3. 进入车门， **攻击者BCM** 显示屏下方的OBDII接口连接车机系统
  4. 运行代码向系统发送命令，发送VIN码将 **攻击者BCM** 接入车机CAN总线（由于没有CAN协议的身份伪造数据发送，推理该车的CAN总线接入无身份认证），看到”成功连接汽车，当前已成功配对的密钥信息“的打印输出，程序继续发送命令试图使用 **恶意密钥（已生成的RSA配对密钥）** 进行密钥配对
  5. 车机BCM发出挑战，挑战是由AES算法生成的随机数和车机BCM的RSA1公钥。 **攻击者key fob** 缩短的RSA公钥

  * 根据挑战响应协议，此处的挑战为一个随机数，但是该随机数是由AES算法生成并且使用了RSA加密，保证了传输可靠性（具体是进行身份验证和保证数据完整性）

  6. 攻击者用RSA1私钥解密得到共享的AES密钥，进行一系列认证过程（如下）， **恶意密钥** 成功配对到车机系统。

 **【认证过程：**

 **①车机BCM** 生成 **明文随机数** ，使用 **AES密钥** 加密随机数和使之成为 **密文随机数** ，使用 **RSA1私钥** 加密
**AES密钥** 使之成为 **code1** （我把它自定义称为code）, **车机BCM** 发送 **密文随机数+code1+RSA1公钥** 给
**攻击系统** 。

 **②攻击系统** 使用 **RSA1公钥** 解密 **code1** 得到 **AES密钥** ，再使用 **AES密钥** 解密 **密文随机数**
得到 **明文随机数**

 **③攻击系统** 用 **MD5算法** 计算 **用户口令和随机数** 得到 **hash1** ，使用 **AES密钥** 加密 **hash1**
使之称为 **密文,** 攻击系统使用 **RSA2** 私钥加密 **AES密钥** 使之成为 **code2** ，攻击系统发送
**RSA2公钥+code2+密文** 给 **车机BCM**

④ **车机BCM** 使用 **RSA2公钥** 解密 **code2** 得到 **AES密钥** ，也可能不解，直接使用刚刚生成的 **AES密钥**
，因为是共享的； **车机BCM** 使用 **AES密钥** 解密 **code2** 得到 **hash1** 。 **车机BCM** 使用
**MD5算法** 计算 **本地的随机数和用户配对口令** 得到 **hash2**
。对比得到hash1=hash2(由于故事中认证成功，所以hash1=hash2)，配对成功。】

  * 过程分析中的传输的内容自定义可能性很高，切莫纠结

认证流程示意图（原创）

![](https://image.3001.net/images/20220904/1662281356_6314668c0f771bd14e9b3.png!small)

  7. 攻击者发送CAN总线命令企图开车(这些命令模拟了安全元件行为)， **车机BCM** 发出挑战， **攻击者key fob** 认证向 **车机BCM** 回复响应，认证成功，车辆解锁，开走汽车。

## 五、漏洞总结

该部件存在问题：

  1. 固件更新缺少防篡改防伪造的数字签名，因此攻击者可以随意刷新固件，获得对钥匙链的完全控制
  2. PKES被动无钥匙进入漏洞，具备PKES 系统的车辆，当车主的车钥匙靠近车辆时，车辆能检测和识别到射频信号，进而解锁车辆，进入车辆后，按下一键启动按钮即可启动开走车辆。

# 六、参考

  1. [Belgian security researchers from KU Leuven and imec demonstrate serious flaws in Tesla Model X keyless entry system](https://www.imec-int.com/en/press/belgian-security-researchers-ku-leuven-and-imec-demonstrate-serious-flaws-tesla-model-x)
  2. [Hacker đánh cắp xe hơi trong 90 giây chỉ với một thiết bị bluetooth](https://zingnews.vn/hacker-danh-cap-xe-hoi-trong-90-giay-chi-voi-mot-thiet-bi-bluetooth-post1156443.html)

