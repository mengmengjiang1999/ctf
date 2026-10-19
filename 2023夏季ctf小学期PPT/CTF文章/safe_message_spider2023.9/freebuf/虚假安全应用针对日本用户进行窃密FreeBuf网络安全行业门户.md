McAfee 的安全研究人员发现了针对日本 NTT DOCOMO 用户的新型恶意软件。该恶意软件伪装成合法的移动安全应用程序，在 Google Play
商店中进行分发。应用程序名为 `スマホ安心セキュリティ`或 `Smartphone Anshin Security`实际上该恶意软件是针对 NTT
DOCOMO 移动支付用户进密码盗窃与支付欺诈的。应用程序程序包名为 `com.z.cl​​oud.px.app`与
`com.z.px.appx`，MaAfee 已经告知 Google 下架处理。

## 诱导安装

攻击者使用各种开发者账户在 Google Play 中发布恶意应用程序。雅虎的安全研究员 Yusuke Osumi 最早发现攻击者从海外发送带有
Google Play 链接的短信，引诱用户安装恶意程序。

![image.png-80.2kB](https://image.3001.net/images/20220921/1663727793_632a78b1d3fb45d51b5e4.png!small)来自法国的短信

![image.png-195.5kB](https://image.3001.net/images/20220921/1663727794_632a78b28097976c6f805.png!small)Google
Play 上的恶意软件

攻击者还使用 Google Drive 来分发恶意软件，这一方式安装 APK 文件不会留下任何痕迹，而且安装过程更为简单。如果用户此前允许通过 Google
Drive 来安装未知应用程序，只需要点击三次即可完成安装。

![image.png-261.4kB](https://image.3001.net/images/20220921/1663727795_632a78b34ff6c36931421.png!small)跳转安装页面

## 恶意软件本身

当 NTT DOCOMO
用户安装并启动此恶意软件时，会要求提供网络密码。恶意软件甚至会提示要求输入正确的密码，密码实际是否正确并不重要，这只是一种窃密的方式。

![image.png-103.2kB](https://image.3001.net/images/20220921/1663727796_632a78b434a54f08fc164.png!small)询问网络密码

网络密码可以用于 NTT DOCOMO 的在线支付，只需要输入四位密码即可将费用计入手机账单。

![image.png-164.7kB](https://image.3001.net/images/20220921/1663727796_632a78b4eae14e7047e02.png!small)界面对比

获取密码后，恶意软件会显示虚假的移动安全状态。界面显示与旧版 McAfee Mobile Security
十分类似，但是所有的按钮其实都是假的，并不具备相关功能。

## 技术分析

该恶意软件使用 Golang 编写，在执行期间加载了一个名为 `libmyapp.so`的库，该库在加载时会尝试使用 Web Socket 连接到 C&C
服务器。建立连接后，恶意软件会回传网络信息以及电话号码并接受如下控制：

RPC 函数名| 描述  
---|---  
connect_to| 创建反向代理  
disconnect| 断开反向代理  
get_status| 获取反向代理状态  
get_info| 获取相关信息  
toggle_wifi| 设置 Wi-Fi 开/关  
show_battery_opt| 关闭后台电池优化  
  
![image.png-40.3kB](https://image.3001.net/images/20220921/1663727797_632a78b59f651c26962bf.png!small)数据包中包含个人信息

![image.png-17.4kB](https://image.3001.net/images/20220921/1663727798_632a78b63c973b8d2e4fc.png!small)发送网络密码

通过命令 `toggle_wifi`将受害者从 Wi-Fi 切换到移动网络，再利用窃取的密码进行欺诈性购买。

![image.png-73.2kB](https://image.3001.net/images/20220921/1663727798_632a78b6d4a0f53792ff3.png!small)整体流程

## 结论

恶意软件使用反向代理来窃取用户的密码，实现欺诈性购买从而获利。用户在使用移动设备安装应用程序时，一定要更加小心谨慎。

## IOC

> 193[.]239[.]154[.]23  
> 91[.]204[.]227[.]132  
> ruboq[.]com  
> 5d29dd12faaafd40300752c584ee3c072d6fc9a7a98a357a145701aaa85950dd  
> e133be729128ed6764471ee7d7c36f2ccb70edf789286cc3a834e689432fc9b0  
> e7948392903e4c8762771f12e2d6693bf3e2e091a0fc88e91b177a58614fef02  
> 3971309ce4a3cfb3cdbf8abde19d46586f6e4d5fc9f54c562428b0e0428325ad  
> 2ec2fb9e20b99f60a30aaa630b393d8277949c34043ebe994dd0ffc7176904a4  
> af0d2e5e2994a3edd87f6d0b9b9a85fb1c41d33edfd552fcc64b43c713cdd956

## 参考来源

> [Mcafee](https://www.mcafee.com/blogs/other-blogs/mcafee-labs/fake-security-> app-found-abusing-japanese-payment-system/)

