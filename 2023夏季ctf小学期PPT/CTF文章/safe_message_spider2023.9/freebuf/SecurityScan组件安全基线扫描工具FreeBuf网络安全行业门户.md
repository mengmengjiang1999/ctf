## 痛点

  1. 安全形势严峻、客户安全关注度逐步提高

公司众多项目对安全要求逐步增高，现场对主机操作系统安全配置、中间、数据库等各类组件提出了各类基线安全需求

  2. 现场组件类型多问题广泛、暴露面多

从IaaS到PaaS再到SaaS层，涉及组件及应用广泛，缺乏统一的管控，问题暴露后缺乏有效的解决机制。随着云原生技术的应用，除了需满足传统安全组件操作系统的安全扫描还需要对docker及K8S等进行安管控

  3. 安全扫描整改费时费力

对于各类组件的安全配置扫描检测及修复，需要各个项目现场及安全专业人员配合，周期长，成效不显著，且扫描后无可视化结果进行审计和分析

## 需求分析

基于DevSecOps实践的思想，我们可以考虑利用开源的安全工具实现安全扫描自动化

为此我们以合规配置自动化扫描的痛点为例，基于chef inspec扫描框架，定制自动化扫描工具security_scan将
IaC（基础设置即代码）思想在实际项目中落地

  1. 扫描基线覆盖绝大多组件及操作系统：比如CIS数据库配置、各类中间件组件安全配置以及docker、k8S，系统安全配置例如linux安全基线扫描

![1638430804_61a87854e704361820a33.png!small?1638430806603](https://image.3001.net/images/20211202/1638430804_61a87854e704361820a33.png!small?1638430806603)

  2. 自动触发扫描：执行python脚本即可自动触发扫描，无需了解组件及工具的具体技术原理
  3. 支持批量扫描：可以通过配置文档方式读入扫描主机ip端口等信息即可批量执行
  4. 输出html/json报告：扫描结果支持html导出，便于分析统计
  5. 支持报告结果统计分析：对于多台主机或多组件扫描结果，可利用Heimdall server，直接导入扫描结果，生成分析报表

## 扫描效果

自动触发扫描

![](https://image.3001.net/images/20211202/1638430986_61a8790aeb1d584345c0d.gif!small)

生成扫描结果![](https://image.3001.net/images/20211202/1638431885_61a87c8dd6664e313f7c2.png!small)

可视化报告结果分析

![1638430289_61a87651ecb64844aef6b.png!small?1638430291781](https://image.3001.net/images/20211202/1638430289_61a87651ecb64844aef6b.png!small?1638430291781)

## 使用方式

### 环境部署

##

  1. inspec环境配置

    
    
    curl https://omnitruck.chef.io/install.sh | sudo bash -s -- -P inspec

  2. python环境配置（若已安装请忽略）

    
    
    wget https://www.python.org/ftp/python/3.8.6/Python-3.8.6.tgz
    tar -xvJf  Python-3.8.6.tgz
    mv Python-3.8.6 /usr/local/python3
    cd /usr/local/python3
    ./configure --prefix=/usr/local/python3 
    make && make install
    ln -s /usr/local/python3/bin/python3 /us/bin/python3
    ln -s /usr/local/python3/bin/pip3 /us/bin/pip3
    pip3 install prompt_toolkit

### 工具扫描

##

  1. 工具部署

    
    
    git clone https://github.com/JalinZhang/Security_Scan.git

  2. 参数说明

    
    
    Scanner:
      -i IP        target host ip address  #指定IP
      -p PORT      target address ssh port  #端口
      -u USER      target host ssh user #用户
      -d PASSWORD  target user ssh password  #密码
      -f FILE      target hosts list file name  #执行批量扫描配置文件  
      
    

  3. 执行扫描

指定IP扫描（ip/端口/用户名/密码）

![1638425826_61a864e2d54d999879ceb.png!small?1638425828404](https://image.3001.net/images/20211202/1638425826_61a864e2d54d999879ceb.png!small?1638425828404)

![1638426001_61a86591d159fae2c57e7.png!small?1638426003492](https://image.3001.net/images/20211202/1638426001_61a86591d159fae2c57e7.png!small?1638426003492)

批量扫描

编辑target.txt文件，输入批量扫描主机信息
**（工具暂未实现passwd加密，为避免配置信息泄露，请勿报错配置文件，并在扫描后删除）**![1638430073_61a87579b0aa0faf8f256.png!small?1638430075388](https://image.3001.net/images/20211202/1638430073_61a87579b0aa0faf8f256.png!small?1638430075388)

  

  4. 查看扫描结果，结果默认存放/tmp/scan_result文件夹

    
    
    cd /tmp/scan_result/
    (venv)[/tmp/scan_result]# ll
    drwxr-xr-x  html
    drwxr-xr-x  json

## 报告展示

##

检测生成的报告可以使用开源web server进行解析生成可视化报表

![1638430289_61a87651ecb64844aef6b.png!small?1638430291781](https://image.3001.net/images/20211202/1638430289_61a87651ecb64844aef6b.png!small?1638430291781)

MITRE Heimdall Viewer 有两个版本——完整的 Heimdall Enterprise Server 和 Heimdall-Lite
版本。两者共享相同的前端，但都是为了满足不同的需求和用例而生产的。​

### Heimdall Light

###

适用于单节点少量报告查看和检测，只支持手动导入

<https://heimdall-lite.mitre.org/>

### Heimdall server

###

适用于多台主机报告查看和检测，可通过扫描工具导入，也可手动导入报告

鉴于 Heimdall server至少需要一个数据库服务，我们使用 Docker 和 Docker Compose 来提供简单的部署​：

设置 Docker 容器

###

  1. 安装 Docker
  2. 下载Heimdall压缩包至本地并解压[heimdall2-master.zip](https://sipc.yuque.com/attachments/yuque/0/2021/zip/399728/1627014345774-76f89a95-fd15-4e37-8f86-b17dcc748076.zip?_lake_card=%7B%22src%22%3A%22https%3A%2F%2Fsipc.yuque.com%2Fattachments%2Fyuque%2F0%2F2021%2Fzip%2F399728%2F1627014345774-76f89a95-fd15-4e37-8f86-b17dcc748076.zip%22%2C%22name%22%3A%22heimdall2-master.zip%22%2C%22size%22%3A24128017%2C%22type%22%3A%22application%2Fx-zip-compressed%22%2C%22ext%22%3A%22zip%22%2C%22status%22%3A%22done%22%2C%22taskId%22%3A%22u4c16c4da-0c74-4b63-8222-024d6ffd988%22%2C%22taskType%22%3A%22upload%22%2C%22id%22%3A%22u8cada9d9%22%2C%22card%22%3A%22file%22%7D)
  3. 导航到docker-compose.yml所在的基本文件夹/heimdall2-master
  4. 默认情况下，Heimdall 将生成自签名证书，有效期为 7 天。将您的证书文件分别放入/heimdall2-master/nginx/certs/文件下，文件名分别为ssl_certificate.crt和ssl_certificate_key.key。
  5. 在 Heimdall 源目录/heimdall2-master/的终端窗口中运行以下命令

    
    
    [/root/heimdall2-master]# ./setup-docker-secrets.sh  #如果你想进一步配置你的 Heimdall 实例，编辑运行上一行后生成的 .env 文件
    [/root/heimdall2-master]# docker  -compose up -d

有关 .env
文件的更多信息，请访问[环境变量配置。](https://github.com/mitre/heimdall2/wiki/Environment-Variables-Configuration)默认端口映射为"3000:3000"，若需要修改端口映射，在docker-compose.yml中修改

  6. 导航到 [http://ipaddress:3000﻿](http://127.0.0.1:3000/)

## 工具参考与致谢

[DevSec Hardening Framework](https://dev-sec.io/)

[WeblogicScan](https://github.com/rabbitmask/WeblogicScan)

[Chef InSpec](https://www.chef.io/products/chef-inspec)

[mitre/heimdall2](https://github.com/mitre/heimdall2)

  

