我们基本上每天都会使用微信，与家人朋友视频聊天，与同事讨论工作，付款也会使用微信支付，微信已成为生活中的一部分，甚至已经离不开它，但是你知道这款应用里面也存在漏洞吗，这些漏洞会引起哪些安全隐患问题呢？

说起漏洞大家或许比较陌生，但类似下面这张图的提示大部分人应该都经常看见：  

![1.png](https://image.3001.net/images/20181212/1544582014_5c10737e559ab.png!small)  

你知道点开“ **打开** ”意味着什么吗？是不是从来没有想过这个问题，那么今天我们就从网络安全技术角度去探究，更深层次的学习： **了解iOS URL
Schemes、如何发现iOS URL Schemes、iOS URL Schemes结合漏洞案例。**

 ** **iOS URL Schemes****

 ** ** **基本概念**  
****

抛开iOS从URL Schemes的字面意思理解，就是地址协议( **Scheme一般用来表示协议，比如 http、https、ftp 等**
)，我们所熟知的HTTP协议的URL格式就是：

http(s)://user:pass@host:port/path?query

举个例子：

http://gh0st.cn/，在浏览器输入这个地址，浏览器是使用HTTP协议向 **gh0st.cn** 请求，请求的资源就是 **/** 。

再来看一下iOS URL
Schemes的一个例子：weixin://，你在Safari浏览器(Mobile)输入这个网址就会提示你在"微信"中打开链接吗?，然后由你选择"取消"或"打开";和
**HTTP协议格式的URL访问流程进行对比，iOS URL Schemes 实际上就是启动一个应用的 URL，** 其访问流程是这样的：

浏览器输入"weixin://" -> iOS识别URL Schemes ->询问是否跳转到微信 -> 确认跳转 -> 从浏览器跳转到微信端

 ** ** **那么问题就来了，以上所述流程中的" **iOS识别URL Schemes** "，iOS如何识别这段URL Schemes?
**iOS官方要求的是APP开发者需要自己定义自己APP的"URL Schemes"，只有APP本身定义(支持)了URL
Schemes，iOS才会去识别然后跳转。**  
******

 ** ** ** ** **定义**  
********

一个完整的 URL Schemes 应该分为 Scheme、Action、Parameter、Value 这4个部分，中间用冒号 :、斜线 /、问号
?、等号 = 相连接。

举个例子：

mst://jump?url=https://gh0st.cn/&title=test，它对应的4部分就是如下所示：

Scheme(头): mst、Action(动作): jump、Parameter(参数):
url、title、Value(值):https://gh0st.cn、test

不同的部分之间有符号相连，它们也有一定的规则(和URL部分规则是一样的)：

  * 冒号:：在 **链接头** 和 **命令** 之间；

  * 双斜杠 //：在 **链接头** 和 **命令** 之间，有时会是三斜杠 ///；

  * 问号 ?：在 **命令** 和 **参数** 之间；

  * 等号 =：在 **参数** 和 **值** 之间；

  * 和符号 &：在一组 **参数** 和另一组 **参数** 之间。

  *  **理解**  

上述所举的例子：

mst://jump?url=https://gh0st.cn/&title=test，来简单的说明下这段URL Scheme所产生的效果：

1、跳转到"mst"所对应的APP

2、在APP中执行jump动作(跳转网站)

3、告诉APPjump动作所需的url和title参数，对应的值分别为https://gh0st.cn/和test

 **可以理解为在APP应用中访问https://gh0st.cn/，网页标题为test。**

 **寻找iOS APP的URL Schemes**

当你学会了如何寻找APP的URL Schemes，你就算发现了半个漏洞。

 ** ** ** ** ** **获取IPA包**  
**********

基本的URL Schemes可以在iOS APP中的Info.plist文件中寻找到，而一般你是无法获取到APP的ipa包的，所以需要借助软件获取到这个包。

前提是你需要这两台设备：MacBook、iPhone，如果你只拥有一台iPhone的话也有办法去获取(需要Thor APP，具体方法自行寻找)。

Mac上先安装Apple Configurator 2，然后你需要在该软件中登录你的Apple账户：

 ** ** ** ** **
**![2.png](https://image.3001.net/images/20181212/1544582156_5c10740c20533.png!small)使用iPhone充电线将手机连接Mac，这时候软件中就会显示已经连接Mac的设备：  
************

 ** ** ** ** **
**![3.png](https://image.3001.net/images/20181212/1544582175_5c10741ff3703.png!small)假设你需要获取微信的URL
Schemes，那么你的手机已经安装过了微信，然后使用该软件进行添加，选中设备点击添加按钮，选择应用：  
************

 ** ** ** ** **
**![4.png](https://image.3001.net/images/20181212/1544582194_5c107432a6dc4.png!small)搜索微信，选中添加：  
************

 ** ** ** ** **
**![5.png](https://image.3001.net/images/20181212/1544582213_5c10744566fc8.png!small)  
************

当你下载完成看见如下提示的时候，在Finder中按快捷键 Command+Shift+G，输入~/资源库/Group

Containers/K36BKF7T3D.group.com.apple.configurator/Library/Caches/Assets/TemporaryItems/MobileApps/

![6.png](https://image.3001.net/images/20181212/1544582238_5c10745e35fe9.png!small)软件下载的微信ipa文件就存在该文件夹中：

![7.png](https://image.3001.net/images/20181212/1544582279_5c107487dfac6.png!small)进入文件夹将ipa文件复制到其他地方：  

![8.png](https://image.3001.net/images/20181212/1544582301_5c10749d69ecf.png!small)然后回到Apple
Configurator 2的提示，点击停止即可。  

 **获取基本** **URL Schemes**

将IPA包后缀名修改为ZIP，然后解压，进入Payload目录会看见一个.APP后缀名文件，选中文件右击显示包内容：  

![9.png](https://image.3001.net/images/20181212/1544582334_5c1074bed92db.png!small)找到Info.plist文件并打开，搜索关键词URLSchemes：  

![10.png](https://image.3001.net/images/20181212/1544582354_5c1074d215679.png!small)被String标签所包含的就是微信的URL
Schemes：  

![11.png](https://image.3001.net/images/20181212/1544582379_5c1074eb973cb.png!small)

 **寻找完整** **URL Schemes**

 **如上已经了解了如何获取最基本的URL Schemes，但是这远远不够，因为完整的URL
Schemes有4部分，而目前只找到了第一部分，仅仅能做到的功能就是启动，而想找到更多的非基本URL
Schemes需要其他的方法。有很多方法在这里不一一例举了，只列几个常见的思路供你参考。  
**

 **从手机站点页面获取  
**

一般网站都会有这些子域名：m\h5\mobile...

打开这些子域名，利用Chrome的开发者工具(F12)切换为手机模式视图，这样就能模拟手机去访问了：

![12.png](https://image.3001.net/images/20181212/1544582459_5c10753bf19cb.png!small)  

那在这里可以在该页面的HTML代码中寻找URL Schemes(前提是你已经知道了基本的URL Schemes)

在这里我从页面的JavaScript代码中发现了很多URL Schemes：

![13.png](https://image.3001.net/images/20181212/1544582485_5c1075558f80b.png!small)  

有些还有参数，可以根据命名来猜这些URL Schemes的含义，例如path:
"mst://jump/core/web/jump"，就可以知道这个是做Web跳转的，那跳转到哪个地址是什么参数控制呢?下面也有对应的告诉我们是url参数去控制，也就组成了这样一个URL
Scheme: mst://jump/core/web/jump?url=https://gh0st.cn

 **逆向APP**

不仅是iOS，安卓也支持URL Schemes，而一般的定义是一样的，所以你可以基于获取基本URL
Schemes这个步骤将.APP文件的后缀去掉，这时候这个文件就变成了一个文件夹拖到Sublime里面全局搜索" **weixin://** "即可。

至于安卓的APK的逆向可以参考i春秋社区中的< 打造Mac下APK逆向环境到实战接口XSS挖掘 >，可以在源代码中、所有文件内容中搜索URL
Schemes。

![14.png](https://image.3001.net/images/20181212/1544582521_5c107579f228d.png!small)

 **漏洞案例**

 **APP内URL跳转问题**

其实严格来讲这不算是漏洞，毕竟利用有限，但又和 **一切能产生危害的问题都算漏洞**
这句话所冲突，所以在这还是选择列了出来，至于厂商觉不觉得是个安全性问题，还要看他们对“安全风险“的定义。

如何发现这类问题?在上文中我提到了如何发现URL Schemes，只要你发现了这种类型的URL
Schemes就可以尝试替换地址为你的地址然后使用浏览器打开查看是否能在APP内跳转到你的地址，当然利用方式也很简单，构建一个HTML页面即可，然后将网址发送给“
**受害者** ”即可：

![15.png](https://image.3001.net/images/20181212/1544582566_5c1075a6c29b3.png!small)
**凭证窃取(设计不当)**  

 **在做一次漏洞挖掘的时候也碰见了很多次这种问题，大概的描述下就是我找到了能在APP中打开网页的入口方式(例如：二维码扫描、URL
Schemes动作)，让APP访问到我的地址，这样我就可以直接获取到APP中登录后的凭证信息。  
**

**![16.png](https://image.3001.net/images/20181212/1544582624_5c1075e06e9d0.png!small)  
**

利用方式和URL跳转的方式是一样的；关于这方面漏洞产生原理得出一个可能 **“不太严谨的结论”** ：
**APP在做HTTP请求的时候默认所有访问的都是信任域，所以带上了本身已经登录的凭证去请求了。**

 **  
**

 **结合漏洞扩大攻击面**

在一次APP的漏洞挖掘中发现了一个JSONP劫持的问题，但是在这里只会对APP用户产生影响，在没有二维码扫描的情况下就需要结合URL
Schemes来扩大这个漏洞的影响面，而不是局限于self。

利用流程：

用户打开https://gh0st.cn/test.html，test.html内容：

![17.png](https://image.3001.net/images/20181212/1544582648_5c1075f866ff9.png!small)用户点开之后启动mst应用执行jump动作，跳转到https://gh0st.cn/jsonp.html，jsonp.html内容  

![2222.png](https://image.3001.net/images/20181212/1544582674_5c107612d33fd.png!small)  

 **URL Schemes劫持**

这个漏洞是15年在乌云爆出来的，漏洞编号为：wooyun-2015-0103233，大家可以自行去查看。

这个问题说白了是一个流程上的缺陷，苹果官方没有限制APP定义的URL Schemes名字，导致其他APP也可以定义“支付宝”的URL
Schems名字；又因为iOS系统判定URL Schemes优先级顺序与 Bundle ID 有关(一个 Bundle ID
对应一个应用)，如果有人精心伪造 Bundle ID，iOS 就会调用恶意 App 的 URL Schemes 去接收相应的 URL Schemes
请求，这就导致了可以被劫持。

还有很多思路等着我们去探寻，此文仅做思路启发。

