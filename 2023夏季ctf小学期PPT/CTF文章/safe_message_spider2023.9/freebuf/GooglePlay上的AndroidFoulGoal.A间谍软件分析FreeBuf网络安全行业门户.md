**世界杯的余热还未散去，但近期安全专家却发现了一个针对世界杯足球球迷的间谍软件活动。**

![pngGoogle
Play上的AndroidFoulGoal.A间谍软件分析](https://image.3001.net/images/20180728/1532740332_5b5bc2ec5d363.png!small)

## Golden Cup

这款恶意软件名叫“Golden Cup”，主要在Google
Play应用商店中进行传播。实际上，利用当前热门事件来作为社工技术的内容核心其实并不算新颖，而Golden
Cup这一次利用的是“世界杯”这个全球范围内的足球盛典。

表面上，Golden Cup可以观看足球视频（包括直播）和球队比分以及积分情况，但实际上，当目标设备成功安装好Golden
Cup之后，它便会在目标设备上安装间谍软件。McAfee Mobile
Security将这一威胁标记为Android/FoulGoal.A，不过广大用户无须担心，Google已经将这款恶意应用程序从Google
Play下架了。

![Google
Play上的AndroidFoulGoal.A间谍软件分析](https://image.3001.net/images/20180728/1532740340_5b5bc2f4bedd2.png!small)

值得一提的是，Golden Cup给用户呈现出的赛事数据来源于合法的Web服务，但是它在后台却会将用户的数据信息发送给另一台由攻击者控制的恶意服务器。

## 数据捕捉

GoldenCup能够从目标用户的设备中收集到下列加密数据：

> 1\. 手机号码；
>
> 2\. 已安装的数据包；
>
> 3\. 设备型号、制造商和序列号；
>
> 4\. 可用的内部存储空间；
>
> 5\. 设备ID；
>
> 6\. Android版本信息；
>
> 7\. IMEI和IMSI；

由于这款间谍软件会从远程资源加载dex文件，因此研究人员认为这只是它收集信息的第一个阶段。App会跟其命令控制服务器进行连接，并尝试下载、解压和解密第二阶段的操作命令。

Android/FoulGoal.A能够检测屏幕是否处于亮起状态，并将相关信息记录在其内部文件scrn.txt之中，用字符串“on”或“off”来标记用户是否在查看自己的手机屏幕：

![Google
Play上的AndroidFoulGoal.A间谍软件分析](https://image.3001.net/images/20180728/1532740357_5b5bc3058b6a2.png!small)

在数据传输的过程中，受感染设备与远程命令控制服务器（攻击者控制的）的通信信道采用的是消息队列遥测传输协议（MQTT）。

### 数据解密

在将用户数据发送给恶意服务器之前，恶意软件会采用AES算法对用户数据进行加密。在恶意软件的代码中，Cryptor类负责对数据进行加密和解密操作。其中，doCrypto函数是一个常规函数，第一个参数“1”代表加密，“2”代表解密模式：

![Google
Play上的AndroidFoulGoal.A间谍软件分析](https://image.3001.net/images/20180728/1532740371_5b5bc3134cf81.png!small)

加密过程中，加密密钥是通过SecureRandom函数动态生成的，该函数会在设备上生成一个唯一值来对收集到的数据进行混淆处理。addKey函数负责将加密密钥嵌入至加密数据中，接下来，带有密钥的数据将会被上传到恶意服务器中：

![Google
Play上的AndroidFoulGoal.A间谍软件分析](https://image.3001.net/images/20180728/1532740378_5b5bc31abe892.png!small)

安全研究专家认为，这款恶意软件的开发者之所以要使用这种AES加密技术来进行数据传输，主要是想躲避Google
Bouncer以及其他网络安全产品的检测。数据显示，目前至少有三百台设备感染了Golden
Cup恶意软件，感染高峰期在2018年6月8号至12号之间，也就是俄罗斯世界杯开赛之前。

## 第二阶段

攻击的第二阶段利用了一个加密的dex文件，该文件带有.data后缀，由第一阶段的恶意软件下载并动态加载。该文件会使用相同的机制进行提取，并用来向恶意服务器上传加密后的用户文件。

解密密钥的存储位置可以通过识别第一阶段恶意软件中的内容大小以及固定数值来查找。解密之后，我们可以看到out.dex文件为压缩格式，dex文件带有的间谍软件功能能够从受感染设备中窃取短信信息、通讯录、多媒体文件和设备地理位置信息。

![Google
Play上的AndroidFoulGoal.A间谍软件分析](https://image.3001.net/images/20180728/1532740399_5b5bc32f4e621.png!small)

第二阶段所使用的命令控制服务器跟第一阶段所使用的并不是同一台，但是采用的加密方法和服务器目录结构却是相同的。在分析过程中，研究人员还在恶意服务器中发现了一名用户的GPS定位信息以及录音文件（.3gp）。

## 恶意软件变种

需要注意的是，研究人员还发现了两个Golden Cup变种，而这两个拌种版本都是由同一开发者上传到Google
Play商店中的。虽然Google现在已经将这三款App下架了，但还是已经有大量用户感染了Golden
Cup，因为通过对其恶意服务器的分析来看，这些App目前仍活跃在某些用户的设备上。

研究数据表明，虽然全球范围内都有用户下载了这款恶意软件，但主要的下载量还是中东地区的用户贡献的，因此受此活动影响最大的应该是中东地区的朋友们。

目前，McAfee Mobile Security已经将该威胁标记为了Android/FoulGoal.A，并且能够识别该恶意软件威胁的所有变种版本。

 *** 参考来源：[securingtomorrow](https://securingtomorrow.mcafee.com/mcafee-labs/google-play-users-risk-a-yellow-card-with-android-foulgoal-a/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

