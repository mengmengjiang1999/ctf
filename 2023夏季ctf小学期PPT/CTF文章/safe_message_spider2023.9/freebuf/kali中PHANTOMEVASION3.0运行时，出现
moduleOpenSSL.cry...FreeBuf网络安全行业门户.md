kali中直接用pip install pyopenssl安装当最新的openssl中的crypto中的函数名PKCS12Type改成了PKCS12

[![\[`MI%T2{~\[\)STJ89}YM8K3O
](https://image.3001.net/images/20201116/1605505906.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111091134877-839990942.png)

所以需要在phantom中改对应代码

[![wps24](https://image.3001.net/images/20201116/1605505908.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201110200412213-1325419360.jpg)

将这个文件中对应的PKCS12Type的改成PKCS12就OK了

![](https://image.3001.net/images/20201116/1605505909.png!small)

