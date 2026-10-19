你的私人资料正在网上交易和出售，想必你自己也已经知道了。其实，每天都有大量的数据会泄漏，这会让我们安全人员感到无力。大多数用户密码和其他敏感信息都会被发布在互联网中的某个地方，供他人窥探和查看，我们毫无办法。为了更好地掌控你的个人信息，你可以使用Haveibeenpwned来缩小你信息被泄露的范围。这是一个很好的开始，但是如果你想确切地知道其他人可以获得你的哪些信息，该怎么办呢？BaseQuery就是答案，BaseQuery是一个多功能应用程序，可以轻松地导入和搜索成千上万的泄露数据。

![](https://image.3001.net/images/20191202/1575298611_5de526333a028.png!small)

## 功能介绍

> 1、4x嵌套存储结构
>
> 2、平均每秒12000+条目的导入速度（Intel Core i7-7700HQ CPU@2.8GHz）
>
> 3、实时查询系统
>
> 4、Facebook的zstd无损压缩算法可以减少数据的大小（平均来说，将数据减少到原始大小的10%以下）
>
> 5、根据特定硬件计算导入所有文件所需的时间
>
> 6、重复数据保护
>
> 7、以标准格式输出您的所有发现
>
> 8、内置电子邮件收集

## 工具安装

广大用户可以直接输入下列命令完成BaseQuery的安装：

    
    
    git clone <https://github.com/g666gle/BaseQuery.git>
    
    sudo chmod 755 -R BaseQuery/
    
    cd BaseQuery
    
    ./dependencies.sh
    
    ./run.sh

## 工具使用

首先，配置“PutYourDataBasesHere”目录中的数据库，BaseQuery只能支持包含下列格式的文件，一行为一条数据：

    
    
    "test@example.com:password" 

或

    
    
    "password:test@example.com"

接下来，在BaseQuery目录路径下打开终端窗口，输入“./dependencies.sh”来安装所有需要的资源。然后输入“./run.sh”启动程序。

## 针对硬件特性导入基于时间的查询

![](https://image.3001.net/images/20191202/1575298644_5de5265433cdc.png!small)

## 查询选项

![](https://image.3001.net/images/20191202/1575298646_5de52656f22f3.png!small)

## 依赖组件

注意：下列组件可以使用‘dependencies.sh’脚本来自动安装。

    
    
    Update packages:    (sudo apt-get update)
    
    Python Version 3.6+ (sudo apt-get install python3.7)
    
    Bash 4+
    
    tar                 (sudo apt-get install tar)
    
    zstd                (sudo apt-get install zstd)
    
    xterm               (sudo apt-get install xterm)

## 工具构建

> 1、Ubuntu 18.04
>
> 2、Bash版本：GNU bash，v4.4.19(1)-release (x86_64-pc-linux-gnu)
>
> 3、Python版本：3.7.1

## 项目地址

> BaseQuery：【[ _GitHub传送门_](https://github.com/g666gle/BaseQuery)】

## 许可证协议

> BaseQuery项目的开发和发布遵循[
> _MIT开源许可证协议_](https://github.com/g666gle/BaseQuery/blob/master/LICENSE.md)。

 *** 参考来源：[
_g666gle_](https://github.com/g666gle/BaseQuery)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

