几个星期以来，全世界的目光都集中在俄乌冲突上。西方国家对俄罗斯的银行和企业进行了多轮制裁，也在国际媒体上引起了热议。这也为攻击者提供了机会，利用相关话题进行针对性攻击。

近日，研究人员发现冒充美国证券交易委员会（SEC）发送相关话题的恶意文档，研究认为是 Cloud Atlas 发起的攻击行动。

该文档的内容大体是要求从俄罗斯客户处获取信息的要求：

![image.png-222.6kB](https://image.3001.net/images/20220406/1649245262_624d7c4e20ae3717ea093.png!small)诱饵文档

初期的时候，恶意文档的检出率非常低。

![image.png-60.5kB](https://image.3001.net/images/20220406/1649245262_624d7c4eaafe6bd264607.png!small)VirusTotal
检测结果

接着深入分析 Payload 与相关攻击技术：

![image.png-124.7kB](https://image.3001.net/images/20220406/1649245263_624d7c4f0d1d2a51dc0cd.png!small)反汇编代码

通常情况下，恶意文档都是一个 Dropper。在文档中，可以发现一个指向压缩文档的 URL 地址（`hxxps://cvg[.]org/wp-content/uploads/2020/document.zip`）。

该压缩文件的检出率最初也很低：

![image.png-53.5kB](https://image.3001.net/images/20220406/1649245263_624d7c4f7ae81abea147f.png!small)VirusTotal
检测结果

下载得到文件后，将程序安装进系统的（`%LOCALAPPDATA%\EdgeTools\edgecef.dll`）路径中，其中包括一些合法文件与恶意库文件（main）。

![image.png-43.3kB](https://image.3001.net/images/20220406/1649245263_624d7c4fdde8eb78a90bd.png!small)包内信息

之后，恶意样本就会向 C&C 服务器发起连接，将失陷主机的相关信息发送过去，并等待后续的命令。

研究人员认为该攻击是由 Cloud Atlas 发起的，该组织自 2014 年被发现时已经活跃了多年，经常使用恶意样本攻击大使馆、航空业组织等政府单位。

## IOC

> 8df0d05c36a64b13869343917076ba8f65604ea1ecde50292f361ad4e34b4b09  
> ff06cffedc00b97f82005c9768951d0e8c18c63ba36e584aef3c7c9e845e62e0  
> 4eb85a5532b98cbc4a6db1697cf46b9e2b7e28e89d6bbfc137b36c0736cd80e2  
> driverwindowsupdate.at  
> windowsdriverupdate.at  
> 212.193.48.150

## 参考来源

> [Inquest](https://inquest.net/blog/2022/03/30/cloud-atlas-maldoc)

