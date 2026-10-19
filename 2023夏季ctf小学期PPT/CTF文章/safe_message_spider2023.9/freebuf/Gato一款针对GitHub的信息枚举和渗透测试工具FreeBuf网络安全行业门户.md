![](https://image.3001.net/images/20230719/1689765616_64b7c6f05607869952cbd.png!small)  

## 关于Gato

Gato是一款针对GitHub的信息枚举和渗透测试工具，该工具是一个GitHub自托管的安全测试工具。在该工具的帮助下，广大蓝队研究人员或渗透测试安全研究人员就可以轻松评估目标组织的GitHub安全性，并尝试枚举其中存在安全问题的个人访问令牌或其他安全问题。

值得一提的是，GitHub建议仅将自托管运行程序用于私有存储库，然而有成千上万的组织仍然会在公共代码库中使用自托管运行程序。因此，该工具还可以搜索并枚举使用了自托管运行程序的GitHub公共存储库。

## 功能介绍

> 1、GitHub PAT特权枚举；
>
> 2、基于API的GitHub代码搜索枚举；
>
> 3、GitHub Action 运行日志解析以识别自托管Runner；
>
> 4、GitHub Action工作流分析；
>
> 5、自动命令执行分支PR创建；
>
> 6、自动命令执行工作流创建；
>
> 7、自动化的工作流敏感信息泄露；
>
> 8、SOCKS5代理支持；
>
> 9、HTTPS代理支持；
>
> 10、敏感信息枚举；
>
> 11、敏感信息提取；
>
> 12、API枚举；
>
> 13、JSON格式输出结果；
>
> 14、GitHub企业服务器支持；
>
> 15、PAT验证；

## 工具安装

当前版本的Gato支持macOS和Linux，并且要求系统安装并配置好Python 3.7环境。

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/praetorian-inc/gato

然后切换到项目目录中，并使用pip install命令完成工具安装即可，我们建议在一个虚拟环境中使用Gato：

    
    
    cd gato
    
    python3 -m venv venv
    
    source venv/bin/activate
    
    pip install .

## 工具使用

安装完成后，我们就可以使用下列命令运行Gato了：

    
    
    gato

或

    
    
    praetorian-gato

我们还可以使用下列命令查看工具的参数帮助选项：

    
    
    gato -h
    
    gato search -h
    
    gato enum -h
    
    gato attack -h

该工具的正常运行还需要你拥有一个GitHub PAT，如需创建，请登录GitHub并访问[
_GitHub开发者设置_](https://github.com/settings/tokens)，并选择“Generate New
Token”并点击“Generate new Token (classic)”。

创建完成后，打开你的Shell，并运行下列命令设置你的GH_TOKEN环境变量：

    
    
    export GH_TOKEN=<YOUR_CREATED_TOKEN>

## 许可证协议

本项目的开发与发布遵循[ _Apache_ _-2_ _._ _0_](https://github.com/praetorian-inc/gato/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Gato** ：【[ _GitHub传送门_](https://github.com/praetorian-inc/gato)】

## 参考资料

> [ _https://github.com/settings/tokens_](https://github.com/settings/tokens)

