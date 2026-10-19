## **前言**

Goby
是一款实时网络空间测绘工具，我尤其喜欢插件市场，它可以集成很多我们平时利用的小工具，不用再去烦恼的打开一个个文件夹。初次编写插件的我选择从常见的未授权漏洞里边找，发现
Zookeeper 未授权漏洞的比较简单，利用方法只需要查看泄露的文件信息。

## 0x001 插件效果

### 1.1 插件使用

当扫描出 Zookeeper 未授权漏洞后，会在漏洞相关⻚以及资产详情处显示"View按钮"，点击即可展开该 Zookeeper
服务器的节点信息，在搜索框输入节点路径就可以查看该节点的数据。

![](https://image.3001.net/images/20210429/1619685670_608a712630cf869b3a5cc.gif!small)

## 0x002 插件开发

### 2.1 插件入口点

参考之前@Faz 师傅的“ES未授权利用”插件分享，把入口点选择在漏洞相关页面。

首先在 package.json 中和 extension.js 做以下配置。

![](https://image.3001.net/images/20210429/1619685230_608a6f6e976f19adbd24f.png!small)

### 2.2 大致开发思路

第一步:我们需要先连接上 Zookeeper 并得到数据，搜索一下 node.js 有没有相关连接 Zookeeper 的模块，运气很好找到了node-zookeeper-client这个模块，它提供了连接函数和一些处理数据的函数。

![](https://image.3001.net/images/20210429/1619685266_608a6f92a3e94d5d0e07c.png!small)

第二步:我们的 extension.js 需要和弹出的 html 窗口进行双向的数据传输，这里参考了@go0p 师傅的 Redis-cli
插件写法（下载完插件在 extensions 目录下找到插件文件夹查看）。

![](https://image.3001.net/images/20210429/1619685333_608a6fd52c0db9773ff6c.png!small)

第三步:编写 html，这点就不多说了，我比较懒所以直接 copy 修改。

### 2.3 extension.js编写

使用官方提供的开发脚手架，下载→解压到 goby/extensions 目录

在该文件夹下安装 node-zookeeper-client 模块（需要先安装npm）

    
    
    npm install node-zookeeper-client

extension.js 内容如下

    
    
    function activate(content) {
    
        class ZookeeperU{  //创建一个Zookeeper对象
    
            constructor(){  //构造函数
                this.Zookeeper = require('node-zookeeper-client');  //引入模块
                this.clent;
            }
    
            Zclent(hostinfo){  //创建连接zookeeper客户端的函数
                this.clent = this.Zookeeper.createClient(hostinfo,{sessionTimeout:5000});
                this.clent.connect();
                console.log(this.clent)
            }
    
            setInfo(hostinfo){
                this.hostinfo = hostinfo;
            }
    
            getInfo(){
                return this.hostinfo;
            }
    
            getListtree(){    //获取节点的函数
                return new Promise ((resolve,reject) => {
                    this.clent.listSubTreeBFS('/', function (error, children) {
                        if (error) {
                            console.log(error.stack);
                            return;
                        }
                        
                        resolve(children);
                    });
                })
            }
    
            getDataa(path){    //获取节点数据的函数
                return new Promise ((resolve,reject) => {
                    this.clent.getData(path, function (error, data,stat) {
                        if (error) {
                            console.log(error.stack);
                            return;
                        }
                        
                        resolve(data.toString());
                    });
                })
            }
        }
    
        if (!window.ZookeeperU){   //实例化Zookeeper对象
            window.ZookeeperU = new ZookeeperU();
        }
    
        goby.registerCommand('zookeeper', (content) => {
            window.ZookeeperU.setInfo(content.hostinfo);  //传入hostinfo(即IP和端口)
            window.ZookeeperU.Zclent(content.hostinfo);  
            let path = __dirname + "/index.html";
            goby.showIframeDia(path, "Zookeeper Unauthorized Exploitation", "600", "600");
        });
    
        goby.registerCommand('zookeeper_visi',  (content) => {
            return content.name === "zookeeper unauthorized"   //判断是否存在该漏洞
        });
    }
    
    exports.activate = activate;

需要注意的是，使用 node-zookeeper-client 模块的 listSubTreeBFS() 和 getData()
方法都是没有返回值（void），可以使用 Promise 来处理回调获取返回值。

### 2.4 编写index.html的javascript部分

    
    
    <script>
      var Zk = parent.ZookeeperU;    //获取父窗口的Zookeepe实例，注意Zookeeper后边没有括号
      let hostinfo = Zk.getInfo();  
      var path ="/";
      Zk.Zclent(hostinfo);
    
       Zk.getListtree().then(function (res){  //通过Promise对象then方法获取返回值
        var arr="";
        for(let i=1;i<res.length;i++){  
          var a=0;
          for(let j=res.length;j>i;j--){
            var b = res.slice(j,j+1);
            var c = b.toString();
            if(c.includes(res[i])==true){
              a=a+1;
            }
    
          }
          if(a==0){arr += '<p>'+ res[i] + '  ——File' +'</p>';}
          else{arr += '<p>'+ res[i] +'   ——File Node'+ '</p>';}
        }
        document.getElementById("Listname").innerHTML = arr;
      });
    
       Zk.getDataa(path).then(function (res){document.getElementById("Filedata").innerHTML = res;});
    
       function getinput(){
         path = document.getElementById("filename").value;
         Zk.getDataa(path).then(function (res){document.getElementById("Filedata").innerHTML = res;});
       }
    </script>

主要点：通过获取窗口的 Zookeeper 实例，调用实例的方法获取返回值，其他就是正常的处理了。

最后，把自己及插件的相关信息分别填到 package.json、Readme.md、Changlog.md 文件中，然后注册账号，打包上传发布。

## 0×003 小结

Goby 插件的开发文档写的非常清晰，插件的开发总体还是挺顺利的，用了一天半就做好了，过程中请教了@叶落凡尘 师傅和@go0p
师傅，学会了不少东西。最后希望师傅们多多反馈插件问题，开发插件的过程中大开脑洞，Goby 越来越好，冲冲冲！

插件开发文档及Goby开发版下载：  
<https://gobies.org/docs.html>

关于插件开发在B站都有详细的教学，欢迎大家到弹幕区合影~  
<https://www.bilibili.com/video/BV1u54y147PF/>

文章来自Goby社区成员：h1ei1，转载请注明出处。

