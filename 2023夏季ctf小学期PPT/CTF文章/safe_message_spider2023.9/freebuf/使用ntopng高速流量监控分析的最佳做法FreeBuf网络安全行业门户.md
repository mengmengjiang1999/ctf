很多人都使用nProbe和ntopng来收集流量，其架构类似于下面图所示：

![](https://image.3001.net/images/20210513/1620886977_609cc5c16ed66c190b9f5.png!small)其中nprobe和ntopng的启动方式如下：

    
    
    nprobe -3 \<collector port> -i none -n none —zmq "tcp://\*:1234" --zmq-encryption-key \<pub key> ntopng -i tcp://nprobe\_host:1234 --zmq-encryption-key \<pub key>

在这种情况下，ntopng通过加密通道与nProbe通信，并以紧凑的二进制格式发送流，以实现最佳性能。如果不需要nProbe缓存和聚合流，则还可以–collector-passthrough 在nProbe端添加以进一步增加流收集性能。  
只要您具有根据系统性能合理收集的流量，此设置就非常适合。如果要收集的流量太多（例如，有许多路由器发送流到nProbe，或每秒发送许多流量的大路由器），则此设置不再适用，因为它没有利用多核体系结构。解决方案如下：

> 1.将负载分布在多个（而不是一个）nProbe实例上。
>
> 2.在ntopng上，收集多个ZMQ接口上的流，并最终将它们与视图接口聚合。

![](https://image.3001.net/images/20210513/1620887386_609cc75ac7372e1ba95a7.png!small)

启动nProbe / ntopng的方法，如下所示：

    
    
    nprobe -i none -n none -3 2055 —zmq tcp://127.0.0.1:1234 nprobe -i none -n none -3 2056 —zmq tcp://127.0.0.1:1235 nprobe -i none -n none -3 2057 —zmq tcp://127.0.0.1:1236 ntopng -i tcp://127.0.0.1:1234 -i tcp://127.0.0.1:1235 -i tcp://127.0.0.1:1236 -i view:all

在这种情况下，每个nProbe实例将同时处理流，并且在ntopng上也一样。您需要做的就是尝试在所有nProbe实例之间共享入口负载，以便每个实例接收数量接近的流，并在它们之间共享工作负载。

相反，如果您有单个大路由器将流导出到一个nProbe实例，则无法使用上述方法，因此我们需要以不同的方式进行负载平衡。这可以通过以下方式实现：

![](https://image.3001.net/images/20210513/1620887405_609cc76d9d8e2843a529e.png!small)

您可以通过以下方式配置nProbe：

    
    
    nprobe -i none -n none -3 2055 --collector-passthrough —zmq tcp://127.0.0.1:1234 —zmq tcp://127.0.0.1:1235 —zmq tcp://127.0.0.1:1236 ntopng -i tcp://127.0.0.1:1234 -i tcp://127.0.0.1:1235 -i tcp://127.0.0.1:1236 -i view:all

在这种情况下，当每个ZMQ接口在单独的线程上运行时，nProbe将负载均衡多个出口ZMQ上，并且ntopng将同时收集流。

 **注意：**

> –collector-passthrough 是可选的，但它可以减轻nProbe的负载，如果你有一个大的路由器出口朝着同一个nProbe实例这是可取的。
>
> 上述解决方案还可以用于原始数据包处理（nprobe -i  
> ethX），而不仅仅是流收集（在这种情况下–collector-> passthrough是没有必要的）。也就是说，越是在接口之间分散负载，就越能利用多核系统，系统性能也就可以提升。

 **虹科** 提供[网络流量监控与分析的软件解决方案-ntop](https://hongwangle.com/ntop/)。该方案可在物理，虚拟，容器等多种环境下部署，部署简单且无需任何专业硬件即可实现高速流量分析。解决方案由多个组件构成，每个组件即可单独使用，与第三方工具集成，也可以灵活组合形成不同解决方案。包含的组件如下：

> PF_RING：一种新型的网络套接字，可显着提高数据包捕获速度。  
> nProbe：网络探针，可用于处理NetFlow/sFlow流数据或者原始流量。  
> n2disk：用于高速连续流量存储处理和回放。  
> ntopng: 基于Web的网络流量监控分析工具，用于实时监控和回溯分析。

