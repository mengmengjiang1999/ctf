![](https://image.3001.net/images/20220930/1664542646_6336e7b6ee0fe59d774e1.png!small)

## 关于Pmanager

Pmanager是一款功能强大的密码检索和泄漏检测工具，该工具可以帮助广大研究人员从一个安全的脱机数据库中存储或恢复密码。除此之外，该工具还可以检查目标用户的密码以前是否泄漏过，以防止有针对性的密码重用攻击。

## 功能介绍

> 1、使用了最先进的加密算法确保密码存储安全；
>
> 2、多次迭代argon2id进行密钥派生，使攻击者更难进行暴力攻击；
>
> 3、使用了Aes-gcm256加密算法实现数据库加密；
>
> 4、使用了自定义加密键值对数据库，确保数据完整性；
>
> 5、易于安装和使用，其核心功能不需要连接到外部服务；
>
> 6、支持检查目标用户的密码以前是否泄漏过，以防止有针对性的密码重用攻击；
>
> 7、工具功能通过使用keccak-512散列密码并将前10位数字发送到[
> _XposedOrNot_](https://xposedornot.com/api_doc)来实现；

## 工具运行机制

![](https://image.3001.net/images/20220930/1664542663_6336e7c79d04c76088364.png!small)

## 工具安装

### 发布版本

在Ubuntu操作系统中，Pmanager需要依赖“pkg-config”和“libssl-dev”这两个代码包，我们可以使用下列命令来进行安装：

    
    
    sudo apt install pkg-config libssl-dev -y

接下来，访问该项目的【[
_Releases页面_](https://github.com/yukselberkay/pmanager/releases)】下载对应操作系统的工具代码文件，然后将代码路径添加到PATH环境变量中即可。

### 源码构建（Ubuntu&WSL）

    
    
    sudo apt update -y && sudo apt install curl
    
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    
    sudo apt install build-essential -y
    
    sudo apt install pkg-config libssl-dev git -y
    
    git clone https://github.com/yukselberkay/pmanager
    
    cd pmanager
    
    make install

### Windows安装

首先，我们需要安装并配置好Rust环境：【[ _点我下载_](https://www.rust-lang.org/tools/install)】

接下来，安装Git工具：【[ _点我下载_](https://gitforwindows.org/)】

然后运行下列命令：

    
    
    git clone https://github.com/yukselberkay/pmanager
    
    cd pmanager
    
    cargo build --release

## 工具使用样例

首先，我们需要使用“init”命令来初始化数据库。

### 初始化

    
    
    # 在主目录路径下初始化数据库
    
    pmanager init --db-path ~

### 插入数据

    
    
    # 往数据库插入一个新的用户（用户名-密码对）
    
    pmanager insert --domain github.com

### 获取数据

    
    
    # 通过域名获取指定记录
    
    pmanager get --domain github.com

### 枚举数据

    
    
    # 枚举数据库中的所有记录
    
    pmanager list

### 更新数据

    
    
    # 通过域名更新一条记录
    
    pmanager update --domain github.com

### 删除数据

    
    
    # 从数据库中删除目标域名相关的记录
    
    pmanager delete github.com

### 检查泄漏数据

    
    
    # 检查密码是否之前泄漏过
    
    pmanager leaked --domain github.com

## 工具使用演示

![](https://image.3001.net/images/20220930/1664542734_6336e80e0a73632540b68.gif)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/yukselberkay/pmanager/blob/Master/LICENSE)开源许可证协议。

## 项目地址

 **Pmanager** ：【[ _GitHub传送门_](https://github.com/yukselberkay/pmanager)】

## 参考资料

> [ _https://yukselberkay.github.io/programming/2022/09/12/post-keyval-> db.html_](https://yukselberkay.github.io/programming/2022/09/12/post-keyval-> db.html)
>
> [ _https://xposedornot.com/api_doc_](https://xposedornot.com/api_doc)
>
> [ _https://www.rust-lang.org/tools/install_](https://www.rust-> lang.org/tools/install)
>
> [ _https://gitforwindows.org/_](https://gitforwindows.org/)

