![](https://image.3001.net/images/20230421/1682067410_64424fd2e94e861fd9779.png!small)

## 关于S3Scanner

S3Scanner是一款针对S3
Bucket的安全扫描工具，该工具基于Python开发，是一个强大的脚本工具，可以帮助广大研究人员快速扫描和识别不安全的公开S3
Bucket，并转储其中的数据内容。

该工具已在Python 2.7和3.6环境中进行过完整测试。

## 工具下载

由于该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/yehgdotnet/S3Scanner.git

然后切换到项目目录中，使用pip命令和项目提供的requirements.txt来安装该工具所需的依赖组件：

    
    
    cd S3Scanner
    
    pip install -r requirements.txt

## 工具使用

推荐广大研究人员在虚拟环境中使用该工具，虚拟环境的创建和激活命令如下：

    
    
    virtualenv venv && source ./venv/bin/activate

该工具由两个部分组成，即s3finder.py和s3dumper.sh。

### s3finder.py

该脚本可以接受一个域名列表文件作为输入参数，并检测这些域名是否由Amazon
S3托管。工具会将所有找到的S3域名输出到结果文件中，其中包括域名信息和对应的地区region信息，并以“domain:region”的形式存储。

### s3dumper.sh

该脚本支持接收由s3finder.py创建的带有区域的域名列表作为输入参数。针对每一个S3域名，该脚本都会检测其中是否托管了公共可读的S3
Bucket，如果有，则将其转储。

注意，该脚本的正常运行需要使用到[ _aws_
_-cli_](http://docs.aws.amazon.com/cli/latest/userguide/installing.html)。

## 工具使用样例

    
    
    $> python s3finder.py -o output.txt domainsToCheck.txt
    
    
    $> s3dumper.sh output.txt

## 工具运行截图

![](https://image.3001.net/images/20230421/1682067461_644250050eb7af532000f.png!small)![](https://image.3001.net/images/20230421/1682067468_6442500c9d3914ec6a55d.png!small)

  

## 许可证协议

本项目的开发与发布遵循[ _CC BY-NC-SA 4.0_](https://creativecommons.org/licenses/by-nc-sa/4.0/)许可证协议。

## 项目地址

 **S3Scanner** ：【[ _GitHub传送门_](https://github.com/yehgdotnet/S3Scanner)】

## 参考资料

> [
> _http://docs.aws.amazon.com/cli/latest/userguide/installing.html_](http://docs.aws.amazon.com/cli/latest/userguide/installing.html)

