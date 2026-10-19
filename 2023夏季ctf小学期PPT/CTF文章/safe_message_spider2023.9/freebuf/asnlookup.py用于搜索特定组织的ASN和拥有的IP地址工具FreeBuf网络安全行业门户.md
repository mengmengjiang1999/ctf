**ASN是由互联网号码分配机构（IANA）分配给自治系统（AS）的唯一号码。
AS由IP地址块组成，这些IP地址具有明确定义的用于访问外部网络的策略，并由单个组织管理此工具将在更新的数据库中搜索特定组织的ASN，然后使用后者查找组织注册和拥有的所有IP地址（IPv4和IPv6）。**

## 目的

可以在侦察阶段使用此脚本来识别公司拥有的属性，并对其运行端口扫描以识别开放端口和公开公开的服务。

## 用法

    
    
    $ git clone https://github.com/yassineaboukir/Asnlookup && cd Asnlookup
    $ pip install -r requirements.txt
    $ python asnlookup.py -o <Organization>
    

## 端口扫描

该工具将IP地址列表导出为文本文件，您可以将其与其他工具（如Masscan）一起使用。 另一方面，该工具支持Nmap和Masscan端口扫描。

### 安装Nmap

    
    
    - On CentOS
    yum install nmap
    - On Debian
    apt-get install nmap
    - On Ubuntu
    sudo apt-get install nmap
    - Mac OS
    brew install nmap
    

### 安装Masscan

下载地址<https://github.com/robertdavidgraham/masscan/>要扫描IP地址，请Masscan的命令`-m`参数或Nmap的`-n`：`$
python asnlookup.py -m -o <Organization>`您还可以传递自己的Nmap/Masscan参数（默认为nmap：-p
1-65535 -T4 -A -v;默认为Masscan： - p0-65535 --rate 200）。`$ python asnlookup.py -m
"<Masscan arguments>" -o <Organization>s`使用带自定义参数的Nmap的示例：`$ python
asnlookup.py -n "--top-ports 65535" -o
twitter`它会将结果导出到与脚本相同的目录中的文本文件（例如./twitter.txt），然后运行Nmap，如下所示：
![Image](https://image.3001.net/images/20190123/15482345935439.png!small)***参考来源：[github](https://github.com/yassineaboukir/Asnlookup)，由周大涛编译，转载请注明来自FreeBuf.COM**

