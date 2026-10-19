![](https://image.3001.net/images/20211108/1636366495_6188f89fe1d3e12d691de.jpg!small)

## 关于SharpSpray

SharpSpray是一款功能强大的活动目录密码喷射安全工具，该工具基于.NET C#开发，可以帮助广大研究人员对活动目录的安全性进行分析。

SharpSpray是DomainPasswordSpray工具的C#实现，并且还引入了很多增强功能以及额外功能。除此之外，该工具还使用了LDAP协议来跟域活动目录服务进行通信。

## 功能介绍

  * 可以从域上下文的内部和外部进行操作。
  * 从列表中排除禁用域的帐户。
  * 自动从活动目录中收集域用户信息。
  * 通过在一次锁定尝试中排除帐户，避免潜在的帐户锁定。
  * 通过自动收集域锁定账户来观察窗口设置，避免潜在的帐户锁定。
  * 与域细粒度密码策略兼容。
  * 用户自定义LDAP筛选器，例如（description=admin）。
  * 支持设置每次身份验证尝试之间的延迟（秒）。
  * 支持设置每次身份验证尝试之间的抖动。
  * 支持单个密码或密码列表。
  * 单文件控制台终端应用程序。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/iomoath/SharpSpray.git

## 工具使用

### 命令行参数

    
    
    > SharpSpray.exe --help
    
     
    
      -v, --Verbose       Show verbose messages.
    
      -u                  (Optional) Username list file path. This will be
    
                          automatically fetched from the active directory if not specified.
    
      -p                  A single password that will be used to perform the password spray.
    
      -k, --pl            (Optional) Password List file path.
    
      -d                  (Optional) Specify a domain name.
    
      -m                  Use this option if spraying from a host located outside the Domain context.
    
      -q, --dc-ip         Required when the option 'm' OutsideDomain is checked
    
      -x                  Attempts to exclude disabled accounts
    
                          from the user list (Not supported with the option -m)
    
      -z                  Exclude accounts within 1 attempt of
    
                          locking out (Not supported with the option -m)
    
      -f                  Custom LDAP filter for users, e.g. "(description=*admin*)"
    
      -o                  A file to output the results to.
    
      -w                  Do not relay on domain lockout observation window settings and use this specific value. (Default 32 minute)
    
      -s                  (Optional) Delay in seconds between each authentication attempt.
    
      -j                  (Optional) Jitter in seconds.
    
      --Force             Force start without asking for confirmation.
    
      --get-users-list    Get the domain users list from the active directory.
    
      --show-examples     Get domain users list from the active directory.
    
      --show-args         Show command line args
    
      --help              Display this help screen.

### 参数介绍

    
    
    -v, --Verbose       显示Verbose信息
    
      -u                （可选）用户名列表文件路径，如果不指定，则自动从活动目录获取  
    
      -p                用于执行密码喷射的单个密码
    
      -k, --pl            （可选）密码列表文件路径
    
      -d               （可选）指定目标域名
    
      -m              如果目标主机位于域上下文之外的位置，则可以使用该选项
    
      -q, --dc-ip         检测’m’参数时要求使用该选项
    
      -x                尝试从用户列表中排除已禁用的账号
    
      -z                 通过在一次锁定尝试中排除帐户，避免潜在的帐户锁定                      
    
      -f                 自定义LDAP过滤器，例如"(description=*admin*)"
    
      -o                 存储处理结果的文件
    
      -s                  （可选）每次身份验证尝试之间的延迟（秒）
    
      -j                  （可选）以秒为单位的抖动
    
      --Force              强制执行任务，无需进行确认
    
      --get-users-list        从活动目录获取域用户列表
    
      --show-examples      从活动目录获取域用户列表
    
      --show-args          显示命令行参数
    
      --help              显示帮助信息

## 工具使用样例

### 样例1

    
    
    SharpSpray.exe -v -x -z --pl password.txt
    
    SharpSpray.exe -x -z -u users.txt --pl psswd.txt
    
    SharpSpray.exe -x -z -u users.txt -p Passw0rd!
    
    SharpSpray.exe -x -z -s 3 -j 1 -u users.txt -k psswd.txt -o sprayed.txt

### 样例2

    
    
    SharpSpray.exe -w 32 -m -d DC-1.local --dc-ip 10.10.20.20 -u users.txt --pl psswd.txt
    
    SharpSpray.exe -w 32 -s 3 -j 1 -m -d DC-1.local --dc-ip 10.10.20.20 -u users.txt --pl psswd.txt

### 样例3

    
    
    SharpSpray.exe --get-users-list
    
    SharpSpray.exe --get-users-list > users.txt
    
    PS> .\SharpSpray.exe --get-users-list | Out-File -Encoding ascii users.txt

## 如何从活动目录中仅获取用户列表

下列命令可以从目标活动目录中获取域用户信息，并打印在终端窗口中：

    
    
    SharpSpray.exe -x -z --get-users-list
    
     
    
    -x: Exclude disabled accounts from the user list.
    
    -z: Exclude accounts within 1 attempt of locking out.

### 参数介绍

    
    
    -x: 从用户列表中排除已禁用的账号
    
    -z: 一次尝试锁定后排除目标账号

## 项目地址

 **SharpSpray：** 【[ _GitHub传送门_](https://github.com/iomoath/SharpSpray)】

## 参考资料

  * [ _https://c99.sh/sharpspray-active-directory-password-spraying-tool/_](https://c99.sh/sharpspray-active-directory-password-spraying-tool/)

