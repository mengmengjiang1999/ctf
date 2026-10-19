近期，新冠肺炎在韩国大爆发，不过某些思密达们好像不是很在意，一句哈利路亚，23333  

![2.png](https://image.3001.net/images/20200302/1583159891_5e5d1a53ecc11.png!small)  

而一些长期针对韩国的APT组织也开始利用疫情相关新闻开始搞事，安全研究人员发现一例kimsuky利用疫情搞事情的样本。

![1.png](https://image.3001.net/images/20200302/1583159900_5e5d1a5c5aad4.png!small)  

样本相关信息如下

文件名| 코로나바이러스 대응.doc_（冠状病毒对应）  
---|---  
MD5| a9dac36efd7c99dc5ef8e1bf24c2d747  
利用方式| 宏  
后续链接| vnext.mireene[.]com/theme/basic/skin/member/basic/upload/search.hta  
样本地址| <https://app.any.run/tasks/bac5cebf-30df-457c-aa56-511a58d01e63/>  
  
样本运行后显示如下内容诱导受害者启用宏

![3.png](https://image.3001.net/images/20200302/1583159910_5e5d1a66c6aed.png!small)  

当受害者启用宏之后，便会显示疫情相关文档迷惑受害者

![4.png](https://image.3001.net/images/20200302/1583159918_5e5d1a6e8930b.png!small)  

而恶意宏会从vnext.mireene[.]com/theme/basic/skin/member/basic/upload/search.hta下载Hta文件执行

但发现时已经无法获取Hta文件了。

![5.png](https://image.3001.net/images/20200302/1583159928_5e5d1a786cb96.png!small)  

不过有兴趣的大佬可以分析分析之前的同源样本

md5| 50416931926754d867c9e5f418a4d08a  
---|---  
利用方式| 宏  
后续地址| http://kiseong[.]co[.]kr/m/public/navi/rabin/pop[.]hta  
样本地址| <https://app.any.run/tasks/a08e3d24-e6b8-4695-a6d9-af7823499514/>  
  
在anyrun沙箱还可以看到hta文件

![6.png](https://image.3001.net/images/20200302/1583159934_5e5d1a7e11c1d.png!small)  

