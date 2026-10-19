![](https://image.3001.net/images/20200810/1596997920.jpg!small)

## PhishingKitTracker

PhishingKitTracker是一款功能强大的钓鱼活动跟踪工具包，该工具是一个可扩展的，并且集成了大量最新钓鱼攻击的工具集，可支持广大研究人员的数据分析和取证工作，而且还能够提供简单的统计信息。

PhishingKitTracker这个项目中包含了大量网络钓鱼工具，很多网络犯罪分子都会利用这些工具来窃取用户的信息。该项目的raw目录中存储的内容都是恶意工具，请不要将其用于恶意目的。除此之外，PhishingKitTracker存储在Git大文件系统（git-lfs）中以实现大数据追踪，因此在克隆该项目之前，请先安装[ _git-lfs_](https://git-lfs.github.com/)。

## 工具下载

在使用PhishingKitTracker之前，请先确保[ _git-lfs_](https://git-lfs.github.com/)以正常安装。广大研究人员在配置好git-lfs之后，可以使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/marcoramilli/PhishingKitTracker.git

## 原始数据

该项目的raw目录中包含的是最新的网络钓鱼工具的原始版本，我们并没有对其中的数据进行修改。工具的后台脚本会持续不断地遍历公共资源网站以收集其中托管的网络钓鱼工具，并且会将扫描到的网络钓鱼工具下载到raw文件夹中。由于很多工具的大小都超过了100MB，因此该项目才会选择使用Git大文件系统来进行托管。

**下图显示的是该项目中的部分网络钓鱼工具列表：**![](https://image.3001.net/images/20200810/1596997936.png!small)

## 统计信息

Stats目录里中包含了两个持续更新的文件：

1、files_name文件中包含了扫描到的钓鱼工具文件名之间的相关率，以实现对网络钓鱼工具真实性进行验证。

2、sites文件中包含了托管目标钓鱼工具的域名出现频率，即保存了钓鱼工具的托管域名。如果跟踪的钓鱼工具没有重复，则频率和文件名都是唯一的。比如说“3
li.humanbiomics-project.org”，它意味着工具已经在“li.humanbiomics-project.org”上找到了三款不同的网络钓鱼工具了。这些文件是由下列bash脚本生成的：

    
    
    ls raw/ | cut -d'_' -f1 | uniq -c | sort -bgr > stats/sites.txt
    
    ls raw/ | cut -d'_' -f2 | uniq -c | sort -bgr > stats/files_name.txt

## SIMILARITY.CSV结构

SIMILARITY.CSV文件的相似性结构数据包含FileA、FileB、SimilarityAVG、SimilarityMin和SimilarityMax。其中：

> FileA：待分析的钓鱼工具文件。
>
> FileB：需要跟FileA进行对比的钓鱼工具文件。
>
> SimilarityAVG：SimilarityAVG是相似性的平均值，这个平均值是通过将FileA中的每个文件与FileB中的每个文件对比计算得出的。
>
> SimilarityMin：SimilarityMin是PhishingKitA和PhishingKitB之间的最低相似度值。
>
> SimilarityMax：SimilarityMax是PhishingKitA和PhishingKitB之间的最大相似度值。

如果你想要自行生成SIMILARITY.CSV，我们还在src目录中提供了一个简单的脚本来帮助实现。

## src文件配置

广大研究人员可以根据自己的需求来修改compute_similarity.py文件中的变量：

    
    
    EXTENSION_FOR_ANALYSIS = ['.html','.js','.vbs','.xls','.xlsm','.doc','.docm', '.ps1']
    
    OUTPUT_FILE =  'similarity.csv'                                                 
    
    RAW_FOLDER = '/tmp/raw/'                                                        
    
    TEMP_FOLDER = '/tmp/tt'     

当研究人员修改了脚本运行参数之后，该工具将会切换至RAW_FOLDER目录下，获取.zip文件，并计算两个文件的代码相似度。处理完成后，该工具会将分析结果存储至OUTPUT_FILE中。接下来，我们就可以将其以文件的形式导入到其他的电子表格处理工具中，并显示代码的相似度分析结果。

目前，PhishingKitTracker只能支持进行zip文件对比。

## 项目地址

PhishingKitTracker：【[
_GitHub传送门_](https://github.com/marcoramilli/PhishingKitTracker)】

