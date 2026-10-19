![](https://image.3001.net/images/20200414/1586861131_5e95944b1673f.jpg!small)

## Inhale - Malware Inhaler

**Inhale是一款针对恶意软件的分析与分类工具，广大安全研究人员可以利用Inhale来对恶意软件中的很多的静态分析操作进行自动化实现以及扩大覆盖范围。请注意，当前版本的Inhale仍处于测试阶段（Beta版本），欢迎社区的各位大神贡献自己的代码。**

从一开始，Inhale只是由一系列小型脚本组成，可以用来从各种恶意源收集和分析大量恶意软件。虽然目前社区中有很多的框架和工具可以完成类似的工作，但是它们却无法满足我自己的工作流任务，比如说快速发现、分类和存储大量恶意软件相关的文件之类的任务。除此之外，也有很多服务要求购买API密钥和其他服务，这也会花掉我们很多钱。

因此，我便打算将我自己收集和使用的脚本整合成一套工具，Inhale便应运而生，该工具的安装和使用都分厂方便，你可以在一台研究服务器中使用Inhale，也可以在自己的笔记本电脑上使用，甚至你还可以在树莓派上使用Inhale。

## 工具安装

该工具目前仅支持在Linux系统平台上运行，并且需要使用Python3、ElasticSearch、Radare2、Yara和Binwalk。除此之外，你还需要使用到jq来对数据库中读取出的输出内容进行格式化。

### Python3

安装依赖组件：

    
    
    python3 -m pip install -r requirements.txt

### 安装ElasticSearch（Debian）

> 详细文档：【[
> _点我获取_](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-> elasticsearch.html)】
    
    
    wget -qO -<https://artifacts.elastic.co/GPG-KEY-elasticsearch>| sudo apt-key add -    
    sudo apt-get install apt-transport-https
    
    echo "deb<https://artifacts.elastic.co/packages/7.x/apt>stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
    
    sudo apt-get update && sudo apt-get install elasticsearch
    
    sudo service elasticsearch start

当然了，你也可以按照这篇【[
_指南_](https://www.elastic.co/guide/en/elasticsearch/reference/current/targz.html)】来进行手动安装

除此之外，你也可以[ _设置一个完整的ELK栈_](https://www.freebuf.com/wp-admin/post.php?post=233623&action=edit#installing-elk)来实现数据分析和可视化，但这对于该工具来说只是可选项而已。

### 安装Radare2

需要注意的是，你需要从Radare2的[
_GitHub库_](https://github.com/radare/radare2)来安装Radare2，不要使用其他的包安装工具。

    
    
    git clone<https://github.com/radare/radare2>
    
    cd radare2
    
    sys/install.sh

### 安装Yara

> 详细文档：【[ _点我获取_](https://yara.readthedocs.io/en/v3.10.0/gettingstarted.html)】
    
    
    sudo apt-get install automake libtool make gcc
    
    wget<https://github.com/VirusTotal/yara/archive/v3.10.0.tar.gz>
    
    tar xvzf v3.10.0.tar.gz
    
    cd yara-3.10.0/
    
    ./bootstrap.sh
    
    ./configure
    
    make
    
    sudo make install

如果你接收到了关于共享对象的错误信息，可以尝试运行下列命令来进行修复：

    
    
    sudo sh -c 'echo "/usr/local/lib" >> /etc/ld.so.conf'
    
    sudo ldconfig

### 安装binwalk

广大用户可以直接使用下列命令来安装[ _binwalk_](https://github.com/ReFirmLabs/binwalk)：

    
    
    git clone<https://github.com/ReFirmLabs/binwalk>
    
    cd binwalk
    
    sudo python3 setup.py install

## 工具使用

根据目标类型来指定需要爬取和分析的文件：

    
    
    -f infile
    
    -d directory
    
    -u url
    
    -r recursive url

### 其他选项

    
    
    -t TAGS Additional Tags
    
    -b Turn off binwalk signatures with this flag
    
    -y YARARULES Custom Yara Rules
    
    -o OUTDIR Store scraped files in specific output dir (default:./files/<date>/)
    
    -i Just print info, don't add files to database

## 工具使用样例

运行inhale.py之后，将会对指定文件/目录/URL地址来进行分析，并将分析结果输入在终端窗口。

查看/bin/ls内容，但并不添加至数据库中：

    
    
    python3 inhale.py -f /bin/ls -i 

添加目录‘`malwarez`’至数据库：

    
    
    python3 inhale.py -d malwarez

下载目标文件，并添加至数据库中：

    
    
    python3 inhale.py -u https://thugcrowd.com/chal/skull

下载远程目录中的全部内容，并标记为“`phishing`”：

    
    
    python3 inhale.py -r http://someurl.com/opendir/ -t phishing

### Yara规则

你可以使用-y参数来设置你自己的[
_Yara规则_](https://github.com/kevthehermit/PasteHunter/tree/master/YaraRules)。

### 查询数据库

广大研究人员可以使用db.sh来快速询数据库：

    
    
    db.sh *something* | jq .

## 项目地址

> Inhale：【[ _GitHub传送门_](https://github.com/netspooky/inhale)】

 *** 参考来源：[
_netspooky_](https://github.com/netspooky/inhale)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

