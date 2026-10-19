![](https://image.3001.net/images/20210904/1630760813_61336f6dece58cc48f5e5.jpg!small)

## 关于tsharkVM

tsharkVM这个项目旨在构建一台虚拟机，以帮助广大研究人员分析tshark的输出结果。虚拟设备是使用vagrant构建的，它可以使用预安装和预配置的ELK堆栈构建Debian
10。

 **虚拟机启动之后，整个执行流程相对比较简单：**

> 解码pcap文件（tshark -T ek output / ndjson），该文件会通过“TCP/17570”发送至虚拟机；
>
> 虚拟机中的ELK堆栈将会处理并索引数据；
>
> Kibana会在虚拟机中运行，可以通过“http://127.0.0.1:15601/app/kibana#/dashboards”访问；

## 工具安装-如何在Ubuntu桌面系统上构建虚拟机

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/H21lab/tsharkVM.git

接下来，使用下列命令构建tsharkVM：

    
    
    sudo apt update
    
    sudo apt install tshark virtualbox vagrant
    
    vagrant plugin install vagrant-disksize
    
    vagrant plugin install vagrant-scp
    
    bash ./build.sh

然后，下列命令可以将pcap文件上传至虚拟机：

    
    
    # 复制pcap文件至./Trace
    # 上传pcap文件（含文件名）
    bash upload_pcaps_with_filenames.sh
    # 或者使用“vagrant scp”将ndjson文件拷贝至/home/vagrant/inpu
    # 或者直接上传pcap文件（无文件名）
    bash upload_pcaps.sh 
    # 或者直接使用tshark转发至127.0.0.1 17570/tcp
    tshark -r trace.pcapng -x -T ek > /dev/tcp/localhost/17570

使用浏览器打开Kibana：

    
    
    firefox http://127.0.0.1:15601/app/kibana#/dashboards

打开程序主仪表盘后，就可以查看到这些pcap文件了。

## 工具使用

### SSH连接到虚拟机

    
    
    cd ./VM
    
    vagrant ssh

### 删除虚拟机

    
    
    cd ./VM
    
    vagrant destroy default

### 开启虚拟机

    
    
    cd ./VM
    
    vagrant up

### 挂起虚拟机

    
    
    cd ./VM
    
    vagrant halt

### SSH连接至虚拟机并检测ELK是否正常运行

    
    
    cd ./VM
    
    vagrant ssh
    
    sudo systemctl status kibana.service
    
    sudo systemctl status elasticsearch.service
    
    sudo systemctl status logstash.service

## Elasticsearch映射模板

这个项目还给大家提供了简单的Elasticsearch映射模板，主要针对的是frame、eth、ip、udp、tcp、dhcp协议。如需处理其他额外的协议，我们可以根据自己的需要并以下列方式映射模板：

    
    
    # 1. 创建自定义映射，选择所需的协议
    tshark -G elastic-mapping --elastic-mapping-filter frame,eth,ip,udp,tcp,dns > ./Kibana/custom_tshark_mapping.json
    # 2. 消除重复数据并对映射进行后期处理，以适应当前Elasticsearch版本
    ruby ./Public/process_tshark_mapping_json.rb
    # 3. 上传文件至虚拟机
    cd VM
    vagrant upload ../Kibana/custom_tshark_mapping_deduplicated.json /home/vagrant/tsharkVM/Kibana/custom_tshark_mapping_deduplicated.json
    cd ..
    # 4. 连接虚拟机并上传模板
    cd VM
    vagrant ssh
    cd tsharkVM/Kibana
    curl -X PUT "localhost:9200/_index_template/packets_template" -H 'Content-Type: application/json' -d@custom_tshark_mapping_deduplicated.json

或者我们也可以使用动态映射的方式，具体可以查看“./Kibana/template_tshark_mapping_dynamic.json”。

## 许可证协议

本项目的开发与发布遵循Apache License v2.0开源许可证协议。

## 项目地址

>  **tsharkVM：** 【[ _GitHub传送门_](https://github.com/H21lab/tsharkVM)】

