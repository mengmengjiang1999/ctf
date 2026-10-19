## 起因

我有一个朋友。。。  
![image.png](https://image.3001.net/images/20210526/1622025744_60ae2610e14d7ceb5c9e7.png!small)  
![image.png](https://image.3001.net/images/20210526/1622025818_60ae265a40894e499fc62.png!small)

## 过程

按照这个密码，我觉得90%的可能是被爆破了。随即登录进行排查。

1\. 登录行为定位  
通过history发现在扫描全网3389：  
![image.png](https://image.3001.net/images/20210526/1622026077_60ae275dc3aa6a0b2abb0.png!small)  
看到此处使用yum安装了masscan，果断查看yum日志。  
![image.png](https://image.3001.net/images/20210526/1622026219_60ae27ebcc62c0421831f.png!small)  
发现了时间点，通过此时间点对登录者进行定位。  
![image.png](https://image.3001.net/images/20210526/1622026383_60ae288fc51d00a58cec2.png!small)  
118.70.52.167 越南 河内 河内市

2\. 可疑进程  
发现一进程大量占用CPU，对该进程文件进行定位。然后通过kill -9 杀掉进程，文件进行改名移动。  
此处我大意了。忘记截图了，只有当时交流的截图。  
![image.png](https://image.3001.net/images/20210526/1622026918_60ae2aa68c40328f4f4f9.png!small)  
果然一会，又新起来了一个新的进程。  
![image.png](https://image.3001.net/images/20210526/1622026566_60ae2946047495f2e13d3.png!small)  
![image.png](https://image.3001.net/images/20210526/1622026616_60ae29781abbb134747da.png!small)  
在查看进程env时候发现了端倪。  
![image.png](https://image.3001.net/images/20210526/1622026757_60ae2a052c008f948974e.png!small)  
同样的，该文件删除后也会立刻恢复。  
![image.png](https://image.3001.net/images/20210526/1622027110_60ae2b66ce6c6855a6c83.png!small)

3\. 定时任务  
刚开始朋友说使用`crontab -l`查过了计划任务，但是又无法解释删除后又出现。便查看/etc/crontab文件  
![image.png](https://image.3001.net/images/20210526/1622027337_60ae2c495ce592f482baa.png!small)  
gcc.sh 内容如下:  
![image.png](https://image.3001.net/images/20210526/1622027458_60ae2cc210e6346d1c811.png!small)  
同时也在/etc/cron.hourly/发现了可能是运行产生的临时文件（名字也是随机的10位字符串）  
![image.png](https://image.3001.net/images/20210526/1622027625_60ae2d693c8a96c77618f.png!small)

4\. 清理  
注释掉/etc/crontab中的恶意内容，将libudev.so、/usr/bin/hujqsw进行改名移动。又发现/etc/init.d情况如下：  
![image.png](https://image.3001.net/images/20210526/1622028384_60ae3060e740efa238fbc.png!small)  
使用grep -E 进行定位：  
![image.png](https://image.3001.net/images/20210526/1622028476_60ae30bca26af5b1b07ac.png!small)  
发现有一个正常的netconsole也被定位到了。可以先将其改名再恢复或者直接grep -v。  
然后使用xargs进行传参给rm  
![image.png](https://image.3001.net/images/20210526/1622028605_60ae313dccb4943acc764.png!small)

5\. ioc 溯源  
118.70.52.167 越南 河内 河内市  
41c85522f8a2a2a1235523cb3a1a24b8 libudev.so  
ca1fa3bbed65438116ad707900c63ecf hujqsw  
样本已上传微步、VT。搜索即可查看分析结果。对应标签为：DoS、Xorddos

## 结束

总的来说，此次处理过程只能说是比较大意。有看到`ps -aux`结果中恶意进程pid对应的名字为gnome-terminal，但是没有截图留存。也完美体现了/etc/crontab文件与`crontab -l`命令返回的差异性。

