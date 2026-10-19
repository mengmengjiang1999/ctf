![](https://image.3001.net/images/20210428/1619584815_6088e72f392af0bc3eab6.jpg!small)

## 关于VulnerableCode

VulnerableCode是一个免费的开放FOSS软件包漏洞数据库，并且还包含了能够创建并跟踪当前数据的相关工具。在该工具的帮助下，广大研究人员能够查看受漏洞影响的代码包，并实现漏洞的聚合、关联和管理。

FOSS，即Free and Open Source
Software，这是联合国教科文组织启用的一个官方术语。“FOSS产业”是有新意的，严格讲来，它不完全等同于“开源产业”。FOSS把现代软件业带入一个全新阶段。“FOSS”的中译文是“自由及开源软件”。

VulnerableCode是FOSS社区开发的一款工具，它能够提升开源软件生态系统的安全性。

## 运行机制

VulnerableCode独立地聚合了许多软件漏洞数据源，并以去中心化的方式支持数据重新创建。这些数据源包括Linux和BSD发行版发布的安全建议、应用程序软件包管理器和包存储库、FOSS项目、GitHub等等。由于这种方法，数据集中在特定的生态系统上，但在单个数据库中进行聚合，从而能够查询代码包之间更丰富的关系图。特定性提高了数据的准确性和有效性，因为跨不同生态系统的同一版本上游数据包可能会或可能不会受到同一漏洞的影响。

工具使用了Package URL PURL来作为主要标识符，而没有使用CPE。VulnerableCode对数据的主要访问是通过REST API进行的。

此外，工具还提供了一个高级的Web界面来帮助用户更好地浏览和搜索漏洞数据库，并通过添加新的包和漏洞逐步实现数据的社区管理，以及审查和更新它们的关系。

## 工具安装&配置

我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/nexB/vulnerablecode.git
    
    cd vulnerablecode

### 使用Docker Compose

安装VulnerableCode最简单的方法就是使用Docker容器和Docker Compose。安装好Docker引擎和Docker
Compose之后，我们就可以使用下列命令来启动VulnerableCode了：

    
    
    sudo docker-compose up

接下来，通过下列地址即可访问VulnerableCode：

    
    
    http://localhost:8000/
    
    http://127.0.0.1:8000/

别忘了运行虾类命令来在每一次git pull之后同步你的实例：

    
    
    sudo docker-compose up -d --no-deps --build web

然后，我们可以使用下列命令来访问VulnerableCode容器，这里我们可以访问manage.py，并运行管理命令来导入数据：

    
    
    sudo docker-compose exec web bash

### 本地安装

系统要求：

> Python 3.8+
>
> PostgreSQL 9+
>
> 针对Python和PostgreSQL的编译工具链和开发文件

在基于Debian的发行版系统上，可以使用下列下列命令安装和配置VulnerableCode：

    
    
    sudo apt-get install python3-venv python3-dev postgresql libpq-dev build-essential
    
    sudo -u postgres createuser --no-createrole --no-superuser --login \
    
    --inherit --createdb --pwprompt vulnerablecode``
    
    createdb --encoding=utf-8 --owner=vulnerablecode  --user=vulnerablecode \
    
    --password --host=localhost --port=5432 vulnerablecode
    
    python3 -m venv venv
    
    source venv/bin/activate
    
    pip install -r requirements.txt
    
    DJANGO_DEV=1 python manage.py collectstatic
    
    DJANGO_DEV=1 python manage.py migrate

## 运行测试

下列命令可以运行代码风格检测和测试用例：

    
    
    black -l 100 --check .
    
    DJANGO_DEV=1 python -m pytest

## 数据导入

某些数据导入工具使用了GitHub API，首先我们需要使用下列命令导出GH_TOKEN环境变量：

    
    
    export GH_TOKEN=yourgithubtoken

运行所有的数据导入器：

    
    
    DJANGO_DEV=1 python manage.py import --all

枚举所有可用的导入器：

    
    
    DJANGO_DEV=1 python manage.py import --list

运行指定导入器：

    
    
    DJANGO_DEV=1 python manage.py import rust npm

## REST API访问

开启Web服务器：

    
    
    DJANGO_DEV=1 python manage.py runserver

获取关于API节点的完整文档：

    
    
    http://127.0.0.1:8000/api/docs

## 连续定期数据导入

如果你想要持续定期导入数据，你可以使用一个系统定时器：

    
    
    $ cat ~/.config/systemd/user/vulnerablecode.service
    
     
    
    [Unit]
    
    Description=Update vulnerability database
    
     
    
    [Service]
    
    Type=oneshot
    
    Environment="DJANGO_DEV=1"
    
    ExecStart=/path/to/venv/bin/python /path/to/vulnerablecode/manage.py import --all
    
     
    
    $ cat ~/.config/systemd/user/vulnerablecode.timer
    
     
    
    [Unit]
    
    Description=Periodically update vulnerability database
    
     
    
    [Timer]
    
    OnCalendar=daily
    
     
    
    [Install]
    
    WantedBy=multi-user.target

配置好之后，你就可以使用下列命令来开启这个定时器：

    
    
    systemctl --user daemon-reload
    
    systemctl --user start vulnerablecode.timer

## 项目地址

 **VulnerableCode：** https://github.com/nexB/vulnerablecode

## 参考资料

https://nvd.nist.gov/products/cpe

https://github.com/nexB/vulnerablecode/blob/main/SOURCES.rst

https://github.com/package-url/purl-spec

https://github.com/nexB/vulnerablecode/blob/main/docs/Why-Is-There-No-Free-Software-Vulnerability-Database-v1.0.pdf

https://docs.docker.com/get-docker/

https://docs.docker.com/compose/install/#install-compose

https://nixos.org/download.html

https://github.com/DavHau/mach-nix

https://github.com/DavHau/pypi-deps-db

https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token

