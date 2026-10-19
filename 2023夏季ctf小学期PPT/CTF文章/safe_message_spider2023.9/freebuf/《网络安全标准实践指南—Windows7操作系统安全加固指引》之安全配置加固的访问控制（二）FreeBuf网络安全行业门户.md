2022年5月26日全国信息安全标准化委员会发布了《网络安全标准实践指南—Windows
7操作系统安全加固指引》，全国信息安全标准化委员会针对2020年1月开始微软不再提供Windows 7操作系统的更新服务，制定了Windows
7操作系统安全加固指引，本文根据实践指南内容，从实际出发对windows 7操作系统安全配置加固的访问控制进行实际加固作业。

![](https://image.3001.net/images/20220528/1653707819_6291942b9d80375a68356.png!small)

 **1、管理员账户**

进入“控制面板→管理工具→计算机管理”，在“系统工具→本地用户和组→用户”：Administrator→属性→重命名或设置“账户已禁用”；或Administrator→重命名→修改为其他名称。

![](https://image.3001.net/images/20220528/1653717226_6291b8ea432896b5a892e.png!small)

 **2、Guest** **账户**

进入“控制面板->系统和安全->管理工具->计算机管理”，在“系统工具->本地用户和组”，查看Administrator、Guest及其他账户状态，选择Guest账户，右击属性，勾选“账户已禁用”。

![](https://image.3001.net/images/20220528/1653717258_6291b90aab21f761eca57.png!small)

 **3、多余或者过期账户**

进入“控制面板->系统和安全->管理工具->计算机管理”，在“系统工具->本地用户和组”，查看多余或者过期的账户状态，选择该账户，进行删除。

![](https://image.3001.net/images/20220528/1653717280_6291b920c2dc9c8e7b965.png!small)

 **4、用户自动登录**

在“开始->运行->键入 regedit”设置注册表项：15

HKEY_LOCAL_MACHINE\Software\Microsoft\WindowsNT\CurrentVersion\Winlogon\AutoAdminLogon
(REG_DWORD)，值为0。

![](https://image.3001.net/images/20220528/1653717307_6291b93b3de61dbd3a9e6.png!small)

 **5、远程强制关机**

在运行窗口输入“gpedit.msc”打开本地组策略。配置计算机配置-> Windows设置 ->安全设置 ->本地策略 ->用户权限分配
->“从远程系统强制关机”的策略值。

![](https://image.3001.net/images/20220528/1653717405_6291b99de60a9570f2a0d.png!small)

 **6、共享文件夹访问**

进入“控制面板->管理工具->计算机管理”，进入“系统工具－>共享文件”；修改对应共享文件夹的共享权限。

![](https://image.3001.net/images/20220528/1653717424_6291b9b02c50aea2bd477.png!small)

 **7、匿名访问命名**

“控制面板->管理工具->本地安全策略”，在“本地策略->安全选项”：网络访问：可匿名访问的共享设置为全部删除。

![](https://image.3001.net/images/20220528/1653717440_6291b9c00deab139b16cc.png!small)

 **8、共享账户**

进入“控制面板->管理工具->计算机管理”，在“系统工具->本地用户和组”：根据系统的要求，设定不同的账户和账户组。

![](https://image.3001.net/images/20220528/1653717464_6291b9d838d5eba28d688.png!small)

 **9、远程访问**

配置计算机配置 -> Windows设置 ->安全设置 ->本地策略 ->安全选项
->“网络访问：可远程访问的注册表路径”的策略值为“System\CurrentControlSet\Control\ProductOptions

System\CurrentControlSet\Control\ServerApplications

Software\Microsoft\Windows NT\CurrentVersion”。

![](https://image.3001.net/images/20220528/1653717485_6291b9ed718a5cdd9d7c0.png!small)

 **10、拒绝从网络访问计算机**

在运行窗口输入“gpedit.msc”打开本地组策略。配置计算机配置-> Windows设置 ->安全设置 ->本地策略 ->用户权限分配
->“拒绝从网络访问这台计算机”配置相应值。

![](https://image.3001.net/images/20220528/1653717506_6291ba02e1fbca55218af.png!small)

 **11、拒绝批处理作业登录**

在运行窗口输入“gpedit.msc”打开本地组策略。配置计算机配置-> Windows设置 ->安全设置 ->本地策略 ->用户权限分配
->“拒绝作为批处理作业登录”配置相应值。

![](https://image.3001.net/images/20220528/1653717532_6291ba1c7e19afc7b138c.png!small)

 **12、拒绝服务登录**

在运行窗口输入“gpedit.msc”打开本地组策略。配置计算机配置-> Windows设置 ->安全设置 ->本地策略 ->用户权限分配
->“拒绝作为服务登录”配置相应值。

![](https://image.3001.net/images/20220528/1653717551_6291ba2f877481406949f.png!small)

 **13、拒绝本地登录**

在运行窗口输入“gpedit.msc”打开本地组策略。配置计算机配置-> Windows设置 ->安全设置 ->本地策略 ->用户权限分配
->“拒绝本地登录”配置相应值。

![](https://image.3001.net/images/20220528/1653717571_6291ba435948a9923b3e7.png!small)

 **14、拒绝远程桌面服务登录**

在运行窗口输入“gpedit.msc”打开本地组策略。配置计算机配置-> Windows设置 ->安全设置 ->本地策略 ->用户权限分配
->“拒绝通过远程桌面服务登录”配置相应值。

![](https://image.3001.net/images/20220528/1653717598_6291ba5ee6d23fb2e3bce.png!small)

