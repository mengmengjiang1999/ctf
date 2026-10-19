![](https://image.3001.net/images/20220328/1648470855_6241ab47cecb56423e4cb.jpg!small)

## 关于Oh365UserFinder

Oh365UserFinder是一款功能强大的信息枚举工具，该工具基于Python
3开发，主要针对的是Office365用户信息安全。该工具可以帮助广大用户和研究人员识别有效的Office365账号和域，而且整个过程不会让目标账号暴露在安全风险之中或导致账户被锁定。

该工具可以对响应信息进行分析，以识别“IfExistsResult”标志是否为NULL，并且还会在目标用户或账号有效的情况下做出适当的响应。Oh365UserFinder能够根据响应数据来尝试识别误报，并自动创建一个等待周期，以允许重置阈值，或提醒用户去增加尝试操作之间的间隔时间周期。

Oh365UserFinder还支持使用“-d”或“--domain”参数来轻松识别Office365中是否存在目标域，这样就可以省去了从文本中复制url地址并将其输入到目标域url地址栏中所花的时间。

## 工具下载

广大研究人员可以直接使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/dievus/Oh365UserFinder.git

接下来，在命令行终端中切换到项目根目录，然后安装该工具所需的依赖组件：

    
    
    pip3 install -r requirements.txt

## 工具使用

下列命令可以打印出该工具的帮助文档：

    
    
    python3 Oh365UserFinder.py -h

## 工具参数命令

> -h, --help - 查看帮助信息
>
>  
>
>
> -e, --email - Oh365UserFinder所要扫描的单个电子邮箱账号
>
>  
>
>
> -r, --read - 从文本文件中读取目标电子邮件列表，例如“-r emails.txt”
>
>  
>
>
> -w, --write - 从文本文件中读取有效的电子邮件列表，例如“-w validemails.txt”
>
>  
>
>
> -c, --csv - 将有效电子邮件账户写入至CSV文件中，例如“-c validemails.csv”
>
>  
>
>
> -t, --timeout - 设置每次操作尝试之间的时间间隔（秒），例如“-t 60”
>
>  
>
>
> -d, --domain - 检测目标域是否有效，例如“-d mayorsec.com”
>
>  
>
>
> \--verbose - Verbose模式输出

## 工具使用样例

    
    
    python3 o365UserFinder.py -e example@test.com
    
    
    python3 Oh365UserFinder.py -r emails.txt -w validemails.txt
    
    
    python3 Oh365UserFinder.py -r emails.txt -w validemails.txt -t 30 -v

## 注意事项

需要注意的是，
Microsoft针对这种安全检测也设置了一定的防御措施，并且会时不时地反馈误报信息。如果你发现了这类问题，请暂停测试，并使用“-t”参数增加每次测试操作之间的间隔周期。

## 工具使用演示

### 工具主界面

![](https://image.3001.net/images/20220328/1648471142_6241ac661f562e6c2f31f.png!small)

### 信息扫描

![](https://image.3001.net/images/20220328/1648471149_6241ac6d26375ec7cd3d7.png!small)

### 信息枚举

![](https://image.3001.net/images/20220328/1648471165_6241ac7d3caa26b576c2f.png!small)

### 域验证

![](https://image.3001.net/images/20220328/1648471178_6241ac8abc3a35f74899e.png!small)

## 发布版本

 **点击获取：** 【[ _Releases页面_ _-_ _v_
_1.0.1_](https://github.com/dievus/Oh365UserFinder/releases)】

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/dievus/Oh365UserFinder/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Oh365UserFinder：** 【[
_GitHub传送门_](https://github.com/dievus/Oh365UserFinder)】

