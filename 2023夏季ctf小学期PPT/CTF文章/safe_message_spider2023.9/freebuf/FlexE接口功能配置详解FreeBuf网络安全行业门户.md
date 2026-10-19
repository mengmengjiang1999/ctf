**该说明为仅供参考不同设备型号对于配置命令可能有微小的差异**

## 1.FlexE接口：

1)背景：网络接口需要根据不同的业务提供不同的带宽，以太网口固定速率不能灵活适配不同的网络业务  
通过部署FlexE接口，对于不同的业务分配带宽  
2)分类：有物理接口和业务接口  
物理接口：以太网接口切换到灵活以太模式的物理接口，可以加入FlexE-Group接口，FlexE组接口的带宽等于所有FlexE物理接口带宽总和  
业务接口：灵活指定带宽的逻辑接口。组接口的带宽可以按需要分配给FlexE业务接口，从而实现针对不同业务分配不同带宽

## 2.FlexE-Group接口

功能：创建组接口后可以将多个物理接口加入组接口，并根据业务流量需求将组内多个物理接口的总带宽按灵活分配给各业务接口，达到为不同  
业务分配不同带宽的目的；  
**组接口的个数赢该小于等于接口扩展上物理接口的实际个数  
**只有FlexE-Group接口下不存在bind interface和client命令时，才能删除该组接口3.物理接口加入组接口  
[A-4-FlexE-Group5/0/1]bind interface FlexE-50-100G 5/0/0 phy-number 20  
**一个物理接口只能加入一个组接口  
**需要在两台设备上分别将FlexE物理接口加入Group-number相同的FlexE-Group接口，且加入时指定的phy-number必须相同  
**多个物理接口可以加入同一个组接口但是同一个组接口中的物理接口的phy-number不能相同

当物理接口的带宽或时隙被业务接口绑定时，不能将该物理接口从组接口中删除，不能修改FlexE接口的phy-number值

## 4.创建业务接口并配置接口带宽：

[A-4]flexe config-mode slot 5 subslot 0 bandwidth 命令配置FlexE业务接口模式为带宽模式时，  
只能执行client client-id bandwith value命令为业务接口灵活配置具体带宽

[A-4]flexe config-mode slot 5 subslot 0 timeslot 命令配置FlexE业务接口模式为时隙模式时  
只能执行 client client-id binding interface interface-type interface-number
timeslot timeslot-list  
对于FlexE-100G接口 时隙编号取值范围为0-19 一个时隙代表5G带宽

## 5.配置FlexE物理接口绑定承载时钟业务的FlexE业务接口

：物理接口无法处理时钟业务的协议报文，需要FlexE业务接口处理；  
**业务时钟正常工作需要保证对接的两端设备上FlexE业务接口的client-id参数值相同，否则时钟业务不可用  
如果业务接口故障而影响时钟业务，可将FlexE物理接口绑定其他可用FlexE业务接口 切换过程时钟不可用  
[DX-A3-FlexE-50-100G5/0/0]clock binding interface FlexE业务接口

## 6.配置FlexE接口的MTU

修改接口FlexE接口的MTU值会影响IP报文的分片与重组  
[DX-A3-FlexE5/0/1:1]int flexe-dcn5/0/0  
[DX-A3-FlexE-DCN5/0/0]m  
[DX-A3-FlexE-DCN5/0/0]mtu

## 7.切换FlexE业务接口的二三层工作模式

二层：bridge  
三层：route

## 8.配置业务接口允许超长帧通过

超长帧：业务接口在进行文件传输等大吞吐量数据交换的时候，接口收到的长度大于固定值的帧，固定值的大小与设备具体型号有关  
**如果系统配置了禁止超长帧通过，会直接丢弃该帧不在进行处理  
**允许超长帧通过，当接口收到长度在指定范围内的超长帧时，系统会继续处理，当接口收到长度超过指定最大长度的超长帧时，系统会丢弃不在处理帧  
业务接口视图如下命令  
[DX-A3-FlexE5/0/1:1]jumboframe enable [size]

## 9.配置FlexE接口物理连接状态抑制功能

需求：如果短时间内接口物理状态频繁改变，会给系统带来额外的开销，可设置物理连接状态抑制功能，在抑制时间内，系统忽略接口的物理状态变化  
若经过抑制状态后，如果状态还没有恢复，在上报cpu处理  
**同一接口下，接口状态从up到down的抑制时间和接口状态从down变成up的抑制时间可以不同  
**可以配置抑制上报down状态和抑制上报up状态  
**当配置的是同一状态的抑制时间，则最新的配置生效  
[DX-A3-FlexE5/0/1:1]link-delay ?  
down Suppress link-down event  
up Suppress link-up event  
[DX-A3-FlexE5/0/1:1]link-delay up ?  
INTEGER<0-600> Delay time in seconds  
msec Set the delay time in milliseconds  
[DX-A3-FlexE5/0/1:1]link-delay up msec ?  
INTEGER<0-10000> Delay time in milliseconds, in steps of 10

## 10.配置FEC功能

功能：用于报文纠错，发送端为数据报文附加纠错信息，在接受端利用纠错信息来纠正数据报文在传输时产生的错误编码  
[DX-A3-FlexE-50-100G5/0/0]port fec mode ?  
auto Enable FEC autonegotiation  
none Disable FEC  
rs-fec Enable Reed-Solomon FEC

## 11.配置FlexE业务接口的流量控制功能

基本原理：如果本端 设备发生拥塞，将通知对端暂时停止发送报文；对端收到消息后停止向本端发送报文，反之亦然  
flow-control 设备具有发送和接收流量控制报文的能力

flow-control receive enable 设备具有接收控制报文的能力 但不具有发送流量控制报文的能力  
**当本端收到对端的流量控制报文，会停止向对端发送报文  
当本端发生拥塞时，设备不能向对端发送流量控制报文

## 12.配置FlexE业务接口的PFC功能

priority-base FLow Control ：基于优先级的流量控制  
为了避免报文在传输过程中因拥塞而发生丢包，需在报文流经的所有端口上都进行相同的PFC功能配置  
**无论端口是否配置PFC功能，端口都可以接收PFC pause帧，但只有PFC功能enable时，才对收到的PFC pause帧进行处理  
所以两端的PFC功能都需要开启才能生效  
PFC功能的开启优先于流量控制功能的开启

## 13.开启FlexE接口的环回功能

内部环回：配置内部环回后，接口将需要从接口转发出去的报文返回给设备内部，让报文向内部线路环回，内部环回用于定位设备是否故障  
外部环回：配置外部环回后，接口将需要从接口转发出去的报文返回给设备外部，让报文向外部线路环回，外部环回用于定位设备间链路是否故障  
[DX-A3-FlexE5/0/1:1]loopback ?  
external Specify external loopback on this port  
internal Specify internal loopback on this port

 **暂时就到这了，后续欢迎补充**

