## 1、开启密码复杂度策略

路径：cmd命令运行gpedit.msc—>安全设置—>账户策略—>密码策略。

标准：密码必须符合复杂性要求—启用；密码长度最小值—8个字符；密码最短使用期限—1天；密码最长使用期限—90天；强制密码历史—0个记住的密码；用于还原的加密来存储密码—已禁用。

加固如截图所示：

![](https://image.3001.net/images/20210709/1625801932_60e7c4cc51794a7b51b80.png)

## 2、开启账户锁定策略

路径：cmd命令运行gpedit.msc—>安全设置—>账户策略—>账户锁定策略。

标准：账户锁定阈值—5次。

加固如截图所示：

![](https://image.3001.net/images/20210709/1625801947_60e7c4db18a04184bf667.png)

## 3、开启审核策略

路径：cmd命令运行gpedit.msc—>安全设置—>本地策略—>审核策略。

标准：开启所有审核策略。

加固截图如下所示：

![](https://image.3001.net/images/20210709/1625801959_60e7c4e789f4908c22582.png)

## 4、用户权限分配

### 4.1关闭系统权限

路径：cmd命令运行gpedit.msc—>安全设置—>本地策略—>用户权限分配—>关闭系统。

标准：仅允许administrator账户。

加固截图如下：

  

![](https://image.3001.net/images/20210709/1625801972_60e7c4f43deae011110cd.png)

### 4.2拒绝从网络访问这台计算机

路径：路径：cmd命令运行gpedit.msc—>安全设置—>本地策略—>用户权限分配—>拒绝从网络访问这台计算机。

标准：拒绝除administrator组外的所有组。

加固截图如下：

**![](https://image.3001.net/images/20210709/1625801986_60e7c5029c7b554c70b86.png)**

## 5、安全选项

路径： cmd命令运行gpedit.msc—>安全设置—>本地策略—>安全选项。

### 1、启用登录时间过期后断开与客户端的链接

![](https://image.3001.net/images/20210709/1625802131_60e7c5935f372cd94576b.png)

### 2、设置暂停会话所需的空闲时间数量

![](https://image.3001.net/images/20210709/1625802155_60e7c5abafc7bb2cf86a8.png)

### 3、启用清除虚拟内存页面文件

![](https://image.3001.net/images/20210709/1625802169_60e7c5b94de053a569fe7.png)

### 4、启用不显示最后的用户名

![](https://image.3001.net/images/20210709/1625802191_60e7c5cf212a4b8172721.png)

### 5、启用不显示用户信息

![](https://image.3001.net/images/20210709/1625802204_60e7c5dc1c2d381cd4af8.png)

### 6、启用提示密码过期

![](https://image.3001.net/images/20210709/1625802216_60e7c5e8cc42fdd086684.png)

### 7、禁用：无须按ctrl+alt+del

![](https://image.3001.net/images/20210709/1625802230_60e7c5f6a09fa8d8ccad0.png)

### 8、启用域环境：域控制器身份验证以解锁工作站

![](https://image.3001.net/images/20210709/1625802251_60e7c60b7ab5b9e80962d.png)

### 9、设置域环境：设置登录到缓存的次数

![](https://image.3001.net/images/20210709/1625802271_60e7c61f099435a7cc7e9.png)

### 10、重命名系统管理员账户

![](https://image.3001.net/images/20210709/1625802288_60e7c6308cd8f9da87eca.png)

### 11、关闭自动播放

路径：cmd命令运行gpedit.msc，window组件—>自动播放策略—>关闭自动播放

![](https://image.3001.net/images/20210709/1625802301_60e7c63daf0a74510e4d7.png)

### 12、关闭多余服务

路径：cmd命令运行serverces.msc,

标准：禁用Application Management、Background Intelligent Transfer
Service、RemoteRegistry、Print Spooler

![](https://image.3001.net/images/20210709/1625802313_60e7c6494095105b0fc99.png)

### 13、关闭默认共享服务

路径：cmd运行net share命令查看默认共享文件，cmd运行servers.msc进入系统服务。

标准：关闭所有默认共享文件夹：C$/IPS$/admin$,共享服务对应的名称是
“Server”（在进程中的名称为services），在弹出的“常规”标签中把“启动类型”由原来的“自动”更改为“已禁用”。然后单击下面“服务状态”的“停止”按钮，

![](https://image.3001.net/images/20210709/1625802324_60e7c654d14042899e424.png)

## 6、启用安全传输协议

路径：cmd命令运行gpedit.msc—>管理模板—>远程桌面服务—>远程桌面会话主机—>安全—>远程（RDP）连接要求使用指定的安全层。

标准：启用 SSL（TLS1.0）

截图所示：

**![](https://image.3001.net/images/20210709/1625812877_60e7ef8d5ee4c61e1a323.png)**

## 7、远程会话连接超时设置

路径：cmd命令运行gpedit.msc—>管理模板—>远程桌面服务—>远程桌面会话主机—>会话时间设置—>设置活动但空闲的远程桌面服务会话的时间限制·。

标准：启用15分钟

截图如下：

![](https://image.3001.net/images/20210709/1625812891_60e7ef9bc70f85f5b65f0.png)

## 8、会话连接数设置

路径：cmd命令运行gpedit.msc—>管理模板—>远程桌面服务—>远程桌面会话主机—>链接—>限制连接的数量

标准：启用，最大连接数为20

截图如下：

![](https://image.3001.net/images/20210709/1625812904_60e7efa820f1a89de2b79.png)

## 9、系统防火墙设置

### 9.1开启系统防火墙

路径：cmd运行firewall.cpl。

标准：开启系统防火墙，使用推荐设置。

截图如下：

![](https://image.3001.net/images/20210709/1625812915_60e7efb33aad3e7b573ce.png)

### 9.2禁用高危端口

路径：cmd运行firewall.cpl->高级设置->入站规则。

标准：创建入站规则，新建规则，禁用135，137，138，139，445端口。

截图所示：

**![](https://image.3001.net/images/20210709/1625812930_60e7efc25c77e4b0a541e.png)**

## 10、正确配置日志情况

路径：cmd运行eventvwr.msc打开事件管理器—>window日志。

标准：应用程序，安全，setup，系统日志属性修改为：日志大小为102400，不覆盖事件。

截图：

![](https://image.3001.net/images/20210709/1625812940_60e7efcc0113c611bbc4b.png)

## 11、安全防护

### 1、启用并正确配置SYN攻击保护

路径：cmd运行regedit,查看注册表项

HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters

标准：创建以下项并赋予值类型为DWORD：

SynAttackProtect=1

TcpMaxPortsExhausted=5

TcpMaxHalfOpen=500

TcpMaxHalfOpenRetried=400

### 2、启用ICMP攻击保护

路径：cmd运行regedit,查看注册表项

HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters

标准：创建以下项并赋予值类型为DWORD：

EnableICMPRedirect=0

备注：有效值：0（禁用），1（启用）

### 3、启用碎片攻击保护

路径：cmd运行regedit,查看注册表项

HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters

标准：创建以下项并赋予值类型为DWORD：

EnablePMTUDiscovery=0

### 4、禁止windows自动登录

路径：cmd运行regedit,查看注册表项

HKEY_LOCAL_MACHINE\Software\Microsoft\WindowsNT\CurrentVersion\Winlogon

标准：创建以下项并赋予值类型为DWORD：

AutoAdminLogon=0

备注:AutoAdminLogon值1为自动登录

### 5、启用源路由攻击保护

路径：cmd运行regedit,查看注册表项

HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters

标准：创建以下项并赋予值类型为DWORD：

DisableIPSourceRouting=2

备注：此数据的有效值为0-2，0为表示所有数据包，1表示不转发源路由数据包，2表示丢弃所有传入源路由的数据包。

### 6、禁用失效网关检测

路径：cmd运行regedit,查看注册表项

HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters

标准：创建以下项并赋予值类型为DWORD：

EnableDeadGWDetect=0

备注：此数据的有效值0-1，0为禁用，1启用。

### 7、TCP连接存活时间设置

路径：cmd运行regedit,查看注册表项

HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters

标准：创建以下项并赋予值类型为DWORD：

KeepAliveTime=3000(5分钟)

### 8、重传单独数据片段次数设置

路径：cmd运行regedit,查看注册表项

HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters

标准：创建以下项并赋予值类型为DWORD：

TcpMaxDataRetransmissions=65535

备注：此数据的有效值为0-65535.

### 9、禁用路由发现功能

路径：cmd运行regedit,查看注册表项

HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters

标准：创建以下项并赋予值类型为DWORD：

PerformRouterDiscovery=0

备注：此数据的有效值0-1，0为禁用，1启用。

## 12、配置系统时间同步（NET）

路径：

控制面板->日期和时间->Internet时间->更改设置，勾选“与Internet时间服务器“，服务器框里填入：自定义服务器源时间。

截图如下：

![](https://image.3001.net/images/20210709/1625813040_60e7f0307816fe73aacdf.png)

## 13、数据执行保护（DEP）

路径：控制面板->系统，在高级选项选项卡的“性能“下的设置，选择数据执行保护选项卡，选择“仅为基本window操作系统程序和服务启用DEP“。

截图：

  
![](https://image.3001.net/images/20210709/1625813030_60e7f02621c281d250bb8.png)

## 14、开启屏幕保护程序

路径：控制面板->外观->更改屏幕保护程序。

标准：启用并设置等待时间为10分钟

截图：

![](https://image.3001.net/images/20210709/1625813058_60e7f042f371a67a356ea.png!small)

## 15、安装杀毒软件

标准：安装可信杀毒软件且病毒库特征库版本为最新。

截图：

![](https://image.3001.net/images/20210709/1625814677_60e7f695da6725d674688.png!small)

## 16、远程管理地址限制

路径：cmd运行firewall.cpl->高级设置->入站规则->Windows防火墙高级设置->远程桌面（TCP-In）。

标准：仅允许自定义IP远程管理访问主机。

截图:

![](https://image.3001.net/images/20210709/1625814662_60e7f686dcd934775acbd.png)

