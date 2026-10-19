![](https://image.3001.net/images/20201205/1607162992_5fcb5c70039bc49762e9a.jpg!small)

## PatchChecker

PatchChecker是一款基于Web的Windows漏洞检测工具，该项目代码目前以网络服务的形式托管在https://patchchecker.com上。简而言之，PatchChecker是一个基于Flask实现的Web应用程序，它所提供的输出内容类似于Watson。但是，通过使用PatchChecker，我们将不需要在目标计算机上执行二进制文件。除此之外，该项目还提供了一个Web爬虫，它可以使用Microsoft站点上的信息自动更新PatchChecker的数据库，这样不仅可以帮助我们以最快最简单的方式找出目标Windows系统中安装（或未安装）补丁的CVE漏洞问题，而且还提供了一个更具可伸缩性和更易于使用的解决方案。当然了，其他任何的CVE漏洞信息都可以添加到数据采集器输入中，并且只要它们在https://portal.msrc.microsoft.com上存在有一个条目就可以进行CVE检查了。更重要的是，我们也可以使用PatchChecker提供的信息来更新Watson。

## 如何使用PatchChecker来检测Windows漏洞

在PatchChecker的帮助下，我们可以直接访问公开托管PatchChecker的【[
_站点_](https://patchchecker.com/)】，或者使用下列命令将该项目源码克隆至本地，然后安装相应的依赖库：

    
    
    git clone https://github.com/deadjakk/patch-checker.git

此时，我们还需要确保patches.db跟app.py存储在同一目录下，然后使用下列命令开启应用程序：

    
    
    python3 ./app.py

应用程序启动之后，我们可以在浏览器中打开项目文件中的index.html文件，此时浏览器将会激活PatchChecker服务，并获取目标系统中存在安全问题的补丁或者CVE漏洞。

### 获取KB数据：

![](https://image.3001.net/images/20201205/1607163024_5fcb5c9084aa8e3d1b56e.png!small)

### 期望的输入：

![](https://image.3001.net/images/20201205/1607163037_5fcb5c9d80430e2ed009a.png!small)

### 期望的web页面输出：

![](https://image.3001.net/images/20201205/1607163044_5fcb5ca45f910a7124edb.png!small)

### 找到漏洞后，期望的Web页面输出：

![](https://image.3001.net/images/20201205/1607163053_5fcb5cad80da8b5a3dfd2.png!small)

或者说，我们也可以使用一个curl命令并发送类似如下请求来实现相同的效果。

### 请求：

    
    
    curl 'https://patchchecker.com/checkprivs/' --data-raw 'wmicinfo=KB1231411 KB1231441 KB1234141&build_num=17763'

### 响应：

    
    
    {
    
        "total_vuln": 9,
    
        "kbs_parsed": [
    
            "KB1231411",
    
            "KB1231441",
    
            "KB1234141"
    
        ],
    
        "total_kbs_parsed": 3,
    
        "build": "17763",
    
        "results": [
    
            {
    
                "refs": [
    
                    "https://exploit-db.com/exploits/46718",
    
                    "https://decoder.cloud/2019/04/29/combinig-luafv-postluafvpostreadwrite-race-condition-pe-with-diaghub-collector-exploit-from-standard-user-to-system/"
    
                ],
    
                "name": "CVE-2019-0836",
    
                "vulnerable": true
    
            }
    
    ]
    
    }

如果你想要在本地运行该工具的话，别忘了在克隆好项目代码之后运行下列命令来配置依赖组件（支持Python 3.7.3）：

    
    
    python3 -m pip install -r requirements.txt

## 数据收集：patchdata_collector.py

patchdata_collector.py脚本是一个pyppeteer爬虫，它可以遍历多个微软站点来获取--cve-list参数文件中指定的CVE漏洞信息。大家可以查看项目samples目录中的cves.txt文件格式来了解如何提供输入数据，其中每一行包含一条数据，数据格式如下：

    
    
    CVE-XXXX-XXXX|https://website.com/resource-pertaining-to-CVE,http://second_resource.com

在时间上，如果提供数据包含9个CVE漏洞条目，则大约需要11分钟来完成任务。

### patchdata_collector.py使用：

    
    
    usage: patchdata_collector.py [-h] --cve-list CVE_LIST [--db DB] [--new-db] [-v]
    
                              [-vv] [--no-headless] [--json JSON]
    
     
    
    optional arguments:
    
      -h, --help           show this help message and exit
    
      --cve-list CVE_LIST  line and pipe separated list containing CVEs and
    
                           related-URLs with information example: CVE-2020-1048|https://github.com/ionescu007/faxhell,https://github.com/ionescu007/PrintDemon
    
      --db DB              sqlite database filename
    
      --new-db             erases old database (if exists)
    
      -v                   set output to debug (verbose)
    
      -vv                  set output to annoying
    
      --no-headless        run browser with headless mode disabled
    
      --json JSON          json format output, argument should be json filename

## 运行样例

首先，我们需要运行下列命令：

    
    
    time ./patchdata_collector.py --cve-list cves.txt --db antest.db --new-db

命令执行后的输出结果如下：

    
    
    2020-06-05 20:38:49.292 | INFO     | __main__:main:181 - Loaded 10 CVEs
    
    2020-06-05 20:38:49.430 | INFO     | __main__:parsekb:33 - Parsing KBs for: CVE-2019-0836
    
    2020-06-05 20:40:27.183 | INFO     | __main__:parsekb:33 - Parsing KBs for: CVE-2019-1064
    
    2020-06-05 20:41:07.158 | INFO     | __main__:parsekb:33 - Parsing KBs for: CVE-2019-0841
    
    2020-06-05 20:41:31.675 | INFO     | __main__:parsekb:33 - Parsing KBs for: CVE-2019-1130
    
    2020-06-05 20:42:58.527 | INFO     | __main__:parsekb:33 - Parsing KBs for: CVE-2019-1253
    
    2020-06-05 20:43:25.069 | INFO     | __main__:parsekb:33 - Parsing KBs for: CVE-2019-1315
    
    2020-06-05 20:44:57.974 | INFO     | __main__:parsekb:33 - Parsing KBs for: CVE-2019-1385
    
    2020-06-05 20:45:22.026 | INFO     | __main__:parsekb:33 - Parsing KBs for: CVE-2019-1388
    
    2020-06-05 20:46:48.407 | INFO     | __main__:parsekb:33 - Parsing KBs for: CVE-2019-1405
    
    2020-06-05 20:48:07.026 | INFO     | __main__:parsekb:33 - Parsing KBs for: CVE-2020-1048
    
    finished
    
     
    
    real 11m27.793s
    
    user 1m21.632s
    
    sys 0m14.559s

## 项目地址

PatchChecker：【[ _GitHub传送门_](https://github.com/deadjakk/patch-checker)】

## 参考资料

> [
> _https://deadjakk.github.io/find_privesc_nobinary.html﻿_](https://deadjakk.github.io/find_privesc_nobinary.html)

  

