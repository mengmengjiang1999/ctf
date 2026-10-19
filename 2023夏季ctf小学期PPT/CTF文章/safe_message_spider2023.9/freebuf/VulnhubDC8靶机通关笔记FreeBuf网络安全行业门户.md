官网信息

![1612402732_601b502c4f8ad50017530.png!small](https://image.3001.net/images/20210204/1612402732_601b502c4f8ad50017530.png!small)

确定主机IP

![1612402751_601b503fdc9d248a9ca15.png!small](https://image.3001.net/images/20210204/1612402751_601b503fdc9d248a9ca15.png!small)

扫描开放端口

![1612402821_601b508505caa23a295cf.png!small](https://image.3001.net/images/20210204/1612402821_601b508505caa23a295cf.png!small)

URL发现sql注入

![1612403350_601b5296d00b4b74c2090.png!small](https://image.3001.net/images/20210204/1612403350_601b5296d00b4b74c2090.png!small)

![1612403381_601b52b565fed16745402.png!small](https://image.3001.net/images/20210204/1612403381_601b52b565fed16745402.png!small)

![1612403391_601b52bfc3c7e1fd22440.png!small](https://image.3001.net/images/20210204/1612403391_601b52bfc3c7e1fd22440.png!small)

利用sqlmap工具爆破出库名

![1612403537_601b5351b79d949aa820a.png!small](https://image.3001.net/images/20210204/1612403537_601b5351b79d949aa820a.png!small)

![1612403547_601b535b30eb58366d2a1.png!small](https://image.3001.net/images/20210204/1612403547_601b535b30eb58366d2a1.png!small)

爆破表名

![1612403601_601b539123c9c92293f08.png!small](https://image.3001.net/images/20210204/1612403601_601b539123c9c92293f08.png!small)

得到user表名

![1612403695_601b53efdea1bc0c44b79.png!small](https://image.3001.net/images/20210204/1612403695_601b53efdea1bc0c44b79.png!small)

获取字段

![1612403744_601b542088562b7d0592f.png!small](https://image.3001.net/images/20210204/1612403744_601b542088562b7d0592f.png!small)

![1612403752_601b54286ac264b32840d.png!small](https://image.3001.net/images/20210204/1612403752_601b54286ac264b32840d.png!small)

获取信息![1612403814_601b54669f5267d7de394.png!small](https://image.3001.net/images/20210204/1612403814_601b54669f5267d7de394.png!small)

![1612403823_601b546f01c51a1470c79.png!small](https://image.3001.net/images/20210204/1612403823_601b546f01c51a1470c79.png!small)

使用john工具破解密码

![1612665781_601f53b56e0fc08dd986b.png!small](https://image.3001.net/images/20210207/1612665781_601f53b56e0fc08dd986b.png!small)

root@kali:~# john -show hash.txt

成功得到密码

![1612665814_601f53d63b7b49d21404f.png!small](https://image.3001.net/images/20210207/1612665814_601f53d63b7b49d21404f.png!small)

登录后台

![1612669308_601f617cee104e8791de4.png!small](https://image.3001.net/images/20210207/1612669308_601f617cee104e8791de4.png!small)

![1612669330_601f619259b8602f39a33.png!small](https://image.3001.net/images/20210207/1612669330_601f619259b8602f39a33.png!small)

![1612669345_601f61a1d453a9c8fa8be.png!small](https://image.3001.net/images/20210207/1612669345_601f61a1d453a9c8fa8be.png!small)

![1612669357_601f61ad01018ece01f3b.png!small](https://image.3001.net/images/20210207/1612669357_601f61ad01018ece01f3b.png!small)

![1612669371_601f61bbe637a2a4aed91.png!small](https://image.3001.net/images/20210207/1612669371_601f61bbe637a2a4aed91.png!small)

![1612669477_601f6225560f39987afdb.png!small](https://image.3001.net/images/20210207/1612669477_601f6225560f39987afdb.png!small)

kali端开启监听

![1612669522_601f62520869b73cf9622.png!small](https://image.3001.net/images/20210207/1612669522_601f62520869b73cf9622.png!small)

保存了代码之后要进行表单提交

![1612669673_601f62e94f098f3c1e502.png!small](https://image.3001.net/images/20210207/1612669673_601f62e94f098f3c1e502.png!small)

find / -perm /4000

查找具有执行权限文件

![1612669862_601f63a624e6e69d682df.png!small](https://image.3001.net/images/20210207/1612669862_601f63a624e6e69d682df.png!small)

![1612670086_601f6486c068aa81b4aae.png!small](https://image.3001.net/images/20210207/1612670086_601f6486c068aa81b4aae.png!small)

将权限提升脚本传入靶机

根据脚本说明权限提升有两种方法

![1612670809_601f6759827293103defe.png!small](https://image.3001.net/images/20210207/1612670809_601f6759827293103defe.png!small)

echo "-m setuid : use the setuid payload (default)"  
echo "-m netcat : use the netcat payload"

给脚本加上可执行权限

![1612670905_601f67b92193630653ef5.png!small](https://image.3001.net/images/20210207/1612670905_601f67b92193630653ef5.png!small)

第一种方法未成功

第二种方式可行

![1612670967_601f67f7bdde395f7b0c8.png!small](https://image.3001.net/images/20210207/1612670967_601f67f7bdde395f7b0c8.png!small)

获取flag

![1612670994_601f6812a2a5d438a2098.png!small](https://image.3001.net/images/20210207/1612670994_601f6812a2a5d438a2098.png!small)

