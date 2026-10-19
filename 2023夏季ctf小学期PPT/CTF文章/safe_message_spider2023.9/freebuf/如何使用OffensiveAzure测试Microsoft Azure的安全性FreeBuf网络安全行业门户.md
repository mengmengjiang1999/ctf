![](https://image.3001.net/images/20220630/1656599186_62bdb292e4aef671fc3c0.png!small)  

## 关于Offensive-Azure

Offensive-Azure是一款针对Microsoft
Azure的安全测试工具，该工具基于Python语言开发，支持跨平台运行（与平台无关），可以帮助广大研究人员对Microsoft
Azure应用进行渗透测试或安全研究。

## 功能介绍

> ./Device_Code/device_code_easy_mode.py：生成目标用户要输入的代码，可以在网络钓鱼或社工活动中生成常用令牌；
>
> ./Access_Tokens/token_juggle.py：通过各种方式获取指定资源的最新令牌和访问令牌；
>
> ./Access_Tokens/read_token.py：接收访问令牌并解析包含的声明信息，检查过期时间，尝试验证签名；
>
> ./Outsider_Recon/outsider_recon.py：域名作为输入参数，尽可能多地枚举有关租户的信息，而无需身份验证；
>
> ./User_Enum/user_enum.py：接收用户名或用户名列表作为输入参数，并尝试枚举有效帐户；
>
> ./Azure_AD/get_tenant.py：接收访问令牌或刷新令牌作为输入参数，输出租户ID和租户名称；
>
> ./Azure_AD/get_users.py：接收访问令牌或刷新令牌作为输入参数，输出Azure AD中的所有用户以及Microsoft
> Graph中的所有可用用户属性；
>
> ./Azure_AD/get_groups.py：接收访问令牌或刷新令牌作为输入参数，输出Azure AD中的所有组以及Microsoft
> Graph中的所有可用组属性；
>
> ./Azure_AD/get_group_members.py：接收访问令牌或刷新令牌作为输入参数，输出Azure
> AD中的所有组成员身份以及Microsoft Graph中的所有可用组成员属性；
>
>
> ./Azure_AD/get_subscriptions.py：接收ARM令牌或刷新令牌作为输入参数，输出Azure中的所有订阅以及Azure资源管理器中的所有可用订阅属性；
>
>
> ./Azure_AD/get_resource_groups.py：接收ARM令牌或刷新令牌作为输入参数，输出Azure中的所有资源组以及Azure资源管理器中的所有可用资源组属性；
>
> ./Azure_AD/get_vms.py：接收ARM令牌或刷新令牌，输出Azure中的所有虚拟机以及Azure资源管理器中的所有可用的虚拟机属性；

## 工具安装

我们有很多种方法来下载、安装和配置Offensive-Azure。

我们建议广大研究人员直接克隆本项目代码库，然后直接运行想要的功能模块即可。项目提供了一个requirements.txt文件来帮助我们安装和配置该工具所需的依赖组件。

### Poetry安装

该项目使用了poetry进行构建，因此可以使用下列方法来安装和部署Offensive-Azure：

    
    
    git clone https://github.com/blacklanternsecurity/offensive-azure.git
    
    cd ./offensive-azure
    
    poetry install

### pip安装

该工具的封装版本已经上传到了pypi上，因此我们也可以使用pipi命令来安装Offensive-Azure。我们建议大家使用pipenv来进行绿色环境部署：

    
    
    pipenv shell
    
    pip install offensive_azure

## 工具使用

该工具的每一个功能模块都可以独立运行，也可以将其作为独立的包引入到其他地方使用，每一个模块都会导入到与模块文件名相同的脚本中。

### Poetry使用

    
    
    poetry install
    
    poetry run outsider_recon your-domain.com

### pip使用

    
    
    pipenv shell
    
    pip install offensive_azure
    
    outsider_recon your-domain.com

## 许可证协议

本项目的开发与发布遵循[ _GPL_ _-3.0_](https://github.com/blacklanternsecurity/offensive-azure/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Offensive-Azure** ：【[
_GitHub传送门_](https://github.com/blacklanternsecurity/offensive-azure)】

