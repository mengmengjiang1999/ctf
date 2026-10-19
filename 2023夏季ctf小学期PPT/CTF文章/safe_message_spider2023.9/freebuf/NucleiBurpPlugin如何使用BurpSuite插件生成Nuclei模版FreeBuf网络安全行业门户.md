![](https://image.3001.net/images/20220401/1648827246_62471b6ec273b0f2e05f6.png!small)

## 关于Nuclei Burp Plugin

Nuclei Burp Plugin是一款功能强大的BurpSuite插件，可以帮助广大研究人员轻松生成Nuclei模版。

## 功能介绍

### 模版匹配器生成

> 1、使用 从Proxy历史记录或Repeater上下文中选择的响应信息来创建单词或代码匹配器；
>
> 2、为了便于阅读，多行选择被拆分为单独的单词；
>
> 3、为包含非ASCII字符创建二进制匹配器；
>
> 4、每个生成的模板自动包含一个状态匹配器，并使用响应的HTTP状态代码；

### 请求模版生成

> 1、在“Intruder”标签中，可以使用选择的Payload位置来生成请求模版，可选择以下类型：Battering
> ram、Pitchfork或Cluster bomb；
>
> 2、在“Proxy”或“Repeater”标签中，支持从HTTP请求中选择文本片段，并以此生成测试类型为Battering ram的请求模版；

### 模版执行

> 1、生成的模板可以立即执行，为方便起见，输出显示在同一窗口中；
>
> 2、该插件使用从所需请求中提取的绝对路径、绝对模板路径和目标信息自动生成CLI命令；
>
> 3、存储了唯一已执行命令的历史记录，可以在当前会话中快速搜索并重新执行；

## 工具安装

1、使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/projectdiscovery/nuclei-burp-plugin.git

2、自行构建代码，或者直接访问项目的【[ _Releases页面_](https://github.com/projectdiscovery/nuclei-burp-plugin/releases)】下载预构建版本；

3、点击BurpSuite中的“Extender”；

4、点击“Extensions”标签中的“Add”按钮；

5、将“Extension Type”设置为“Java”；

6、选择插件路径，并设置为该插件.jar文件路径；

## 构建代码

我们可以使用下列命令自行构建项目代码：

    
    
    mvn clean package -DskipTests

该方法要求本地设备安装并配置好Maven 3.x和Java 11+。

在macOS上，该插件的依赖组建需要使用下列命令安装：

    
    
    brew install mvn openjdk@11

或者，我们也可以从该项目的【[ _Actions页面_](https://github.com/projectdiscovery/nuclei-burp-plugin/actions)】下载不同的构建版本。

## 插件设置

> 1、该插件会尝试自动检测并完成配置；
>
> 2、代码会使用进程的环境PATH变量来搜索Nuclei代码路径；
>
> 3、BurpSuite代码跟单独的BurpSuite Jar相反，因为它无法访问当前用户的PATH环境变量；
>
> 4、目标模板路径基于默认模板目录计算，该目录在<USER_HOME>/.config/nuclei/.templates-config.json下配置；
>
> 5、当前操作系统已登录用户的用户名将作为模版作者的默认配置值；

## 工具运行截图

![](https://image.3001.net/images/20220401/1648827359_62471bdf9828e2fa8be7f.png!small)![](https://image.3001.net/images/20220401/1648827371_62471beb9f07fd5a52f63.png!small)

![](https://image.3001.net/images/20220401/1648827378_62471bf2d28a6e982d69f.png!small)

## 工具使用演示

【[GIF](https://github.com/projectdiscovery/nuclei-burp-plugin/projectdiscovery/nuclei-burp-plugin/raw/main/static/demo.gif)】

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/projectdiscovery/nuclei-burp-plugin/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Nuclei Burp Plugin：** 【[
_GitHub传送门_](https://github.com/projectdiscovery/nuclei-burp-plugin)】

## 参考资料

> [
> _https://github.com/projectdiscovery/nuclei_](https://github.com/projectdiscovery/nuclei)
>
> [ _https://github.com/projectdiscovery/nuclei/blob/master/nuclei-> jsonschema.json_](https://github.com/projectdiscovery/nuclei/blob/master/nuclei-> jsonschema.json)
>
> [ _https://github.com/projectdiscovery/nuclei-burp-> plugin/actions_](https://github.com/projectdiscovery/nuclei-burp-> plugin/actions)

