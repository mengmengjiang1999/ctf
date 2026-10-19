![](https://image.3001.net/images/20210925/1632517275_614e3c9bbab3f2805d182.png!small)

## 关于MobileAudit

> MobileAudit是一款Django Web应用程序，该工具可以帮助广大研究人员针对Android
> APK执行静态分析和恶意软件检测。![](https://image.3001.net/images/20210925/1632517285_614e3ca50a428b6b51319.png!small)
>
> 在每一次扫描中，我们将获取到下列信息：
>
> 应用程序信息
>
> 安全信息
>
> 组件
>
> 安全分析结果
>
> 最佳实践方案
>
> VirusTotal信息
>
> 证书信息
>
> 字符串信息
>
> 数据库信息
>
> 文件

![](https://image.3001.net/images/20210925/1632517292_614e3cac39b772581b744.png!small)

为了方便广大研究人员使用，MobileAudit扫描界面的左侧提供了一个侧边栏：

![](https://image.3001.net/images/20210925/1632517299_614e3cb3c676a6e6d5f48.png!small)

## 工具组件

![](https://image.3001.net/images/20210925/1632517309_614e3cbd39ed462bbf82c.png!small)

## 工具安装

使用Docker-compose：

项目提供的docker-compose.yml文件允许我们直接以开发模式在本地运行应用程序。

接下来，构建本地镜像，如果本地应用程序Dockerfile有修改的话，你可以重新构建镜像：

    
    
    docker-compose build

然后开启容器：

    
    
    docker-compose up

应用程序启动之后，你就可以通过访问http://localhost:8888/来使用工具仪表盘，并开始进行测试了。

![](https://image.3001.net/images/20210925/1632517336_614e3cd8cbc461c38ddd4.png!small)

该工具还有一个TLS版本，可通过下列命令来执行：

    
    
    docker-compose -f docker-compose.prod.yaml up

此时，你就可以通过访问http://localhost:8888/来使用工具仪表盘，并开始进行测试了。

如需终止或移除容器，可以运行下列命令：

    
    
    docker-compose down

## TLS

### 预配置

在nginx/ssl中添加证书；

生成自签名证书：

    
    
    openssl req -x509 -nodes -days 1 -newkey rsa:4096 -subj "/C=ES/ST=Madrid/L=Madrid/O=Example/OU=IT/CN=localhost" -keyout nginx/ssl/nginx.key -out nginx/ssl/nginx.crt

### Nginx配置

TLS--端口443：nginx/app_tls.conf

标准：端口8888：nginx/app.conf

### Docker配置

默认配置下，docker-compose.yml中有一个卷，配置为端口8888：

    
    
    - ./nginx/app.conf:/etc/nginx/conf.d/app.conf

在生产环境中，我们需要使用docker-compose.prod.yaml（端口433）：

    
    
    - ./nginx/app_tls.conf:/etc/nginx/conf.d/app_tls.conf

## 环境变量

该工具所有的环境变量都存储在一个.env文件中，并且在.env.example文件中提供了所有需要的变量信息：

    
    
    CWE_URL = env('CWE_URL', 'https://cwe.mitre.org/data/definitions/')
    
     
    
    MALWARE_ENABLED = env('MALWARE_ENABLED', True)
    
    MALWAREDB_URL = env('MALWAREDB_URL', 'https://www.malwaredomainlist.com/mdlcsv.php')
    
    MALTRAILDB_URL = env('MALTRAILDB_URL', 'https://raw.githubusercontent.com/stamparm/aux/master/maltrail-malware-domains.txt')
    
     
    
    VIRUSTOTAL_ENABLED = env('VIRUSTOTAL_ENABLED', False)
    
    VIRUSTOTAL_URL = env('VIRUSTOTAL_URL', 'https://www.virustotal.com/')
    
    VIRUSTOTAL_FILE_URL = env('VIRUSTOTAL_FILE_URL', 'https://www.virustotal.com/gui/file/')
    
    VIRUSTOTAL_API_URL_V3 = env('VIRUSTOTAL_API_URL_V3', 'https://www.virustotal.com/api/v3/')
    
    VIRUSTOTAL_URL_V2 = env('VIRUSTOTAL_API_URL_V2', 'https://www.virustotal.com/vtapi/v2/file/')
    
    VIRUSTOTAL_API_KEY = env('VIRUSTOTAL_API_KEY', '')
    
    VIRUSTOTAL_UPLOAD = env('VIRUSTOTAL_UPLOAD', False)
    
     
    
    DEFECTDOJO_ENABLED = env('DEFECTDOJO_ENABLED', False)
    
    DEFECTDOJO_URL = env('DEFECTDOJO_URL', 'http://defectdojo:8080/finding/')
    
    DEFECTDOJO_API_URL = env('DEFECTDOJO_API_URL', 'http://defectdojo:8080/api/v2/')
    
    DEFECTDOJO_API_KEY = env('DEFECTDOJO_API_KEY', '')

## 项目地址

 **MobileAudit：** 【[ _GitHub传送门_](https://github.com/mpast/mobileAudit)】

