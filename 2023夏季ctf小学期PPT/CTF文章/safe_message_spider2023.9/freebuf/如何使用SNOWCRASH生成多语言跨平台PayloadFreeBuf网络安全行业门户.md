![](https://image.3001.net/images/20210411/1618120011_60728d4b7d1338ec65b47.png!small)

## 关于SNOWCRASH

SNOWCRASH可以帮助研究人员创建可以在Linux和Windows设备上启动的多语言脚本，用户所选择的Payload（支持Bash和PowerShell代码）将会嵌入至一个单独的多语言模板，而这种Payload以及生成的脚本都是与平台无关的，这也就意味着其具备较好的跨平台性。

当前版本的SNOWCRASH提供了多种Payload可供广大研究人员选择和使用，其中包括代码执行、反向Shell建立和二进制代码执行等等。

## SNOWCRASH下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/redcode-labs/SNOWCRASH.git

## 如何使用SNOWCRASH

首先，我们需要使用下列命令安装并配置该工具所需的依赖组件：

    
    
    ./install.sh

然后，我们可以使用下列命令列举出该工具支持的可用Payload：

    
    
    ./snowcrash --list

下列命令可以生成选中的Payload：

    
    
    ./snowcrash --payload memexec --out polyglot_script

修改多语言脚本的后缀：

    
    
    mv polyglot_script polyglot_script.ps1

现在，我们就可以在目标设备上执行我们的多语言脚本了。

## 注意事项

我们可以使用--sleep选项来设置脚本运行和Payload执行的时间间隔以及执行延迟：

    
    
    x[s|m|h]

其中，x代表空闲状态下要花费的间隔量，s代表秒数，m代表分钟数，h代表小时数。

生成之后，包含Payload的脚本后缀名会被设置为.sh或.ps1，具体将取决于目标平台。

## 工具运行截图

![](https://image.3001.net/images/20210411/1618120052_60728d74932f7ebb0f8be.png!small)

![](https://image.3001.net/images/20210411/1618120058_60728d7a9cbd93eb46d54.png!small)

## 项目地址

SNOWCRASH：【[ _GitHub传送门_](https://github.com/redcode-labs/SNOWCRASH)】

## 许可证协议

本项目的开发与发布遵循[ _MIT开源许可证协议_](https://en.wikipedia.org/wiki/MIT_License)。

