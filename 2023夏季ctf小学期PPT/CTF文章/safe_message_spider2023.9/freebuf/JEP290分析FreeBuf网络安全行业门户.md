## RMI中的实现

### 过滤器的创建

    
    
    LocateRegistry.createRegistry(1099);
    

我们跟进一下`createRegistry`方法

![image-20221011214141307.png](https://image.3001.net/images/20221017/1666017721_634d69b98bb454fb828c1.png!small)

返回的是一个`RegistryImpl`对象，跟进其构造方法

![image-20221011214824391.png](https://image.3001.net/images/20221017/1666017730_634d69c2759a6ed754ffe.png!small)

如果开启了开放端口为`1099`并且开启了`SecurityManager`策略

将会进入if语句中进行处理，我这里进入的是else语句

将会创建一个`LiveRef`对象，传入了`RegistryImpl`的ObjID(0)和端口号

