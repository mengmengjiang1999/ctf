**近期安天移动安全和猎豹移动联合捕获到病毒gpSystem，该病毒植入在应用程序private，程序运行后便隐藏图标，进行下载提权相关文件、联网获取数据模拟点击注册google账号、上传用户账号、固件等信息等一系列恶意行为，造成用户资费损耗和隐私泄露风险。目前安天移动安全联合猎豹移动已实现对该病毒的检测查杀，建议用户安装猎豹安全大师等集成安天移动安全反病毒引擎的安全产品，定期进行病毒检测，一旦被感染需及时卸载恶意应用。以下是针对该病毒的详细分析。**

## 一、样本基本信息

![0.png](https://image.3001.net/images/20180718/15318805251687.png!small)

该恶意应用被下载安装后将隐藏图标，下载提权相关文件、私自提权，解密静默安装恶意程序到系统目录，修改多个系统api调用的返回值，联网获取数据模拟点击注册google账号，还会私自下载恶意子包，上传用户账号、固件等信息。

## 二、恶意信息流程图

![02_副本.png](https://image.3001.net/images/20180718/15318805476785.png!small)

## 三、动态分析

运行后多次申请root权限：  

![03.jpg](https://image.3001.net/images/20180718/15318805795932.jpg!small)

## 四、样本分析

程序运行，隐藏图标：  
![image006.png](https://image.3001.net/images/20180718/15318806228065.png!small)

获取root权限：  

![image007.png](https://image.3001.net/images/20180718/15318806933158.png!small)

![image008.png](https://image.3001.net/images/20180718/15318807194957.png!small)

联网下载提权模块：

![image009.png](https://image.3001.net/images/20180718/15318807615558.png!small)

执行提权方案：

![image010.png](https://image.3001.net/images/20180718/15318807669541.png!small)提权后安装apk：  

![image016.png](https://image.3001.net/images/20180718/1531881112714.png!small)解密子包，启动两个子包服务：![image012.png](https://image.3001.net/images/20180718/15318807767291.png!small)![image013.png](https://image.3001.net/images/20180718/15318807794764.png!small)

拷贝到系统目录和sdcard：

![image014.png](https://image.3001.net/images/20180718/15318807829070.png!small)

子包分析：

![image015.png](https://image.3001.net/images/20180718/15318807868198.png!small)

androidntv（gpSystem）： MD5：95EEA5CD39A722507D4781AB3067E5F8
dmrdroid（com.android.dmr）： MD5：62D26656061AB328A079FB6FB4E84460 gpSystem：

启动SuService：

![image016.png](https://image.3001.net/images/20180718/15318811586559.png!small)

hook多个系统函数：

![image017.png](https://image.3001.net/images/20180718/15318813096621.png!small)

判断是否能够注册google账号：

![image018.png](https://image.3001.net/images/20180718/15318813177094.png!small)

判断辅助功能是否启动，用来模拟点击注册google账号：

![image019.png](https://image.3001.net/images/20180718/15318813225733.png!small)

开始hook：

![image020.png](https://image.3001.net/images/20180718/15318813274757.png!small)

hook多个系统api，修改返回值，以防止影响自动注册：

![image021.png](https://image.3001.net/images/20180718/15318813312994.png!small)

hook之后启动注册界面：

![image022.png](https://image.3001.net/images/20180718/1531881335996.png!small)

会先结束其他影响注册的服务，然后am命令启动注册界面：

![image023.png](https://image.3001.net/images/20180718/15318813382183.png!small)

界面启动之后，RegisterAccessbilityService通过监听包名“com.google.android.gsf.login”触发注册界面启动事件：

![image024.png](https://image.3001.net/images/20180718/15318813413812.png!small)

判断sdk版本，使用不同的方式注册google账号：

![image025.png](https://image.3001.net/images/20180718/15318813449955.png!small)

通过辅助功能获取界面上所有控件信息，之后联网获得注册数据：

![image026.png](https://image.3001.net/images/20180718/15318813473088.png!small)

判断是否是测试版本，测试版本则注册测试账号，不是测试版本则联网获取注册数据：

![image027.png](https://image.3001.net/images/20180718/15318813517927.png!small)

注册google账号：

![image028.png](https://image.3001.net/images/20180718/15318813541563.png!small)

通过辅助功能模拟点击：

![image029.png](https://image.3001.net/images/20180718/15318813582955.png!small)

com.android.dmr：

MMLogManagerService服务中，联网获取下载配置信息：  

![image030.png](https://image.3001.net/images/20180718/15318816799188.png!small)

![image031.png](https://image.3001.net/images/20180718/15318816853572.png!small)

下载并加载子包：

![image032.png](https://image.3001.net/images/20180718/15318816904931.png!small)

下载子包：<http://www.supportdatainput.top:8080/modules/abroad.zip>

![image033.png](https://image.3001.net/images/20180718/15318816941830.png!small)

加载子包：

![image034.png](https://image.3001.net/images/20180718/1531881698722.png!small)

abroad.zip分析

拷贝用户账号等数据文件到指定目录，解析数据并上传,上传cc为：<http://game.zxcvbnmasdfghjkl.xyz:8080/game/api>  

![image035.png](https://image.3001.net/images/20180718/15318817049084.png!small)

获取上传数据：

![image036.png](https://image.3001.net/images/20180718/15318817071802.png!small)

拷贝用户账号信息等文件到指定目录：

![image037.png](https://image.3001.net/images/20180718/15318817102360.png!small)

从/data/system/users/0、/data/data/com.google.android.gms、/data/data/com.google.android.gsf、/data/data/com.android.vending这4个目录拷贝数据库或配置文件，主要从这些文件获取用户账号、authtoken（授权令牌）、gcm、固件、GooglePlay等相关信息：

![image038.png](https://image.3001.net/images/20180718/1531881987422.png!small)

解析文件格式后，将数据上传服务器：

![image039.png](https://image.3001.net/images/20180718/15318817191977.png!small)

收集用户账号信息等数据可能用于配合gpSystem注册google账号相关。

相关CC：  

![40.png](https://image.3001.net/images/20180718/15318819932276.png!small)

## 五、总结

该病毒首先通过联网获取root方案，下载并执行提权模块，随后释放两个恶意程序，拷贝到系统目录以防被卸载。恶意程序通过辅助功能模拟点击注册google账号，并且通过修改系统函数返回值（忽略按键、锁屏无效等），防止其影响注册流程，以提高注册成功率。同时还会下载恶意代码，收集用户账号、authtoken（授权令牌）、固件、gcm、GooglePlay等信息，可能用于配合自动注册相关。
近年来，各种黑色产业链逐步形成，黑产的攻击手段也越来越专业化，会利用一系列手段保护自己，对此安全厂商应该持续关注并提升对抗能力，为移动安全保驾护航。

 ***本文作者：AVLTeam，转载请注明来自FreeBuf.COM**

