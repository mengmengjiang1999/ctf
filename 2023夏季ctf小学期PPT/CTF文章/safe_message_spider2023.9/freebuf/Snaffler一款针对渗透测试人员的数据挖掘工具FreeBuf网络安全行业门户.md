## 关于Snaffler

Snaffler是一款专为渗透测试人员设计和开发的数据挖掘工具，可以帮助广大研究人员在一个大规模Windows/AD环境中寻找出有价值的数据。

Snaffler可以从活动目录中获取目标Windows计算机的列表，并将探测Payload发送到所有扫描到的设备上，以确定哪些计算机拥有共享文件，并判断我们是否可以读取这些文件数据。在这个过程中，Snaffler将能够通过智能化的方式找出渗透测试人员所关注的一些有价值的信息。

实际上，如果需要提升数据挖掘的准确率，我们还需要对数据模型进行训练，广大研究人员也可以自行完成这一操作。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/SnaffCon/Snaffler.git

## 工具参数

> -o：将输出结果保存到文件，例如“-o C:\users\thing\snaffler.log”；
>
> -s：将输出结果发送至STDOUT；
>
> -v：控制Verbose模式等级，可选项有Trace、Debug、Info和Data，例如“-v debug”；
>
> -m：给Snaffler分配一个输出目录，工具会将有价值的数据自动拷贝至该目录；
>
> -l：支持的最大文件大小，默认为10000000，大约10MB；
>
> -i：禁用计算机和共享发现，需要提供一个目录路径来执行文件扫描；
>
> -d：需要执行计算机搜索和共享文件搜索的目标域；
>
> -c：查询域计算机列表的域控制器；
>
> -r：搜索数据的最大大小，默认为500k；
>
> -j：有价值数据的上下文数据字节大小，例如“-j 200”；
>
> -z：配置文件的路径，配置文件可涵盖上述所有配置参数，参考配置文件为“.\default.toml”；

## 工具使用

下面给出的样例规则将允许Snaffler忽略包含了指定关键词的所有文件、目录以及子目录：

    
    
    [[Classifiers]]
    
    EnumerationScope = "DirectoryEnumeration"
    
    RuleName = "DiscardFilepathContains"
    
    MatchAction = "Discard"
    
    MatchLocation = "FilePath"
    
    WordListType = "Contains"
    
    WordList = ["winsxs", "syswow64"]
    
    Triage = "Green"

下面的例子中，我们会排除所有的字体、图片、CSS等：

    
    
    [[Classifiers]]
    
    EnumerationScope = "FileEnumeration"
    
    RuleName = "DiscardExtExact"
    
    MatchAction = "Discard"
    
    MatchLocation = "FileExtension"
    
    WordListType = "Exact"
    
    WordList = [".bmp", ".eps", ".gif", ".ico", ".jfi", ".jfif", ".jif", ".jpe", ".jpeg", ".jpg", ".png", ".psd", ".svg", ".tif", ".tiff", ".webp", ".xcf", ".ttf", ".otf", ".lock", ".css", ".less"]

## 工具运行截图

![](https://image.3001.net/images/20220303/1646319244_6220d68cc448e08abe145.png!small)

### 日志文件结构解析

![](https://image.3001.net/images/20220303/1646319261_6220d69d6f33a257bb6f0.png!small)

## 项目地址

 **Snaffler：** 【[ _GitHub传送门_](https://github.com/SnaffCon/Snaffler)】

## 参考资料

> [
> _https://bloodhoundgang.herokuapp.com/_](https://bloodhoundgang.herokuapp.com/)
>
> [ _http://joshstone.us/plunder2/_](http://joshstone.us/plunder2/)
>
> [
> _https://github.com/djhohnstein/SharpShares/_](https://github.com/djhohnstein/SharpShares/)

