# Apache ActiveMQ NMS-RCE

## 漏洞信息

  * 漏洞描述  
[ZDI](https://www.zerodayinitiative.com/advisories/ZDI-23-1281/)

This vulnerability allows remote attackers to execute arbitrary code on
affected installations of Apache ActiveMQ NMS. Interaction with this library
is required to exploit this vulnerability but attack vectors may vary
depending on the implementation.

The specific flaw exists within the Body accessor method. The issue results
from the lack of proper validation of user-supplied data, which can result in
deserialization of untrusted data. An attacker can leverage this vulnerability
to execute code in the context of the current process.

  * 影响组件 及版本  
[activemq-nms-openwire](https://github.com/apache/activemq-nms-openwire)<
2.1.0-rc1  
Apache.NMS.AMQP.dll （AMQP协议）< 2.1.0  
Apache.NMS.ActiveMQ.dll （OpenWire协议）< 2.1.0

![](./img/1759378654749286804.png)

## 环境搭建

[demo](https://activemq.apache.org/components/nms/documentation)

## 漏洞分析

  * NMS的消息格式
    
        Apache.NMS.ActiveMQ.Commands.ActiveMQBlobMessage
    Apache.NMS.ActiveMQ.Commands.ActiveMQBytesMessage
    Apache.NMS.ActiveMQ.Commands.ActiveMQMapMessage
    Apache.NMS.ActiveMQ.Commands.ActiveMQObjectMessage : ActiveMQMessage, IObjectMessage, IMessage
    Apache.NMS.ActiveMQ.Commands.ActiveMQStreamMessage
    Apache.NMS.ActiveMQ.Commands.ActiveMQTextMessage

其中在处理ActiveMQObjectMessage的消息body时，会对其进行序列化和反序列化，并且未对其做任何限制，导致RCE。

  * 发送ActiveMQObjectMessage消息时对其进行序列化的过程

调用producer.Send(IObjectMessage)之后会调用ActiveMQMessageMarshaller#LooseMarshal方法处理消息

    
    
    public override void LooseMarshal(OpenWireFormat wireFormat, object o, BinaryWriter dataOut)
        {
          ActiveMQMessage activeMqMessage = (ActiveMQMessage) o;
          activeMqMessage.BeforeMarshall(wireFormat);
          base.LooseMarshal(wireFormat, o, dataOut);
          activeMqMessage.AfterMarshall(wireFormat);
        }

此时activeMqMessage的type是ActiveMQObjectMessage，进而调用  
ActiveMQObjectMessage#BeforeMarshall()方法对消息体序列化，如下图：

![](./img/1990359563645741183.png)  
此时序列化的formatter为BinaryFormatter，消息体this.body是构造恶意的对象，最后将序列化的对象存放到content中。

  * 如何触发反序列化？

当客户端消费消息时会拿到ActiveMQObjectMessage的类`IObjectMessage message =
consumer.Receive() as
IObjectMessage;`对消息体进行处理时，即调用message.body方法，getbody方法实现如下：

![](./img/2479429007451858913.png)

直接将之前存放序列化对象的content反序列化。  
复现如下：使用的链子是TextFormattingRunProperties。

![](./img/2922946368943822289.png)

## 补丁分析

使用SerializationBinder限制反序列化类型，支持自定义的白名单列表

![](./img/2793997133996474286.png)

## 参考

[commit](https://github.com/apache/activemq-nms-openwire/commit/6bedbb4)

