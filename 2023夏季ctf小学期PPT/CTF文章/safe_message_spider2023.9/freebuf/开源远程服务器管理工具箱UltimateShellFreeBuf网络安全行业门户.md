# UltimateShell

UltimateShell 是一个开源的远程服务器管理工具箱，其目标是为渗透测试工程师、程序员、网站管理员、IT
管理员以及几乎所有需要以更简单的方式处理远程工作的用户提供大量定制功能。

> 注意：程序更新后，若无法正常连接SSH，请备份删除原配置文件`application.properties`

## 一、项目背景

用过很多远程终端管理工具，最初在学校学习路由交换的时候用的是超级终端连接`Console`接口，然后使用`putty`带内管理交换机。再后来学习`Linux`时，使用的是学生版`xshell`、`xftp
`进行`SSH`连接，感觉超级好用，就是限制太多了。在工作的时候发现运维的同事都用`SecureCRT`，但是发现文件传输不够友好，最后使用`MobaXterm`，其可以免费下载使用家庭版，不幸的是，在我保存的会话达到限制数量时，它提示我已经不能再增加会话了，该升级许可了（该花钱了）。

一路过来，百度了、用过了、白嫖了很多的远程终端管理工具，但是在使用它们的过程中或多或少总是有一些困扰：

> 完全免费的工具功能太单一。
>
> 商业软件的免费版限制太多（限制到真就是只能个人用着玩 了）。
>
> 还有一些不错的免费工具、功能也齐全，但是需要注册登录，按套路说不定什么时候就收费了。
>
> 破解版用着确实挺爽的，但总归不大好，说不定什么时候就翻车了（主要是想支持正版:laughing:）。
>
> 总归有一些自己想要而工具没有的功能，但要么工具是闭源的、要么工具的技术栈不熟悉，搞不了。

正好在学习Java代码审计方面的知识，于是起了用Java写个自己想要的远程终端管理工具的心思，主要是出于这些考虑：

> 就当是熟悉Java基础了。
>
> 可以按照自己的想法进行定制化开发。
>
> 能够集成管理外部工具，形成快速启动工具箱。
>
> 集成安全属性，这是很多此类工具所不具备的，如代码检查能力、PoC验证框架，可以方便安全人员快速发现、定位安全问题。
>
> 还有就是想维护一个开源项目，算是对开源环境的一个正向反馈。
>
> 完美！

于是，这代码敲着，敲着，就成了现在这样了......

> 开源不易，且行且珍惜！

## 二、功能特性

支持多操作系统平台，兼容性测试：`Windows`>`Linux`>`MacOS`

支持会话管理

支持本地终端(cmd, bash)

支持`SSH`、`Sftp`，及`内置代码编辑器`，支持代码高亮、折叠等功能

支持`COM`口调试（自动检测存在的`COM`接口）

支持`Telnet`

支持`RDP`远程桌面（基于`FreeRDP`实现）

支持`VNC`，基于`TightVNC Viewer`实现

支持`集成外部工具`，实现快速启动

内置`简易编辑器`，可编辑本地、远程文本文件

内置`Nuclei`GUI，POC概念验证框架

支持60多种主题皮肤切换

支持100多种终端配色方案

支持插件系统

## 三、下载安装包

下载 [ultimateshell](https://github.com/G3G4X5X6/ultimateshell/releases)安装包

  1. `UltimateShell-x.x.x-jar-with-dependencies.jar`：打包了完整的依赖包（平台通用）

  2. `UltimateShell-x.x.x.jar`：没有打包任何依赖包

  3. `ultimateshell_setup.exe`：Windows安装程序（Windows专用）

![image-20220122151254763.png](https://image.3001.net/images/20220226/1645859057_6219d0f1e2882bf8133f6.png!small)

### 3.1 Xpack-Tools 功能增强包

Git
克隆增强包放置到`ultimateshell`工作空间的`tools`目录下，如：`C:\Users\G3G4X5X6\.ultimateshell\tools`

    
    
    # 也可以自己按照仓库的目录结构创建目录，从官网下载工具
    git clone https://github.com/G3G4X5X6/xpack_tools.git
    

## 四、使用截图

### 4.1 快速启动

![image.png](https://image.3001.net/images/20220226/1645859058_6219d0f283096fa2f707a.png!small)  
![image.png](https://image.3001.net/images/20220226/1645859059_6219d0f32d5e4326f986f.png!small)

#### 4.1.1 本地终端

![image.png](https://image.3001.net/images/20220226/1645859059_6219d0f3c4b59c6be78dc.png!small)

#### 4.1.2网络连接

![image.png](https://image.3001.net/images/20220226/1645859060_6219d0f47729d941d3781.png!small)

#### 4.1.3系统信息

![image.png](https://image.3001.net/images/20220226/1645859061_6219d0f54bb68ac5f7c89.png!small)

#### 4.4.4备忘笔记

![image.png](https://image.3001.net/images/20220226/1645859061_6219d0f5f0be602dcd1a3.png!small)

### 4.2 SSH 功能

#### 4.2.1 新建选项卡

SSH 支持公钥登录。

会话分类以路径形式表达，如：local/centos/dev，表示该会话属于local分类下的子类centos下的子类dev。

![image.png](https://image.3001.net/images/20220226/1645859062_6219d0f683274bd7245dd.png!small)

#### 4.2.2 SSH 终端

![image.png](https://image.3001.net/images/20220226/1645859063_6219d0f736c4234b21568.png!small)

#### 4.2.3 sFTP 浏览器

![image.png](https://image.3001.net/images/20220226/1645859064_6219d0f82a3afc351d630.png!small)

#### 4.2.4 专注模式

![image.png](https://image.3001.net/images/20220226/1645859065_6219d0f943b2cde4b65f9.png!small)

### 4.3 Serial 功能

> 只在模拟工具上测试过`console`连接，哪位有条件自己直接上机吧，有问题再反馈，over。

![image.png](https://image.3001.net/images/20220226/1645859066_6219d0fac817bbda41f2c.png!small)

### 4.4 PoC-概念验证框架(Nuclei GUI)

#### 4.4.1 PoC 模板快速搜索

![image.png](https://image.3001.net/images/20220226/1645859067_6219d0fb8c29947f4fe8a.png!small)

#### 4.4.2 设置目标

![image.png](https://image.3001.net/images/20220226/1645859068_6219d0fc826bd76d85399.png!small)

#### 4.4.3 启动检测

![image.png](https://image.3001.net/images/20220226/1645859069_6219d0fd94b45f318c42e.png!small)

#### 4.4.4 检测日志

![image.png](https://image.3001.net/images/20220226/1645859070_6219d0fe8e893bf4e8857.png!small)

### 4.5 更多功能有待探索

## 五、维护者

[@G3G4X5X6](https://github.com/G3G4X5X6)

## 六、开源许可

MIT © 2021 勾三股四弦五小六

