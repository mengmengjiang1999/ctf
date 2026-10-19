![](https://image.3001.net/images/20230719/1689768029_64b7d05d75449562f988d.png!small)

## 关于msLDAPDump

msLDAPDump是一款功能强大的LDAP枚举工具，该工具基于Python 3开发，可以帮助广大研究人员在目标域环境中快速实现LDAP枚举任务。

msLDAPDump通过将Python中的lpap3库封装在一个易于使用的接口中，简化了域环境中的LDAP枚举操作。我们建议广大研究人员在Windows环境中使用该工具，如果你在Unix环境中使用msLDAPDump的话，该工具将无法解析那些不能通过eth0访问的主机名。

## 工具安装

由于该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python 3环境。

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/dievus/msLDAPDump.git

安装完成后，切换到项目目录中，并使用pip命令和项目提供的requirements.txt文件安装该工具所需的其他依赖组件：

    
    
    cd msLDAPDump
    
    pip install -r requirements.txt

## 工具使用

### 匿名绑定

用户可以通过该工具实现LDAP匿名绑定，并转储关于LDAP的基本信息，其中包括目标域名上下文、域控制器主机名等信息：

![](https://image.3001.net/images/20230719/1689768075_64b7d08bd9d7a975861e2.png!small)

### 凭证绑定

![](https://image.3001.net/images/20230719/1689768088_64b7d0986a5393fad7e86.png!small)![](https://image.3001.net/images/20230719/1689768096_64b7d0a0c2cbfb9fda7b3.png!small)

  

用户可以使用一个有效的用户账号凭证或一个有效的NTLM哈希来绑定至LDAP。使用了凭证之后，我们将能够获取与匿名绑定请求的相同的数据，以及下列额外内容：

> 1、通过扫描目标系统开放的389和636端口实现子网扫描；
>
> 2、目标域基础信息；
>
> 3、用户；
>
> 4、组；
>
> 5、Kerberoastable账号；
>
> 6、ASREPRoastable账号；
>
> 7、代理信息；
>
> 8、计算机账户，并尝试针对主机名执行DNS查询来识别IP地址；
>
> 9、识别域控制器；
>
> 10、识别服务器；
>
> 11、识别不推荐的操作系统；
>
> 12、识别MSSQL服务器；
>
> 13、识别Exchange服务器；
>
> 14、组策略对象（GPO）；
>
> 15、用户描述字段中的密码；

其中每一次的操作检测结果工具都支持以明文形式呈现在命令行终端窗口中，或存储到单独的文本文件中。

## 工具运行截图

![](https://image.3001.net/images/20230719/1689768115_64b7d0b3f2d3c0eccbe06.png!small)

![](https://image.3001.net/images/20230719/1689768124_64b7d0bc232d8e8a39425.png!small)

![](https://image.3001.net/images/20230719/1689768131_64b7d0c3e382ef70caec1.png!small)

![](https://image.3001.net/images/20230719/1689768138_64b7d0cac78e033372361.png!small)

## 许可证协议

本项目的开发与发布遵循[ _AGPL_
_-3.0_](https://github.com/dievus/msLDAPDump/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **msLDAPDump** ：【[ _GitHub传送门_](https://github.com/dievus/msLDAPDump)】

