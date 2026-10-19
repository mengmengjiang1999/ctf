![](https://image.3001.net/images/20211008/1633675835_615fea3bb5668dc7a057a.png!small)

## 关于ODBParser

ODBParser是一款公开资源情报工具，可以帮助广大研究人员从Elasticsearch和MongoDB目录中搜索、解析并导出我们感兴趣的数据。除此之外，这款工具还可以帮助广大研究人员从开放数据库中搜索出曝光的个人可标识信息(PII)。

ODBParser的主要目标是创建一个一站式公开资源情报工具，用于搜索、解析和分析开放数据库，以便识别第三方服务器上的PII泄漏。

## 功能介绍

### 识别开放数据库

> 使用所有可行的参数查询Shodan和BinaryEdge，可通过国家、端口号和其他内容过滤查询结果；
>
> 指定单个IP地址；
>
> 加载IP地址列表文件；
>
> 从剪贴板粘贴IP地址列表；

导出选项

> 解析所有的数据库/集合来识别指定的数据；
>
> 获取目标服务器中托管的所有数据；
>
> 获取集合/索引数据；
>
> 使用Ctrl + C跳过特定索引；

### 后渗透处理

> 将JSON导出数据转换为CSV；
>
> 从CSV中移除特定的列；

### 其他功能

> 跟踪查询的所有IP地址和数据库以及有关每个服务器的信息；
>
> 对于每个记录总数超过限制的数据库，脚本将在一个特殊文件中创建一个条目以及5个示例记录，以便你可以查看并决定数据库是否值得抓取；
>
> 默认输出是行分隔的JSON文件，每行上有一个JSON对象。你可以使用“properjson”标志选择让它输出一个“适当的JSON”文件；

## 工具安装

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/citcheese/ODBParser.git

接下来，我们需要自行获取Shodan和BinaryEdge的API密钥，并在ODBconfig.py文件中配置相应的参数。

最后，根据项目目录中的requirements.txt安装并配置该工具所需的依赖组件。

我建议广大研究人员创建一个ODBParser的虚拟环境，该工具目前尽在Windows 10（Python 3.7.3）环境中进行过测试。

## 工具使用

    
    
    Examples: python ODBParser.py -cn US -p 8080 -t users --elastic --shodan --csv --limit 100
                  python ODBParser.py -ip 192.168.2:8080 --mongo --ignorelogs --nosizelimits
        Damage to-date: 0 servers parsed | 0 databases dumped | 0 records pulled
    
        _____________________________________________________________________________
    optional arguments:
    
      -h, --help            show this help message and exit
    
    Query Options:
    
      --shodan, -sh         Add this flag if using Shodan. Specify ES or MDB w/
                            flags.
      --binary, -be         Add this flag if using BinaryEdge. Specify ES or MDB
                            w/ flags.
    
      --ip , -ip            Query one server. Add port like so '192.165.2.1:8080'
    
                            or will use default ports for each db type. Add ES or
    
                            MDB flags to specify parser.
    
      --file , -f           Load line-separated IPs from file. Add port or will
    
                            assume default ports for each db type. Add ES or MDB
    
                            flags to specify parser.
    
      --paste, -v           Query line-separated IPs from clipboard. Add port or
    
                            will assume default ports for each db type, e.g. 9200
    
                            for ES. Add ES or MDB flags to specify parser.
    
    Shodan/BinaryEdge Options:
    
      --limit , -l          Max number of results per query. Default is
    
                            500.
    
      --port , -p           Filter by port.
    
      --country , -cn       Filter by country (two-letter country code).
    
      --terms , -t          Enter any additional query terms you want here, e.g.
                            'users'
    Dump Options:
    
      --mongo, -mdb         Use for IP, Shodan, BinaryEdge & Paste methods to
    
                            specify parser.
    
      --elastic, -es        Use for IP, Shodan, BinaryEdge & Paste methods to
    
                            specify parser.
    
      --properjson, -pj     Add this flag if would like out put to be proper JSON
    
                            file. Default is one JSON string object per line.
    
      --database , -db      Specify database you want to grab. For MDB must be in
    
                            format format 'db:collection'. Use with IP arg & 'es'
    
                            or 'mdb' flag
    
      --getall, -g          Get all indices regardless of fields and
    
                            collection/index names (overrides selections in config
    
                            file).
    
      --ignorelogs          Connect to a server you've already checked out.
    
      --nosizelimits, -n    Dump index no matter how big it is. Default max doc
    
                            count is 800,000.
    
      --csv                 Convert JSON dumps into CSV format on the fly. (Puts
    
                            JSON files in backup folder in case there is issue
    
                            with coversion)
    
     
    
    CSV/Post-processing Options:
    
      --convertToCSV , -c   Convert JSON file or folder of JSON dumps to CSVs
    
                            after the fact. Enter full path or folder name in
    
                            current working directory
    
      --dontflatten         Use if run into memory issues converting JSON files to
    
                            CSV during post-processing.
    
      --basic               Use with --convertToCSV flag if your JSON dumps are
    
                            not true JSON files, but rather line separated JSON
    
                            objects that you got from other sources.
    
      --dontclean, -dc      Choose if want to keep useless data when convert to
    
                            CSV. See docs for more info.

## 项目地址

 **ODBParser：** 【[ _GitHub传送门_](https://github.com/citcheese/ODBParser)】

