研究人员发现一个新的 BRATA 变种在去年年底开始活跃传播，攻击者瞄准英国、波兰、意大利和拉丁美洲的银行和金融机构。

![image.png-118.7kB](https://image.3001.net/images/20220128/1643354928_61f39b307bd660bfca3c9.png!small)攻击趋势

## 演变

最初，在针对意大利某知名零售银行的攻击中发现了 BRATA 银行木马。随后的几个月里，遥测发现了两波新的 BRATA 样本，第一波从 2021 年 11
月开始，第二波从 2021 年 12 月中旬开始。攻击者从第二波攻击开始，在不同国家/地区提供量身定制的 BRATA
变种，甚至还有包含西班牙语和中文字符串的样本。

![image.png-758.2kB](https://image.3001.net/images/20220128/1643354929_61f39b313907368b3e2c0.png!small)常见应用

发现的 BRATA 的主要变种如下所示：

![image.png-2554.6kB](https://image.3001.net/images/20220128/1643354931_61f39b33b7eecacad483d.png!small)三个主要变种

> BRATA.A 是过去几个月中发现最多的变种。该变种主要增加了两个新功能：失陷设备的 GPS 跟踪（似乎仍在开发中），以及对失陷设备执行出厂重置。
>
> BRATA.B 与 BRATA.A 几乎相同。区别在于代码混淆和覆盖页面，来窃取目标银行应用程序的安全号码/PIN。特别的，该变种使用明文 HTTP
> 通信，而在 BRATA.A 中使用 zlib 库压缩。

![image.png-54.5kB](https://image.3001.net/images/20220128/1643354939_61f39b3b73e476248b3a5.png!small)覆盖页面

> BRATA.C 变种通过 Dropper
> 下载并执行真正的恶意软件。大多数安卓银行木马都会试图在外部文件（例如`.dex`或`.jar`）中进行混淆/加密，BRATA
> 只保留必要部分防止被杀软检测。

![image.png-123.9kB](https://image.3001.net/images/20220128/1643354940_61f39b3c07d91d62b50cf.png!small)VirusTotal
检测结果

![image.png-148.1kB](https://image.3001.net/images/20220128/1643354940_61f39b3c9abffe04dff6d.png!small)AndroidManifest
中声明的权限

![image.png-237.8kB](https://image.3001.net/images/20220128/1643354941_61f39b3d28f2f65f62090.png!small)新变种的安装

BRATA.C 的安装过程如上图所示，受害者在下载 Downloader
后只需要授予应用程序一项权限，应用程序就可以从不受信任的来源下载并安装恶意应用程序。受害者点击后，Downloader 会向 C&C 服务器发起 GET
请求下载恶意 .apk 文件。

## 银行账户监控

与其他 Android 银行木马一样，BRATA 通过自定义方法监控银行账户和受害者在其移动设备上执行的操作。应用程序会在安装阶段获得
`Accessibility Service`权限，以观察受害者执行的操作或者通过 VNC 模块查看屏幕上的私人信息（如账户余额、交易记录等）。

攻击者通过 C&C 服务器发送 `get_screen`命令，BRATA 会截取受害者的屏幕截图，通过 HTTP 信道回传给 C&C 服务器。

![image.png-225.5kB](https://image.3001.net/images/20220128/1643354942_61f39b3e7e39714e49735.png!small)接收指令

![image.png-449.6kB](https://image.3001.net/images/20220128/1643354943_61f39b3f084f57f9aa3da.png!small)发送屏幕截图

另一项功能就是键盘记录，BRATA.B 会监控用户的击键记录。当受害者打开银行应用程序，输入了 `Agencia`和 `Conta`的内容会被记录并回传到
C&C 服务器。

![image.png-510kB](https://image.3001.net/images/20220128/1643354945_61f39b4181f25a4f930ff.png!small)目标银行的字段

## GPS 跟踪

应用程序会在安装时请求使用 GPS 权限，但在代码中没有找到使用的痕迹，可能是攻击者为特定的功能在进行开发测试。

![image.png-88.2kB](https://image.3001.net/images/20220128/1643354947_61f39b43994a0e9373614.png!small)GPS
权限请求

## 恢复出厂设置

根据对新变种的分析，攻击者已经增加了恢复出厂设置的功能。该功能会在两种情况下执行：

  * 银行欺诈已经完成，恢复出厂设置会让受害者花费更多的时间才能搞明白到底发生了什么
  * 程序发现被安装在虚拟环境中，恢复出厂设置来阻止动态分析

可由 `eventname`结构中的关键字 `SendMsg_formatdevice`确认。

![image.png-122.1kB](https://image.3001.net/images/20220128/1643354948_61f39b440fb264928d056.png!small)命令列表

`_wsh_formatthisdevice`是负责执行重置的函数，首先检查是否设置了 `admin
manager`变量，再初始化反射类并检索设备管理器运行 `wipeData`方法。

![image.png-171.6kB](https://image.3001.net/images/20220128/1643354948_61f39b44a3b3042985730.png!small)恢复出场设置

![image.png-216.6kB](https://image.3001.net/images/20220128/1643354949_61f39b459449712193378.png!small)请求管理员权限

## C&C 通信

分析发现，BRATA 会使用多个 C&C 信道进行通信。应用程序首先通过 HTTP 协议与 C&C 服务器进行第一次通信，服务器在线的情况下强制将连接切换到
WebSocket 协议。

![image.png-272kB](https://image.3001.net/images/20220128/1643354950_61f39b46b125cc64f7a38.png!small)C&C
通信

HTTP 通信期间，BRATA 会删除受害者设备上的所有安全软件，并从 C&C 服务器接收配置文件。

![image.png-242.7kB](https://image.3001.net/images/20220128/1643354951_61f39b47dfc4499350bfe.png!small)删除列表

通过 WebSocket 协议来减少与 C&C 服务器间的传输数据量，特别是想要从有流量监控系统的网络环境中窃取数据。

如下所示，恶意软件在大部分时间都处于等待状态，直到收到攻击者通过 WebSocket 协议发送执行的命令。

![image.png-508.6kB](https://image.3001.net/images/20220128/1643354952_61f39b48f17580054fe66.png!small)发送重置命令

## 总结

自从 2019 年卡巴斯基发现 BRATA 以来，这种安卓银行木马就从一直都在积极活跃发起攻击，并且不断更新迭代去开发新功能。

## IOC

> 220ec1e3effb6f4a4a3acb6b3b3d2e90  
> e664bd7951d45d0a33529913cfbcbac0  
> 2dfdce36a367b89b0de1a2ffc1052e24  
> 5.39.217.241

## 参考来源

> [CLEAFY](https://www.cleafy.com/cleafy-labs/how-brata-is-monitoring-your-> bank-account)

