## 背景

**近日，奇安信病毒响应中心在日常移动样本监控过程中发现一款伪装名为“CBRC”的APP，CBRC应该是中国银监会或银监会的英文简称（ChinaBanking
Regulatory
Commission），此类仿冒监管机构的APP常用于电信诈骗行业获取受害人的银行账户密码信息[1]；经过分析发现此类伪装的APP还具有一双“千里眼”，时刻监控着受害者的一举一动并能及时作出反侦查行为，提前一步脱离犯罪现场；同时也设置了APP运行超过7天时间后，则关闭服务（即没法进入到“资产清查”界面，给取证办案人员带来困扰）。**

## 诱饵分析

诱饵APP图标：

![](https://image.3001.net/images/20191223/1577090249_5e007cc9de4d9.png!small)

样本运行截图：

![](https://image.3001.net/images/20191223/1577090246_5e007cc6303d2.png!small)

申请的权限：

![](https://image.3001.net/images/20191223/1577090319_5e007d0f952c3.png!small)

通过搜索CBRC资产清查的事情发现一例真实电信诈骗案例[1]，电信诈骗分子实施转账时间为2019年6月7日至2019年6月9日；电信诈骗分子通过前期的资料收集和电话剧本准备，给吴女士进行了一层套一层的洗脑行为，让其深信不疑的相信自己已涉案，最后通过伪装的“CBRC”安卓程序获取受害者的银行账户密码信息，同时诈骗人员继续通过精心准备的案件剧本来套住受害者，不让其登录各类银行APP，空出的时间则进行资产转移。

电信诈骗分子app的聊天记录：

![](https://image.3001.net/images/20191223/1577090327_5e007d17c45aa.png!small)

其相关的报案回执单：

![](https://image.3001.net/images/20191223/1577090336_5e007d205a949.png!small)

受害人相关信息：

![](https://image.3001.net/images/20191223/1577090399_5e007d5fe779c.png!small)

## 样本分析

### 样本信息

文件名称 | 06853346D7D22C6188AD4C2CB40DAA10.apk  
---|---  
软件名称 | CBRC  
软件包名 | com.android.hotel.jingle  
MD5 | 06853346D7D22C6188AD4C2CB40DAA10  
安装图标 |
![](https://image.3001.net/images/20191223/1577090411_5e007d6bb5623.png!small)  
  
### 样本行为描述

样本运行后，首先会检测是否是首次运行，同时检测其运行时间是否大于7天，当受害者运行此样本的时间大于7天时则停止所有的操作(可以误导取证者，此小马已失活)。通过向服务器上传手机sim卡序列号进行注册后，则会返回远控指令参数值信息同时实现远控操作。其主要的远程操作有：电话转接、短信转发、设置静音模式、备份通讯录和短信、更新GPS信息、删除短信等操作。

### 主要恶意功能

1、样本运行后，如果是首次运行app，则会直接插入当前时间到run_log表中的date字段中，直接进入到伪造的“资金清查”界面；如果非首次运行，则通过获取本地数据库datainfo.db中run_log表中的date时间来判断此APP是否运行超过7天，如果超过7天，则无法进入到伪造的“资金清查”界面，同时也无法进行信息备份操作。

![](https://image.3001.net/images/20191223/1577090420_5e007d74071e7.png!small)

![](https://image.3001.net/images/20191223/1577090428_5e007d7c30b29.png!small)

2、
当受害者进入到了伪造的“资金清查”界面后，则是直接在与服务器地址为：<http://103.47.210.243:88/d6>进行直接交互操作了，通过“资金优先清查”进入到各银行界面，下面则以中国银行为例，进行输入案件编号、***号、账户密码、登入密码操作。当受害者输入以上信息后，电信诈骗团伙在服务器后台能实时得到***账户密码信息，从而则可以进行资产转移。

![](https://image.3001.net/images/20191223/1577090438_5e007d861aac2.png!small)

通过抓包所有的信息都是以明文的形式进行上传：

![](https://image.3001.net/images/20191223/1577090444_5e007d8cddae8.png!small)

3、
样本在运行过程中会通过闹钟服务在低电耗模式下开启重复定时任务，主要用于收集用户信息，实时监控受害者；通过上传手机注册信息来获取远程操作指令的参数配置信息。

开启定时任务：

![](https://image.3001.net/images/20191223/1577090455_5e007d974451f.png!small)

1） 通过此APP运行时间是否大于7天来控制否执行定时任务。

![](https://image.3001.net/images/20191223/1577090463_5e007d9f87cc7.png!small)

2） 判断运行环境是否开启网络服务，没开启则不执行下面远控操作

![](https://image.3001.net/images/20191223/1577090519_5e007dd70e960.png!small)

3） 上传手机sim卡序列号、网络类型(2G\3G\4G)进行手机注册操作，同时在通讯过程中数据包进行了AES加密。

![](https://image.3001.net/images/20191223/1577090525_5e007ddd09a69.png!small)

相关的数据包截图：

![](https://image.3001.net/images/20191223/1577090529_5e007de1bba1d.png!small)

接收的数据解密之后参数（在模拟器中执行）：

    
    
    {"is_location_update":0,"switchMobileArray":[],"contactTaskList":[],"messageSwitchMobileArray":[],"sign":"exist","is_message_switch":0,"is_delete_message":0,"commandList":[],"is_del_device":0,"is_contact_update":0,"is_phone_turn":0,"close_sound":0,"is_get_message":1,"delete_new_message":1,"turn_message":0}

![](https://image.3001.net/images/20191223/1577090536_5e007de8a3498.png!small)

4、 根据返回注册手机的参数信息来修改运行参数，从而实现远程控制操作：

指令参数：

指令参数 | 指令功能  
---|---  
none | 值为yes则表示网络注册失败  
delete_new_message | 值为1则设置删除短信标识为true  
is_del_device | 值为1则更新run_log表的date为1800-01-01(即大于7天，直接退出正常运行)  
is_phone_turn | 值为1则表示开启电话转接  
is_message_switch | 值为1则表示是否开启短信转接  
turn_message | 值为1则向指定号码进行转发sim卡序列号  
close_sound | 值为1则设置为静音模式  
commandList | 根据其参数值信息进行相关操作  
is_contact_update | 值为1则表示备份更新通讯录数据  
is_location_update | 值为1则更新GPS位置信息  
is_get_message | 值为1则备份短信信息  
is_delete_message | 值为1则删除短信信息  
switchMobileArray | 电话转接列表  
messageSwitchMobileArray | 短信转接列表  
  
相关的远控操作：

![](https://image.3001.net/images/20191223/1577090543_5e007def864b9.png!small)

相关功能代码：

设置静音模式：

![](https://image.3001.net/images/20191223/1577090550_5e007df645925.png!small)

写入电话转接列表：

![](https://image.3001.net/images/20191223/1577090554_5e007dfa73fe0.png!small)

转发短信：

![](https://image.3001.net/images/20191223/1577090558_5e007dfeb9756.png!small)

备份通讯录：

![](https://image.3001.net/images/20191223/1577090563_5e007e0303409.png!small)

备份短信：

![](https://image.3001.net/images/20191223/1577090567_5e007e07b5e2a.png!small)

删除短信信息：

![](https://image.3001.net/images/20191223/1577090572_5e007e0c84036.png!small)

## 同源分析

通过奇安信威胁分析平台（[http://ti.qianxin.com](http://ti.qianxin.com/)）关联103.47.210.243发现了相同架构的样本10个，功能基本一致，根据其最早编译时间和最后编译时间发现，此类APP最早编译时间为2016年11月22日10时，最新修改后启用的最早时间为2019年2月20日17时；从这些同源APP来看其整体框架未作修改，仅做了部分的细微调整（如URL后缀变化）。

![](https://image.3001.net/images/20191223/1577090579_5e007e132e83c.png!small)

其相关框架大致如下：

![](https://image.3001.net/images/20191223/1577090584_5e007e18a0549.png!small)

通过盘古Janus平台关联发现3款仿冒“CBRC”的样本，其最后编译时间都在2018年3月7日，其中2个使用包名均为“com.apache56.MobileD1”，分析其利用框架与之前关联的一致。不过这三个样本中使用的IP为“183.86.209.139”和”45.125.195.6”。

IP为“183.86.209.139”：

![](https://image.3001.net/images/20191223/1577090592_5e007e20504b1.png!small)

IP为”45.125.195.6”：

![](https://image.3001.net/images/20191223/1577090596_5e007e248f462.png!small)

![](https://image.3001.net/images/20191223/1577090600_5e007e28bc665.png!small)

汇总相关的包名和应用名，可以发现电信诈骗团伙都是通过冒充公检法机构的APP来进行获取受害者的用户银行账户信息和个人隐私信息，从而导致受害者遭受到金钱损失。

**MD5** | **包名** | **应用名**  
---|---|---  
1D7002281B7A73D534271309AB3CA3C0 | com.sms.MobileSMS | 高检院电子协办证  
3F4269BED949905E4ACAAECEDE871ECE | com.android.dobbin | 高检院电子协办证  
8DFA71ED810C54946C3A65A2D3970D68 | com.sms.MobileSMS | 高检院电子协办证  
10FE2FF2A9EBF59F96BE2F81C16B5F75 | com.android.playguns | 高检院电子协办证  
42**B2C031ED0DB7599E7CF540503BAC | com.security.MobileD1 | CBRC  
79E752F5660CE6AF05FB8DB0F44E125B | com.android.goodmans | 高检院电子协办证  
**1D17F49D2546C8AD93AB58DACEB436 | com.security.MobileD1 | CBRC  
ECEF638D69686**9E7F9AFE59D2FA5D6 | com.ademo.chinaphone | 最高人民检察院  
F6DA229B8B68937B0A0B3C0030A4BC79 | com.android.doback | 高检院电子协办证  
FB304A4D2E87A2822D210A2968126777 | com.android.redguns | 警政卫士  
C3ECBDA662BAB53230AF80737E7C8DD9 | com.security.MobileD1 | CBRC  
2654BEFB2953D50D706C60D882BAA76A | com.apache56.MobileD1 | CBRC  
FD0D0D8A0B645B92D8D01EFDE67CB9B1 | com.apache56.MobileD1 | CBRC  
  
## 总结

随着移动互联网技术发展，电信诈骗手段不断升级，通过不断更新“剧本”的方式给受害者洗脑，从而导致受害者深信不疑；当受害者安装了电诈团伙提供的仿冒公检法APP后，同时跟着电诈团伙的“剧本”输入银行账户密码信息，从而导致自身财产被转移；同时电诈团伙利用此APP的“千里眼”功能实时监控受害者的一举一动，进行反侦查活动，不利于警察侦破案件。

奇安信病毒响应中心提醒用户不要安装未知来源的APP，同时提高个人的安全意识，从而可以防止用户隐私信息被盗取的风险。奇安信病毒响应中心移动安全团队会持续对热门仿冒软件的跟踪，目前奇安信威胁情报中心文件深度分析平台

（<https://sandbox.ti.qianxin.com/sandbox/page>）已支持Android样本分析：

同时基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、奇安信NGSOC等，都已经支持对此类攻击的精确检测。

## 参考链接

> [1].<http://www.myzaker.com/article/5d23d5c0b15ec03bbe066e39>

## IOC

### 文件样本MD5：

> 06853346d7d22c6188ad4c2cb40daa10
>
> 79e752f5660ce6af05fb8db0f44e125b
>
> 3f4269bed949905e4acaaecede871ece
>
> ecef638d69686c49e7f9afe59d2fa5d6
>
> f6da229b8b68937b0a0b3c0030a4bc79
>
> 1d7002281b7a73d534271309ab3ca3c0
>
> 8dfa71ed810c54946c3a65a2d3970d68
>
> 42c4b2c031ed0db7599e7cf540503bac
>
> fb304a4d2e87a2822d210a2968126777
>
> 10fe2ff2a9ebf59f96be2f81c16b5f75
>
> c41d17f49d2546c8ad93a***daceb436
>
> fd0d0d8a0b645b92d8d01efde67cb9b1
>
> 2654befb2953d50d706c60d882baa76a
>
> c3ecbda662bab53230af80737e7c8dd9

### C2地址：

> 103.47.210.243
>
> 183.86.209.a139
>
> 45.125.195.6
>
> <http://103.47.210.243:88/d6>
>
> <http://103.47.210.243:88/d6/css/layout.css>
>
> <http://103.47.210.243:88/d6/BANK.php>
>
> <http://103.47.210.243:88/d6/FORM.php?bank=3>
>
> <http://103.47.210.243:88/d6/OK.php>
>
> <http://103.47.210.243:8080/WebMobileD6/phoneajax/index.do>
>
> <http://103.47.210.243:88/D3>
>
> <http://103.47.210.243:8080/WebMobileD3>/phoneajax/index.do
>
> <http://103.47.210.243:88/D4>
>
> <http://103.47.210.243:8080/WebMobileD4/phoneajax/index.do>
>
> <http://103.47.210.243:8080/WebMobileD7/phoneajax/index.do>
>
> <http://183.86.209.139:8080/WebMobileD4/phoneajax/index.do>
>
> <http://183.86.209.139:88/D4>
>
> <http://45.125.195.6:8080/WebMobileD5/phoneajax/index.do>

*本文作者：奇安信威胁情报中心，转载请注明来自FreeBuf.COM

