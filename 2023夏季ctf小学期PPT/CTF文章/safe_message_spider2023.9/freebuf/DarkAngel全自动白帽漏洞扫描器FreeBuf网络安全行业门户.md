![image](https://image.3001.net/images/20221215/1671108353_639b1701ebf2de4acdcdb.png!small)

* * *

DarkAngel 是一款全自动白帽漏洞扫描器，从hackerone、bugcrowd资产监听到漏洞报告生成、企业微信通知。

DarkAngel
下载地址：[github.com/Bywalks/DarkAngel](https://github.com/Bywalks/DarkAngel)

当前已支持的功能：

  * hackerone资产监听；

  * bugcrowd资产监听；

  * 自定义资产添加；

  * 子域名扫描；

  * 网站指纹识别；

  * 漏洞扫描；

  * 漏洞报告自动生成；

  * 企业微信通知扫描结果；

  * 前端显示扫描结果；

## 自动生成漏洞报告

自动生成漏洞报告 - MarkDown格式 - 存放地址/root/darkangel/vulscan/results/report

![image](https://image.3001.net/images/20221215/1671108336_639b16f05b6c7b32eeb86.jpg!small)

支持自添加漏洞报告模板，目前已添加漏洞报告模板如下，漏洞名配置为nuclei模板文件名即可

![image](https://image.3001.net/images/20221215/1671108399_639b172fbfd37efbfee17.jpg!small)

自定义漏洞报告模板格式

![image](https://image.3001.net/images/20221215/1671108382_639b171e1639150645b84.jpg!small)

## 企业微信通知

可先查看如何获取配置：[企业微信开发接口文档](https://developer.work.weixin.qq.com/document/path/90487)

获取参数后，在/root/darkangel/vconfig/config.ini中配置参数，即可启用企业微信通知

微信通知 - 漏洞结果

![image](https://image.3001.net/images/20221221/1671625615_63a2fb8fa24f4be00a9ca.png!small)

微信通知 - 扫描进程

![image](https://image.3001.net/images/20221215/1671108431_639b174f4f9a01b486927.png!small)

## 安装

整体项目架构ES+Kibana+扫描器，所以安装需要三个部分

ES镜像：

    
    
    拉取ES镜像
    docker pull bywalkss/darkangel:es7.9.3
    
    部署ES镜像
    docker run -e ES_JAVA_OPTS="-Xms1024m -Xms1024m" -d -p 9200:9200 -p 9300:9300 --name elasticsearch elasticsearch:7.9.3
    
    查看日志
    docker logs -f elasticsearch
    
    出现问题，执行命令
    sysctl -w vm.max_map_count=262144
    
    重启docker
    docker start elasticsearch
    

Kibana镜像：

    
    
    拉取Kibana镜像
    docker pull bywalkss/darkangel:kibana7.9.3
    
    部署Kibana镜像（修改一下es-ip）
    docker run --name kibana -e ELASTICSEARCH_URL=http://es-ip:9200 -p 5601:5601 -d docker.io/bywalkss/darkangel:kibana7.9.3
    
    查看日志
    docker logs -f elasticsearch
    
    出现问题，执行命令
    sysctl -w vm.max_map_count=262144
    
    重启docker
    docker start elasticsearch
    

扫描器镜像：

    
    
    拉取扫描器镜像
    docker pull bywalkss/darkangel:v1
    
    部署扫描器
    docker run -it -d -v /root/darkangel:/root/darkangel --name darkangel bywalkss/darkangel:v1
    

docker容器内挂载目录无权限  
运行容器时：--privileged=true

## 用法

    
    
    usage:  [-h] [--scan-new-domain]
            [--add-domain-and-scan ADD_DOMAIN_AND_SCAN [ADD_DOMAIN_AND_SCAN ...]]
            [--offer-bounty {yes,no}] [--nuclei-file-scan]
            [--nuclei-file-scan-by-new-temp NUCLEI_FILE_SCAN_BY_NEW_TEMP]
            [--nuclei-file-scan-by-new-add-temp NUCLEI_FILE_SCAN_BY_NEW_ADD_TEMP]
            [--nuclei-file-scan-by-temp-name NUCLEI_FILE_SCAN_BY_TEMP_NAME]
            [--nuclei-file-polling-scan] [--delete]
    
    DarkAngel is a white hat scanner. Every user makes the Internet more secure.
    
    --------------------------------------------------------------------------------    
    optional arguments:
      -h, --help            show this help message and exit
      --scan-new-domain     scan new domain from h1 and bc
      --add-domain-and-scan ADD_DOMAIN_AND_SCAN [ADD_DOMAIN_AND_SCAN ...]
                            scan new domain from h1 and bc
      --offer-bounty {yes,no}
                            set add domain is bounty or no bounty
      --nuclei-file-scan    scan new domain from h1 and bc
      --nuclei-file-scan-by-new-temp NUCLEI_FILE_SCAN_BY_NEW_TEMP
                            use new template scan five file by nuclei
      --nuclei-file-scan-by-new-add-temp NUCLEI_FILE_SCAN_BY_NEW_ADD_TEMP
                            add new template scan five file by nuclei
      --nuclei-file-scan-by-temp-name NUCLEI_FILE_SCAN_BY_TEMP_NAME
                            use template scan five file by nuclei
      --nuclei-file-polling-scan
                            five file polling scan by nuclei
    

### \--scan-new-domain

`$ python3 darkangel.py --scan-new-domain`

  * 监听hackerone和bugcrowd域名并进行扫描（第一次使用时会把hackerone和bugcrowd域名全部添加进去，资产过多的情况下做好准备，扫描时间很长）

![image](https://image.3001.net/images/20221215/1671108452_639b1764e3d29d553cc19.jpg!small)

### \--add-domain-and-scan

`$ python3 darkangel.py --add-domain-and-scan program-file-name1 program-file-name2 --offer-bounty yes/no`

  * 自定义添加扫描域名，并对这些域名进行漏洞扫描

  * 文件名为厂商名称，文件内存放需扫描域名

  * 需提供--offer-bounty参数，设置域名是否提供赏金

![image](https://image.3001.net/images/20221215/1671108475_639b177bd77d47c368512.jpg!small)

![image](https://image.3001.net/images/20221215/1671108493_639b178dafb4631554d84.jpg!small)

扫描结束后，会把子域名结果存在在/root/darkangel/vulscan/results/urls目录，按照是否提供赏金分别存放在，bounty_temp_urls_output.txt、nobounty_temp_urls_output.txt文件内

### \--nuclei-file-scan

`$ python3 darkangel.py --nuclei-file-scan`

  * 用nuclei扫描20个url文件

![image](https://image.3001.net/images/20221215/1671108518_639b17a67d25daa8c6fdc.jpg!small)

url列表存放位置

![image](https://image.3001.net/images/20221215/1671108535_639b17b75bc6a5147fcc4.jpg!small)

### \--nuclei-file-polling-scan

`$ python3 darkangel.py --nuclei-file-polling-scan`

  * 轮询用nuclei扫描20个url文件，可把该进程放在后台，轮询扫描，监听是否url列表是否存在新漏洞出现

### \--nuclei-file-scan-by-new-temp

`$ python3 darkangel.py --nuclei-file-scan-by-new-temp nuclei-template-version`

  * 监听nuclei-template更新，当更新时，对url列表进行扫描

当前nuclei-template版本为9.3.1

![image](https://image.3001.net/images/20221215/1671108589_639b17ed90f771afbe75d.jpg!small)

执行命令，监听9.3.2版本更新

![image](https://image.3001.net/images/20221215/1671108604_639b17fc5acefd170eb77.jpg!small)

企业微信通知

![image](https://image.3001.net/images/20221215/1671108613_639b1805da3717b0adbc2.png!small)

url列表存放位置

![image](https://image.3001.net/images/20221215/1671108625_639b18114f23d2d26c770.jpg!small)

### \--nuclei-file-scan-by-new-add-temp

`$ python3 darkangel.py --nuclei-file-scan-by-new-add-temp nuclei-template-id`

  * 监听nuclei单template更新，当更新时，用该template对url列表进行扫描，这里是打了个时间差，某些时候先提交tempalte，验证后才会加入nuclei模板，在还未加入时，我们已经监听并进行扫描，扫描后id会自动增加，监听并进行扫描

查看nuclei单template的id，这里为6296

![image](https://image.3001.net/images/20221215/1671108639_639b181f6954d56119a3a.jpg!small)

执行命令，对该template进行扫描

![image](https://image.3001.net/images/20221215/1671108659_639b1833057ac59c3bf02.jpg!small)

url列表存放位置

![image](https://image.3001.net/images/20221215/1671108674_639b1842089e5754601f8.jpg!small)

### \--nuclei-file-scan-by-temp-name

`$ python3 darkangel.py --nuclei-file-scan-by-temp-name nuclei-template-name`

  * 用单template对url列表进行扫描

![image](https://image.3001.net/images/20221215/1671108758_639b1896435ada280ad76.jpg!small)

## 结果显示

前端 - 扫描厂商

![image](https://image.3001.net/images/20221215/1671108769_639b18a1ab2f3c8a4d112.jpg!small)

前端 - 扫描域名

![image](https://image.3001.net/images/20221215/1671108777_639b18a96072f5bd79481.jpg!small)

前端 - 扫描结果

![image](https://image.3001.net/images/20221215/1671108786_639b18b2888c7815df616.jpg!small)

微信通知 - 扫描进程

![image](https://image.3001.net/images/20221215/1671108798_639b18be39ad058b8d808.png!small)

微信通知 - 漏洞结果

![image](https://image.3001.net/images/20221215/1671108808_639b18c80d477eac593f7.png!small)

## 注意事项

  * 本工具仅用于合法合规用途，严禁用于违法违规用途。

