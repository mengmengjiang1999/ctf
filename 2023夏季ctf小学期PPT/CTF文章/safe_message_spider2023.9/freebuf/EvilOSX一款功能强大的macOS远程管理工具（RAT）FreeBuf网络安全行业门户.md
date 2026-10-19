**今天给大家介绍一款怎对macOS/OS X的远程管理工具（RAT），研究人员可利用该工具来对macOS系统进行渗透测试。**

![1.png](https://image.3001.net/images/20180810/1533901586_5b6d7b12ed52c.png!small)

## 功能介绍

> 模拟终端实例
>
> 轻松可扩展的模块系统
>
> 无需其他依赖（纯Python实现）
>
> 反病毒产品无法检测（OpenSSL AES-256加密Payload）
>
> 持续感染
>
> GUI和CLI支持
>
> 获取Chrome密码
>
> 获取iCloud令牌和通讯录
>
> 获取/监控剪切板
>
> 获取浏览器记录（Chrome和Safari）
>
> 通过iTunes获取iCloud密码
>
> iTunes（iOS）备份枚举
>
> 记录麦克风
>
> 获取屏幕截图
>
> 尝试通过本地提权获取root权限

## 如何使用

    
    
    # 克隆或下载本项目tory
    
    $ gitclone <https://github.com/Marten4n6/EvilOSX>
    
    # 切换项目目录
    
    $ cdEvilOSX
    
    # 安装依赖模块
    
    $sudo pip install -r requirements.txt
    
    # 开启GUI界面
    
    $python start.py

## 高级用户

本项目还给高级用户提供了CLI接口，可通过SSH进行连接：

    
    
    $ python start.py --builder
    
    $python start.py --cli --port 1337

## 运行截图

![2.png](https://image.3001.net/images/20180810/1533901623_5b6d7b3793206.png!small)

![3.png](https://image.3001.net/images/20180810/1533901623_5b6d7b378d17f.png!small)

## 注意事项

感染一台设备主要分成下列三个步骤：

1.需要在目标设备上运行一个launcher程序，负责运行stager；

2.Stager会向服务器请求一个loader来负责处理Payload额度加载；

3.Loader会返回一个经过加密的特殊Payload，并将其发送给stager；

服务器会通过在HTTP 404错误页面中发送隐藏消息来隐藏其通信数据：

1.命令请求通过GET请求来从服务器端获取；

2.命令响应通过POST请求发送至服务器端；

模块利用的是Python的动态特性，网络数据首先会采用zlib进行压缩，然后通过网络来进行发送。

由于bot只会跟服务器端进行交互，所以服务器并不能得知bot何时下线。

## 许可证协议

本项目遵循[GPLv3许可证协议](https://github.com/Marten4n6/EvilOSX/blob/master/LICENSE.txt)。

***参考来源：[EvilOSX](https://github.com/Marten4n6/EvilOSX)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

