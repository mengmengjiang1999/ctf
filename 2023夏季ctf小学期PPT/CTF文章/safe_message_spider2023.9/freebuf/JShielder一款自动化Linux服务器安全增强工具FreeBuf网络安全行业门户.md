***本工具仅供技术分享、交流讨论，严禁用于非法用途。**  

![a.jpg](https://image.3001.net/images/20190728/1564248222_5d3c889e9195e.jpg!small)

## JShielder

**JSHielder是一款开源的Bash脚本，旨在帮助系统管理员和开发人员增强Linux服务器的安全性，以更好地开发任何Web应用程序或在线服务。该工具可以自动化安装托管Web应用程序所必须的包，并在少量用户交互的情况下完成Linux服务器的安全增强配置。新增加的脚本遵循CIS
Benchmark指南来为Linux服务器建立安全配置。**

## 运行机制

JShielder是一款针对Linux服务器的自动化安全增强脚本，配置步骤如下：

> 1、 配置主机名
>
> 2、 重新配置时区
>
> 3、 更新整个系统
>
> 4、 创建新的管理员用户，无需通过root远程连接来管理服务器
>
> 5、 帮助用户生成安全RSA密钥，避免使用传统密码
>
> 6、 配置、优化和增强SSH服务器的安全性（某些设置遵循CIS Benchmark）
>
> 7、 配置IPTABLE规则，保护服务器免受常见攻击影响
>
> 8、 禁用冗余的文件系统和网络协议
>
> 9、 通过安装fail2ban保护服务器免受爆破攻击的威胁
>
> 10、以蜜罐、监控、屏蔽和警告工具安装并配置Artillery
>
> 11、安装PortSentry
>
> 12、安装、配置和优化MySQL
>
> 13、安装Apache Web服务器
>
> 14、通过配置文件和安装Modules ModSecurity增强Apache安全性
>
> 15、通过安装ModSecurity NginX模块和OWASP ModSecurity Core规则集增强NginX
>
> 16、安装RootKit Hunter
>
> 17、增强Root Home和Grub配置文件
>
> 18、安装Unhide以帮助检测隐藏进程
>
> 19、安装Tiger（严重安全审计与入侵防御系统）
>
> 20、限制Apache配置文件访问
>
> 21、禁用编译器
>
> 22、创建系统更新的每日Corn任务
>
> 23、通过sysctl配置文件增强内核安全性
>
> 24、/tmp目录增强
>
> 25、安装PSAD入侵检测系统
>
> 26、禁用USB支持
>
> 27、配置默认UMASK
>
> 28、配置和启用Auditd
>
> 29、遵循CIS Benchmark配置Auditd规则
>
> 30、安装Sysstat
>
> 31、安装ArpWatch
>
> 32、自动配置GRUB Bootloader密码
>
> 33、安全Boot设置
>
> 34、设置安全文件权限

## CIS Benchmark JShielder脚本添加

如需单独添加安全增强脚本，请务必遵循CIS
Benchmark指南，具体请参考这篇【[文档](https://www.cisecurity.org/benchmark/ubuntu_linux/)】。

## 工具运行

以root用户身份运行下列命令即可使用JShielder：

    
    
    ./jshielder.sh

### 项目地址

> JShielderv2.4：【[GitHub传送门](https://github.com/Jsitech/JShielder)】

 ***
参考来源：[Jsitech](https://github.com/Jsitech/JShielder)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

