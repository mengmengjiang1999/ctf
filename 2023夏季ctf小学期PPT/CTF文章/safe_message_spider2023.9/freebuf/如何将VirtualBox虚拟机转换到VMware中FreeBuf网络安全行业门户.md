首先使用VirtualBox打开虚拟机压缩文件.ova文件，将虚拟机安装好

安装好后进入虚拟机安装目录，找到.vdi文件

![](https://image.3001.net/images/20220902/1662124161_631200818af3d006f9b90.png!small)

记住.vdi文件的文件路径和文件名

进入到VirtualBox软件的安装目录，找到VBoxManage.exe

![](https://image.3001.net/images/20220902/1662124177_631200917259f93c9bb05.png!small)

在这个目录下打开命令行，输入以下命令把vdi文件转换成VM所能用的vmdk文件

    
    
    VBoxManage.exe clonehd    vdi文件(绝对路径)    vmdk文件(输入你想要存储vmdk的位置以及名字的绝对路径)  --format VMDK

![](https://image.3001.net/images/20220902/1662124209_631200b1cfcda5bd899cc.png!small)

此时的vmdk文件VMware还不能用，还需要用VMware再转换一次

找到VMware软件的安装目录，找到vmware-vdiskmanager.exe

![](https://image.3001.net/images/20220902/1662124223_631200bf5296ead8cc3ea.png!small)

在此目录下打开命令行，输入以下命令将.vmdk文件转换为.com.vmdk文件

    
    
    vmware-vdiskmanager.exe  -r  "vmdk文件（绝对路径）"  -t  0  ".com.vmdk文件（绝对路径）"

![](https://image.3001.net/images/20220902/1662124255_631200df90cdb15bf441c.png!small)

用VMware新建虚拟机

![](https://image.3001.net/images/20220902/1662124274_631200f22ca267167df7e.png!small)

选择自定义

![](https://image.3001.net/images/20220902/1662124289_6312010172d51b6232d58.png!small)

默认下一步

![](https://image.3001.net/images/20220902/1662124301_6312010d8f5b1673fda6e.png!small)

选择稍后安装操作系统

![](https://image.3001.net/images/20220902/1662124314_6312011a016dd8017ae1c.png!small)

这里自己转换的虚拟机是什么操作系统就选什么

![](https://image.3001.net/images/20220902/1662124327_63120127852a7ea1eb06a.png!small)

这里填入虚拟机的名字和想要保存的位置

![](https://image.3001.net/images/20220902/1662124341_631201352548cd6a6e88b.png!small)

这里看虚拟机要求和电脑配置自行选择

![](https://image.3001.net/images/20220902/1662124362_6312014ac0e7778c34ad8.png!small)

这里也是看虚拟机要求和电脑配置自行选择

![](https://image.3001.net/images/20220902/1662124377_631201595d1efb8799b1e.png!small)

这可以桥接可以NAT，看自己选择，我是用的NAT，因为我得kali攻击机是NAT

![](https://image.3001.net/images/20220902/1662124391_63120167d546bba42c34a.png!small)

这里默认

![](https://image.3001.net/images/20220902/1662124405_63120175eeb7d97d4cbdc.png!small)

默认

![](https://image.3001.net/images/20220902/1662124419_63120183dba33e51736ae.png!small)

这里选择使用现有虚拟磁盘

![](https://image.3001.net/images/20220902/1662124433_631201912b11f48f80110.png!small)

选择刚才转换得到的.com.vmdk文件

![](https://image.3001.net/images/20220902/1662124446_6312019e7c302becde23a.png!small)

这里选择转换

![](https://image.3001.net/images/20220902/1662124461_631201adc95a47b7c997f.png!small)

完成转换

![](https://image.3001.net/images/20220902/1662124478_631201bee95dd3b137a3b.png!small)

正常启动虚拟机即可。

