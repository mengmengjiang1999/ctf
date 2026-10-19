**搜索特定恶意软件样本很困难？不用怕，今天给大家介绍一款名叫Mquery的工具，它带有友好的Web前端界面，可帮助大家迅速寻找到自己想要的恶意软件样本。多亏了我们的UrsaDB数据库，正是因为有了它，Mquery才可以在一眨眼的功夫给到你想要的数据。**

## 工作机制

YARA的速度毋庸置疑，但是通过给定的数据签名来搜索大型数据库相对来说还是比较慢的。为了解决这个问题，我们实现了一个名叫UrsaDB的自定义数据库，它可以对结果进行预过滤，因此我们只需要运行YARA搜索一小段数据或代码即可：

![2.png](https://image.3001.net/images/20180703/15306142902291.png!small)

## 工具安装（Docker）

建议大家使用docker-compose来构建项目源码：

    
    
    git clone --recurse-submodules https://github.com/CERT-Polska/mquery.git
    docker-composeup --scale daemon=3  
    

其中“--scale daemon=...”指定的是选择或索引的同步进程任务数量。

注意：“docker-compose”必须支持docker-compose.yml v3语句，如果工具遇到问题，可尝试更新你的软件。

## 工具安装（手动）

1.运行ursadb数据库；

2.安装redis-server和Python2；

3.安装依赖组件：pipinstall-rrequirements.txt；

4.将config.example.py重命名为config.py，并对相关配置进行调整，设置单独的SECRET_KEY；

5.在Web服务器中搭建并设置Flask应用（webapp.py）；

6.运行daemon.py（一个可以持续运行的脚本文件）。

## 工具使用

1.搭建环境，完成工具的安装；

2.在浏览器输入<http://localhost:80/>访问Web界面；

3.可在/var/lib/docker/volumes/mquery_samples/_data中查询主机托管的索引文件，可使用“docker image
inspect mquery_samples”命令对样本进行调试；

4.打开Web接口，选择“admin”标签，点击“Index /mnt/samples”；

5.在索引过程中，当前运行进程可在“admin”标签下的“backend”部分查看到，ursadb也会定期在终端显示结果数据；

6.成功索引之后，你的文件将可被搜索到，切换到主标签页，上传相应Yara，例如：

    
    
    ruleemotet4_basic: trojan
    {
        meta:
            author = "psrok1/mak"
            module = "emotet"
        strings:
            $emotet4_rsa_public = { 8d ?? ?? 5? 8d?? ?? 5? 6a 00 68 00 80 00 00 ff 35 [4] ff 35 [4] 6a 13 68 01 00 01 00 ff 15[4] 85 }
            $emotet4_cnc_list = { 39 ?? ?5 [4] 0f44 ?? (FF | A3)}
        condition:
            all of them
    } 

*** 参考来源：[mquery](https://github.com/CERT-Polska/mquery)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

