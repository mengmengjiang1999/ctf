**今天给大家介绍的是一款名叫Hash Buster的工具，大家可以利用这款工具提供的API服务来进行hash查询。**  
![a.png](https://image.3001.net/images/20180618/15292599981936.png!small)

## 功能介绍

> 1\. 自动识别hash类型；
>
> 2\. 支持MD5、SHA1和SHA2；
>
> 3\. 从文件中提取并破解hash；
>
> 4\. 递归搜索目录中的hash；
>
> 5\. 提供了六种稳定的API；

## 跟Hulk一样强大，跟Bruce Banner一样智能

### 单一hash

你不需要指定hash类型，HashBuster能够在三秒之内自动识别并破解目标hash。

### 破解文件中的hash

Hash Buster能够从文件中搜索出hash：

    
    
    simple@gmail.com:21232f297a57a5a743894a0e4a801fc3
    {"json@gmail.com":"d033e22ae348aeb5660fc2140aec35850c4da997"}
    surrondedbytext8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918surrondedbytext  
    

### 从目录中查找hash

没错，你只需要指定一个目录路径，Hash Buster就能够从该目录的文件中搜索出hash。

## 安装和使用

你可以使用下列命令安装Hash-Buster：

    
    
    make install

### 破解单一hash

    
    
    buster -s <hash>

### 破解文件中的hash

    
    
    buster -f /root/hashes.txt

### 从目录中搜索hash

    
    
    buster -d /root/Documents

注意：请不要在目录路径结尾添加“/”。

## 许可证协议

Hash-Buster遵循MIT许可证协议。

 *** 参考来源：[Hash-Buster](https://github.com/s0md3v/Hash-Buster)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

