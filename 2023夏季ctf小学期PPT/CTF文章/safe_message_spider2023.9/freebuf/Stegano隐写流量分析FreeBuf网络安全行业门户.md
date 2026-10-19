CTF套路千千万，今天来看看流量分析。

本次实验题目地址：[《CTF
Stegano练习之隐写5》](https://www.hetianlab.com/expc.do?ec=ECID172.19.104.182014121214032100001&pk_campaign=freebuf-wemedia)。

先来看题，给定的secret文件没有扩展名，我们需要先弄清楚文件的具体格式信息，才好进行更进一步的分析操作，这里使用TrID工具来对其进行识别。打开cmd命令提示符，切换到C:\Stegano\5目录，使用TrID对secret进行识别，如图所示：

![headImg.action?news=2724c480-4462-4708-ab97-06738e732a95.png](https://image.3001.net/images/20210330/1617092277_6062deb531cf2bab29bdc.png!small)

PCAP文件，这种类型的文件通常为网络通信流量抓包文件，可以使用Wireshark进行分析。我们给文件加上.pcap扩展名，然后使用Wireshark将其打开，就可以看到网络通信数据了，如图所示：

![headImg.action?news=c34a67f3-6eea-4032-b9e3-15b811285404.png](https://image.3001.net/images/20210330/1617092277_6062deb5b2065df6591e2.png!small)

372条通信记录，算是很少很少的了，我们先看一下协议类型，除了TCP和UDP协议之外，更具体的协议大概有：TLS、ICMP、DNS、HTTP、FTP。我们可以对这几个协议的数据进行详细的分析，以FTP协议为例，选中一条FTP通信记录，然后单击右键，在菜单中选择“Follow
TCP Stream”，我们看到的信息如图所示：

![headImg.action?news=11cfbba8-df50-4066-8929-b3bb07b4b271.png](https://image.3001.net/images/20210330/1617092278_6062deb6be5ed9a28cb03.png!small)

其中有一个hello.txt文件以及super_secret_message.png文件，这两个文件看起来比较可疑。

我们可以跟踪一下这两个文件的数据。因为FTP的控制命令和文件数据传输分开在两个不同的TCP连接中，因此我们还需要找到传输数据的TCP连接。经过实验步骤二的分析，我们知道通过FTP传送了hello.txt以及super_secret_message.png两个文件，现在我们需要将这两个文件的数据提取出来。

通过在Wireshark中对通信流量的分析，我们发现在包的序号为204的地方开始传送hello.txt的内容，在包的序号为312的地方开始传送super_secret_message.png的内容，如图所示：

![headImg.action?news=0e076421-0d56-428b-939d-542ca20b3eb3.png](https://image.3001.net/images/20210330/1617092279_6062deb769cb84e76bd2e.png!small)

因此我们可以在204以及312后面的数据包去找，以super_secret_message.png文件为例，我们发现序号为313的数据包的协议为FTP-DATA，选中该条记录之后，邮件选择“Follow TCP Stream”，显示方式选择“Raw”，然后选择“Save
As”就可以保存这个PNG文件了，如下图所示：

![headImg.action?news=999b01ff-1a2a-4240-bb4b-669b3fa222ad.png](https://image.3001.net/images/20210330/1617092280_6062deb817155f76a06be.png!small)

打开PNG图片就可以看到Flag为flag{ThIs_Is_sO_1337}，分析完毕。

老套路，还是隐写题，只是加了个流量分析，还要了解FTP协议，分析数据。找到突破口，合理的进行提取就可以事半功倍。

