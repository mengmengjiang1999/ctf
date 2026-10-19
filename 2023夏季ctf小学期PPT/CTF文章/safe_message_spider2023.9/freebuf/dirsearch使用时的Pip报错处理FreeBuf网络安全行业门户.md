# dirsearch安装

觉得还是Github上的好使附上下载链接：

`https://github.com/maurosoria/dirsearch`

![image](https://image.3001.net/images/20230904/1693796373_64f548152c4807aa11206.png!small)

建议把他安装在python的目录下  
![image](https://image.3001.net/images/20230904/1693796331_64f547ebd5320345f6267.png!small)

# 报错处理

使用代码  
`python dirsearch.py -u +地址`  
然后就报错![image](https://image.3001.net/images/20230904/1693796452_64f54864b7afeb6cf246e.png!small)  
试了各种方法，更新pip，单独安装库，挂代理，更换python版本，后面发现不是版本的问题，而是需要切换国内的源

# pip切换清华源

加一个 -i的参数，切换为清华源pip可以正常使用  
`pip install -pq -i https://pypi.tuna.tsinghua.edu.cn/simple`  
![image](https://image.3001.net/images/20230904/1693796636_64f5491c99420aed3a712.png!small)  
就可以安装成功

# dirsearch使用

`python dirsearch.py -u https://www.xxx.com/`  
![image](https://image.3001.net/images/20230904/1693796799_64f549bff2134c955360f.png!small)

