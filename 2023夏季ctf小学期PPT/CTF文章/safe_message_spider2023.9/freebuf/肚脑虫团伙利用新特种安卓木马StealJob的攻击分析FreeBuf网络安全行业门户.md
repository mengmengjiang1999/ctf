## 背景

 **肚脑虫(APT-C-35)，由奇安信高级威胁研究团队持续跟踪发现并命名，其主要针对巴基斯坦等南亚地区国家进行网络间谍活动的组织。**
**此APT组织主要针对政府机构等领域进行攻击，以窃取敏感信息为主要目的。该APT组织除了以携带Office漏洞或者恶意宏的鱼叉邮件进行恶意代码的传播之外，还格外擅长利用恶意安卓APK进行传播。**

近期，经监控，本高级威胁研究团队发现该组织对其恶意安卓APK框架进行了大规模升级，无论是实用性还是稳定性都增强了不少，由于本次使用的APK框架与以往所使用的样本差异性过大，因此我们通过使用其代码中出现频率较高的词汇Job，将该框架命名为StealJob。

以下为详细分析。

## 诱饵分析

本次发现的APK样本名为 “KashmirVoice”(克什米尔之声)的APP。

其中克什米尔指的是查谟-克什米尔地区简称，包括克什米尔谷和查谟平地。这本来是两个独立的邦国。查谟居民主要信奉印度教，克什米尔居民却基本上信奉伊斯兰教。1846年查谟首领从英国人手中买下了被占领的克什米尔。而克什米尔人口数倍于查谟。这就种下了后来争端的根源。

而克什米尔争端指的便是印度和巴基斯坦对查谟和克什米尔地区主权纷争而引发的一系列问题，两国为了这块土地打了不知多少年。

而就在近日，巴基斯坦情报部门称印度在2019年4月16日-20日会在此发动攻击，这也充分证明了两国之间的摩擦和矛盾加剧,或将开战。

![image.png](https://image.3001.net/images/20190417/1555480385_5cb6bf410cc72.png!small)

而克什米尔之声指的是一个网站，该网站用于宣传印度军队的暴力行为，疑似巴基斯坦建立。

![](https://ti.360.net/uploads/2019/04/10/78f4da9c58103f2eef2ab6695d58649d.png)

![](https://ti.360.net/uploads/2019/04/10/1cec30c71a2eadfe123fa5472ad0c036.png)

因此，该APP有很大概率是为了针对一些会上该网站进行浏览的巴基斯坦人所精心定做。

并且我们发现该样本上传地为印度：

![](https://ti.360.net/uploads/2019/04/10/c985973408dcc3ec133dd140c55d31ec.png)

通过包名进行初步分析，该样本疑似为测试样本，并且在将该样本和过去该组织的样本进行对比发现，样本存在很大差异性。

![](https://ti.360.net/uploads/2019/04/10/4ff2fb43303884333230af368474c72c.png)

结合上述因素，我们初步判断，该样本为攻击者为了针对会访问克什米尔之声网站的巴基斯坦人而订做的APP版本的诱饵攻击，并为了进行测试而上传至VT。

## 样本分析

样本名称通过仿冒为“KashmirVoice”(克什米尔之声),诱骗用户安装，因为是测试样本，其包名与图标均没有进行仿冒。

当样本运行以后，会进行多达20种远控操作，其中包含测试操作，其远控操作有：获取用户手机通讯录、用户手机短信、用户手机通话记录、用户地理位置、用户手机文件、用户手机已安装软件等并进行上传。

以下为样本流程图：

![](https://ti.360.net/uploads/2019/04/10/014a28296e278308b9c074bc2e0b71dc.png)

运行后，可看到样本安装图标以及运行界面：

![](https://ti.360.net/uploads/2019/04/10/21b53cd7679850ef7361fd47dae7f85b.png)

![](https://ti.360.net/uploads/2019/04/10/0f18bde0e3534fafab3dab304161f78a.png)

![](https://ti.360.net/uploads/2019/04/10/97cd481279c6c1d4ca6098bf670f41c5.png)

其中，该APP的权限申请如下图所示，大多为敏感权限：

![](https://ti.360.net/uploads/2019/04/10/cb6939741a1869347ef4d584fed66449.png)

下面开始通过代码进行分析：

 **1.程序通过仿冒应用，诱骗用户安装使用，运行后诱骗用户软件已卸载，实则隐藏自身图标，从而达到保护自身的目的：**

![](https://ti.360.net/uploads/2019/04/10/e0398a3e1224813bb3ec0a7c99c8d438.png)

 **2.程序通过读取本地数据库文件，从而获取远控指令，达到对用户手机的远控操作：**

![](https://ti.360.net/uploads/2019/04/10/0d19b5fdc60f5aa8f0ae75967c3d3191.png)

![](https://ti.360.net/uploads/2019/04/10/6ccf989593fb51a623a1d355872d0f18.png)

![](https://ti.360.net/uploads/2019/04/10/9953d3a78f7c5ff1abac9c38f4e2cda5.png)

本地数据库文件：

![](https://ti.360.net/uploads/2019/04/10/8cc4d45ba92e9e83afe68ae0a74367f6.png)

 **3.根据不同指令，执行相应的操作：**

控制指令 | 指令含义  
---|---  
live_recording_scheduling_job | 进行录音控制  
tag_network_info_job | 获取网络状态并上传  
tag_directory_trees_job | 获取手机文件目录并上传  
tag_live_recordings_job | 录音并上传录音文件  
tag_key_logs_job | 获取密钥日志并上传  
tag_user_profile_job | 获取通讯录并上传  
tag_location_job | 获取地理位置并上传  
tag_apps_info_job | 获取手机已安装应用并上传  
test_job | 测试  
tag_sms_job | 获取用户手机短信并上传  
tag_calls_logs_job | 获取用户手机通讯录并上传  
tag_control_info_retrieval_job | 检索控制信息  
tag_notifications_job | 获取通知并上传  
tag_location_sender_job | 获取位置并上传  
tag_files_sending_job | 上传文件  
polling_job | 对程序本身功能进行监控，并做出相应的操作  
tag_contacts_job | 获取手机IMEI并上传  
tag_call_recordings_job | 获取通话录音并上传  
tag_device_info_job | 获取手机固件信息并上传  
tag_key_exchange_job | 密钥交换  
  
程序会获取相应的用户手机信息，并保存在相应的.json文件中，然后将文件进行上传。

下发控制指令：

![](https://ti.360.net/uploads/2019/04/10/3a4debd4249d4ee93388103043eae4f4.png)

主要功能：

![](https://ti.360.net/uploads/2019/04/10/6db00beb43c71bcf51cf7cb5c119bf81.png)

远控操作具体代码：

    
    
    live_recording_scheduling_job

进行录音控制。

![](https://ti.360.net/uploads/2019/04/10/d15814145acd4b707dc6153bff11aac3.png)

指令：

    
    
    tag_network_info_job 

获取网络状态并上传。

![](https://ti.360.net/uploads/2019/04/10/1659d0e831f68b586d98b7d61e549b30.png)

指令：

    
    
    tag_directory_trees_job 

获取手机文件目录并上传。

![](https://ti.360.net/uploads/2019/04/10/505b2275291765591c3f1e42941a25bf.png)

指令：

    
    
    tag_live_recordings_job 

录音并上传录音文件。

![](https://ti.360.net/uploads/2019/04/10/698d1037a3e105743b3353e49a56bf88.png)

指令：

    
    
    tag_key_logs_job 

获取密钥日志并上传。

![](https://ti.360.net/uploads/2019/04/10/7a24ec93ea47894c038b776a8cc6e7ac.png)

指令：

    
    
    tag_user_profile_job 

获取通讯录并上传。

![](https://ti.360.net/uploads/2019/04/10/d5396c0a0d050b2c7c9735733b2535e4.png)

指令：

    
    
    tag_location_job 

获取地理位置并上传。

![](https://ti.360.net/uploads/2019/04/10/15f79d92922eaea164bfa3f070a581a2.png)

指令：

    
    
    tag_apps_info_job 

获取手机已安装应用并上传。

![](https://ti.360.net/uploads/2019/04/10/9bb8eb08ae98ee781a7062ca113c5ad2.png)

指令：

    
    
    test_job 

测试。

![](https://ti.360.net/uploads/2019/04/10/a781c4a70e5912d93fd0fb47ffdef8bc.png)

指令：

    
    
    tag_sms_job 

获取用户手机短信并上传。

![](https://ti.360.net/uploads/2019/04/10/5ab4e1bae9e16997cfe0a66b4b250acd.png)

指令：

    
    
    tag_calls_logs_job 

获取用户手机通讯录并上传。

![](https://ti.360.net/uploads/2019/04/10/1f1791ec5607dd123fb45c20401f8681.png)

指令：

    
    
    tag_control_info_retrieval_job 

检索控制信息。

![](https://ti.360.net/uploads/2019/04/10/d5668f417080c3551f7c2c70e9be4d02.png)

指令：

    
    
    tag_notifications_job 

获取通知并上传。

![](https://ti.360.net/uploads/2019/04/10/80cebbd52a18135747e35114ab718b84.png)

指令：

    
    
    tag_location_sender_job 

获取位置并上传。

![](https://ti.360.net/uploads/2019/04/10/de4bb3fd2739079a34a0ef7b60f901b6.png)

指令：

    
    
    tag_files_sending_job 

上传文件。

![](https://ti.360.net/uploads/2019/04/10/bb0cd1bc48cbb9d98943867df1df6f01.png)

指令：

    
    
    polling_job 

对程序本身功能进行监控，并做出相应的操作。

![](https://ti.360.net/uploads/2019/04/10/d47d6c5538121a1ee8e86f607cecddfb.png)

指令：

    
    
    tag_contacts_job 

获取手机IMEI并上传。

![](https://ti.360.net/uploads/2019/04/10/4d78234ee4707e9f1b48d8556a835b7c.png)

指令：

    
    
    tag_call_recordings_job 

获取通话录音并上传。

![](https://ti.360.net/uploads/2019/04/10/167b81f4856c5d6527b6293c93f1ce95.png)

指令：

    
    
    tag_device_info_job 

获取手机固件信息并上传。

![](https://ti.360.net/uploads/2019/04/10/5a1465065ad55c219e5cfa3a078eebe8.png)

指令：

    
    
    tag_key_exchange_job 

密钥交换。

![](https://ti.360.net/uploads/2019/04/10/766dc7184fd6144c1e8a41bde6169d40.png)

上传到服务器：[https://justin.drinkeatgood.space](https://justin.drinkeatgood.space/)。

![](https://ti.360.net/uploads/2019/04/10/3cb75374dadfa56111f37aa1eaf67fa5.png)

![](https://ti.360.net/uploads/2019/04/10/e75d084bda4c03e9015c1a9352b07ace.png)

![](https://ti.360.net/uploads/2019/04/10/6a09542476004908fff3bbaa7b3f15aa.png)

![](https://ti.360.net/uploads/2019/04/10/52b347c9c361264d3b5fcf0b2eea6726.png)

## 同源分析

经过关联分析，我们判断该APK框架大概率为Donot新的APK框架，由于，相比于2018年8月发现的Donot移动端程序，此次发现的程序代码结构已经大不一样，但其C&C依然保持了Donot的风格。

### 代码对比

 **旧版本：**

![](https://ti.360.net/uploads/2019/04/10/8d463d182debf8b26a5d605b83b10dfe.png)

![](https://ti.360.net/uploads/2019/04/10/b841fcc587142781df7c4aa134d7bf3f.png)

 **新版本：**

![](https://ti.360.net/uploads/2019/04/10/2eaa2fec1d7e9fb4f2035085d8fb253f.png)

![](https://ti.360.net/uploads/2019/04/10/426f2c94690dd305cb85a60579ab6f0a.png)

Donot旧版本与新版本都将窃取到的用户信息，保存在本地文件中再上传。

旧版本将获取到的信息保存在相应的.txt文件中：

![](https://ti.360.net/uploads/2019/04/10/932eb819a1e7e73615591d02852819da.png)

![](https://ti.360.net/uploads/2019/04/10/f12fd0ae729658442592b523a7e29ce7.png)

新版本将获取到的信息保存在相应的.json文件中：

![](https://ti.360.net/uploads/2019/04/10/a58af55ef4f65d986b6a21e0c9b42f1b.png)

![](https://ti.360.net/uploads/2019/04/10/0e714ab8091e8020a007928bd27b016f.png)

服务器地址延续了Donot的风格：justin.drinkeatgood.space

![](https://ti.360.net/uploads/2019/04/10/535b9750a082a88f6a6fde311c45f579.png)

![](https://ti.360.net/uploads/2019/04/10/c657491c96e81e4804d941a94a511d6d.png)

此次Donot还对小米、华为、魅族手机进行了判断，代码如下：

![](https://ti.360.net/uploads/2019/04/10/580acdee60be7e608cb5a38342dabd00.png)

而为何代码中要进行该判断：

![](https://ti.360.net/uploads/2019/04/10/a09de7121ca86a9bdeecd771d8b388b5.png)

在进行溯源分析过程中，我们还发现在2019年1月到2月之间，Donot组织发起过两起伪装成google更新应用程序的APP攻击，如下所示：

    
    
    d3f53bcf02ede4adda304fc7f03a2000
    
    4aea3ec301b3c0e6d813795ca7e191bb

![](https://ti.360.net/uploads/2019/04/10/e7a78ae4a26c02630182e38074709cc1.png)

并且，有趣的是，这两个样本除了功能和StealJob不一致之外，在类命名方面延续了以往的风格。

![](https://ti.360.net/uploads/2019/04/10/9dc8f2acd660c20551c71dc8419069ce.png)

![](https://ti.360.net/uploads/2019/04/10/c5071735927b520c1df9686c2d1db36a.png)

其中，值得注意的是，两个包名都存在拼写错误，其将“google”拼成了“gooqle”。

![](https://ti.360.net/uploads/2019/04/10/0cffcd8f5e0089928055d63c8829236e.png)

![](https://ti.360.net/uploads/2019/04/10/ea0b9ea2d6980680c544ef389bbf1298.png)

而两个样本的签名时间上看，可以看出具有一致性，很有可能该组织会在制定的时间发起攻击。

![](https://ti.360.net/uploads/2019/04/10/e5f36c5a78f681730afb3f3d68e202ec.png)

![](https://ti.360.net/uploads/2019/04/10/ac64034baed58364986691400d29c68c.png)

## 总结

鉴于该样本为donot组织的最新测试样本，在野并未发现真实攻击案例，因此，奇安信高级威胁研究团队在此警示用户，不要点击安装来源不明的安卓应用程序，以防造成个人财产损失。

## IOC

CDF10316664D181749A8BA90A3C07454  
---  
d3f53bcf02ede4adda304fc7f03a2000  
bf06a2b21b1178cff1e9e4bf0e6fa966  
4aea3ec301b3c0e6d813795ca7e191bb  
98a8f1a4ec5893f0b8acbca683ca4a7d  
justin.drinkeatgood.space  
digest.drinkeatgood.space  
drinkeatgood.space  
help.domainoutlet.site  
ground.domainoutlet.site  
guild.domainoutlet.site  
guide.domainoutlet.site  
jasper.drivethrough.top  
qwe.drivethrough.top  
alter.drivethrough.top  
car.drivethrough.top  
param.drivethrough.top  
bike.drivethrough.top  
genwar.drivethrough.top  
139.180.135.59:4233  
hxxps://justin.drinkeatgood.space/api/V1/public/  
  
## 参考信息

[1]<https://ti.360.net/blog/articles/donot-group-is-targeting-pakistani-businessman-working-in-china/>

[2]<https://ti.360.net/blog/articles/latest-activity-of-apt-c-35/>

[3]<https://asert.arbornetworks.com/donot-team-leverages-new-modular-malware-framework-south-asia/>

 ***本文作者：360天眼实验室，转载请注明来自FreeBuf.COM**

