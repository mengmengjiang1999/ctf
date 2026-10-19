## 前言

**当遇到几个IP地址，需要查询它的地理位置信息是很好办的，自己手动查询就行了。可是，如果遇到成千上万个IP地址需要查看它的地址位置信息怎么办？还有一种情况，当需要从网络数据包中提取出IP地址，并查询其地理信息时，又该怎么办？以前面对这种情况，大概只能说一句“臣妾做不到啊”。现在，笔者专门给懒惰的宝宝们写了一款小工具，可以方便地从IP清单文件中或者是网络数据包中批量地查询IP的地理位置信息。**  

****

## 工具使用

1） **工具详细信息打印**

运行程序：python IP_location.py –h

![image.png](https://image.3001.net/images/20180423/15244914819944.png!small)

看打印信息，这款工具主要有两个功能，一是读取IP清单文件，批量地查询里面IP地址的地理信息；二是读取pcap网络数据包，可以选择批量查询源/目的IP地址的地理信息。  

**2)** **批量查询清单文件中** **IP**  

批量查询IP清单文件中IP地址的地理信息，构造好IP清单文件，如图所示，一行即是一个IP地址。

![image.png](https://image.3001.net/images/20180423/15244915273066.png!small)  

运行程序：pythonIP_location.py --IPfile=./iplist.txt

![image.png](https://image.3001.net/images/20180423/15244915424276.png!small)

结果如图所示。同时，将结果存到了ip-location.txt中，以供查询。不但如此，笔者还加入了按照国别、地域分类存储的功能（惊不惊喜，高不高兴^^）。

![image.png](https://image.3001.net/images/20180423/15244915554644.png!small)

在源码中改成你想要的国别、地区和城市，就可以得到你想要的结果。结果分别存在out_country.txt、out_region.txt、out_city.txt中。  

**3)** **批量查询** **pcap** **文件中的** **IP**

pcap文件中的IP包中有源IP和目的IP，本工具实现的是对源IP和目的IP分开查询。以查询源IP为例。

运行：pythonIP_location.py --pcapfile=./out.pcap –s

-s 代表查询源IP地址的地理信息

-d 代表查询目的IP地址的地理信息

![image.png](https://image.3001.net/images/20180423/15244915815361.png!small)

打印信息的前半部分是提取出的源IP地址，后半部分为地址信息。而且不用担心会有相同的IP地址出现而产生大量的重复查询，笔者在程序里面对IP进行了去重操作（体不体贴，意不意外^^），所以可以放心地使用。当然，这些信息最后也以文件的形式存储了下来。out_ip.txt存的是从网络数据包中提取出的所有源IP地址信息。地理信息的存储方式同上。

 **总结**

代码即测试数据以传至github，大家可以方便的查询到。如大家还有其他的功能要求，可以留言给我哟~

[github]:<https://github.com/scu-igroup/IP-location>

 *** 本文作者scu-igroup，转载注明来自FreeBuf.com  
**

