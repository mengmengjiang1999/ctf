![](https://image.3001.net/images/20220108/1641614403_61d90c438416b8492d091.jpg!small)  

## 关于OnionJuggler

OnionJuggler是一款功能丰富的Onion服务管理工具，适用于类Unix操作系统。该工具使用POSIX兼容的Shell脚本进行编写，可以帮助广大研究人员在类Unix系统上通过命令行管理自己的Onion服务。

OnionJuggler是一个低要求、可移植的脚本和文档集合，用于帮助服务运营商处理和管理自己的Onion服务。

## 项目目标

> 1、方便Onion服务管理，从激活服务到向其添加客户端授权，提供手动编辑文件的全部功能，而无需过多的修改。
>
> 2、向研究人员展示，管理Onion服务不仅可以通过Web页面和Web服务器的形式，还可以通过命令行的形式。
>
> 3、分发，从源代码级别（FOSS）到允许任何人在任何操作系统、shell或服务管理器上运行代码所产生的效果。

## 功能介绍

> 启用服务
>
> 禁用服务
>
> 更新服务地址
>
> 凭证设置
>
> Onion认证
>
> Onion位置
>
> 备份
>
> 操作安全
>
> Web服务器
>
> 可用性
>
> 可扩展

## 工具要求

### 系统&权限

> 类Unix系统
>
> 超级用户权限以通过root或tor用户调用命令

### 所需组件

> sh
>
> doas/sudo
>
> tor >= 0.3.5.7
>
> grep >=0.9
>
> sed
>
> tar
>
> Openssl
>
> basez
>
> git
>
> python(3)-stem >=1.8.0 (Vanguards)
>
> dialog/whiptail (TUI)
>
> nginx/apache2

### 可选组件

> (lib)qrencode >= 4.1.1

### 开发组件

> pandoc
>
> shellcheck

## 工具安装

首先，广大研究人员需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/nyxnor/onionjuggler.git
    
    cd onionjuggler

### 设置自定义变量

千万不要去修改“/etc/onionjuggler/onionjuggler.conf”这个默认配置文件，因为它会在每次更新的时候自动修改。你自己的本地配置文件路径为“/etc/onionjuggler/conf.d/*.conf”。

如需修改变量值，可以按照下列步骤操作：

使用编辑器打开上述配置文件：

    
    
    "${EDITOR:-vi}" /etc/onionjuggler/cond.d/local.conf

或者使用tee在结尾插入下列配置内容：

    
    
    printf "su_cmd=\"sudo\"\n" | tee -a /etc/onionjuggler/cond.d/local.conf

或者直接使用sed进行编辑：

    
    
    sed -i'' "s|^su_cmd=.*|su_cmd=\"doas\"|" /etc/onionjuggler/cond.d/local.conf

### 设置环境

在克隆到本地的项目目录下创建tor目录，创建手动页面，并将脚本拷贝至目录中：

    
    
    ./configure.sh --install

## 工具使用

### onionjuggler-tui

onionjuggler-tui是命令行工具的终端用户接口封装，某些TUI选项可以允许我们修改认证授权文件。

获取TUI手册：

    
    
    man onionjuggler-tui

运行下列命令即可使用TUI：

    
    
    onionjuggler-tui

### onionjuggler-cli

onionjuggler-cli是该工具负责管理HiddenServices的主脚本，具体可以参考项目docs目录中的内容，这里提供了很多关于Onion服务管理的参考信息。

下列命令可以创建一个名为terminator的服务：

    
    
    onionjuggler-cli on -s terminator

我们也可以在运行时提供指定的运行参数：

    
    
    onionjuggler-cli on --service terminator --socket unix --version 3 --port 80,127.0.0.1:80

## 工具运行截图

![](https://image.3001.net/images/20220108/1641614865_61d90e110f613bd4a8cc9.png!small)

![](https://image.3001.net/images/20220108/1641614871_61d90e172bc38aa4286ac.png!small)

![](https://image.3001.net/images/20220108/1641614876_61d90e1cc98854bb34d8c.png!small)

## 项目地址

 **OnionJuggler：** 【[ _GitHub传送门_](https://github.com/nyxnor/onionjuggler)】

## 参考链接

> [ _https://git.io/onionjuggler_](https://git.io/onionjuggler)
>
> [
> _https://github.com/onionshare/onionshare/tree/develop/cli_](https://github.com/onionshare/onionshare/tree/develop/cli)
>
> [ _https://stem.torproject.org/faq.html#what-python-versions-is-stem-> compatible-with_](https://stem.torproject.org/faq.html#what-python-versions-> is-stem-compatible-with)
>
> [ _https://github.com/nyxnor/onionjuggler/blob/main/docs/onionjuggler-> tui.1.md_](https://github.com/nyxnor/onionjuggler/blob/main/docs/onionjuggler-> tui.1.md)
>
> [ _https://github.com/nyxnor/onionjuggler/blob/main/docs/onionjuggler-> cli.1.md_](https://github.com/nyxnor/onionjuggler/blob/main/docs/onionjuggler-> cli.1.md)
>
> [
> _https://github.com/nyxnor/onionjuggler/blob/main/docs/onionjuggler.conf.5.md_](https://github.com/nyxnor/onionjuggler/blob/main/docs/onionjuggler.conf.5.md)
>
> [
> _https://github.com/nyxnor/onionjuggler/blob/main/docs/vitor.8.md_](https://github.com/nyxnor/onionjuggler/blob/main/docs/vitor.8.md)

