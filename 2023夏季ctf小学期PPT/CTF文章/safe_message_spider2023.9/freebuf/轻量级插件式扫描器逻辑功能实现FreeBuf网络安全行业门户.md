##  

### 简介

从Python逐渐流行以来插件式扫描器渐渐进入人们的视野，插件式扫描器对于扫描引擎和扫描插件之间的耦合度较低，插件和引擎分离代表插件可以继续扩充从而提高扫描器的检测能力。这样的扫描器也有他的弊端，扫描速度和插件加载速度呈现正比关系。由于大多数用户对于扫描频率和扫描时间的关注递增，扫描速度不再像以前那样受到更多的关注。好比经常体检的朋友，体检结果发布慢一点一般不会在意。下面咱们进入正题。

### 架构设计

插件式扫描器在方便人们使用和扩充的同时，对于研发人员要求也有所提高。咱们要将扫描器作为类似于工厂方法还要加入控制器、任务调度、结果输出、插件加载等一系列功能。咱们对于插件式轻量级扫描器进行架构设计。

![图片1.png](https://image.3001.net/images/20191122/1574395584_5dd75ec07fb5c.png!small)  

在图中咱们对于用户控制能力进行规划，用户通过控制器能够完成提供数据、任务生成、任务调度、结果输出。控制器中可设置全自动或半自动，方便用户的使用。插件加载器中可以加载扩充的插件，方便研发或相关人员扩展检测能力。

### 研发思路

接下来咱们对于如果去研发提供一些代码级的思路。这样能帮助咱们对于轻量级插件式扫描器更深入的理解。

#### 插件加载器

插件加载器是关键模块之一，通常情况下在Python之中咱们会使用到importlib模块，如果你打算使用 **import** ()
，在功能上的确是可行，但是通过Python官方文档得知并不值得推荐。咱们要考虑到在插件中定义一个固定方法用于执行插件，插件加载器类似于工厂方法。具体实现建议使用importlib.import_module()加载插件，插件加载之后调用run()方法，run()方法在每个独立插件中定义，用于插件的执行和返回结果。另外需要注意获得可用插件列表。

    
    
    代码示例：
    【ImportPlugin.py】
    import importlib
    plugin = importlib.import_module(PluginName)
    resulit = Plugin.run()
    return resulit
    

#### 扩展插件

插件相当于扫描器的灵魂，也就是核心部分。每款优秀的插件都需要研发或相关人员用心的编写，基于咱们此种模式，如何编写插件，需要值得注意的是run()方法作为承上启下。

    
    
    代码示例：
    【Scan.py】
    def scan(url):
    (扫描实现逻辑)
    return list
    def run(url):
        return scan(url)
    

#### 域名数据

域名数据属于扫描器的目标，这类数据需要用户通过控制器输入，输入方式可以分为单例、多例、大量。在单例中用户直接输入URL即可执行。在多例中用户需要输入URL，每个URL以逗号分隔，通过分隔函数将URL字符串转化列表，通过列表传递域名数据。在大量中建议使用文本存取或数据库存取的方式，每一行为单个域名。同样读取后通过列表传递域名数据。

#### 任务生成器

任务生成器能够将读取到的域名数据转换为任务列表或者任务队列以及任务链表进行存储，这种方式方便用于任务调度，任务调度包含任务启动、任务定时等等。实现方法并不唯一，需要根据业务需求或实际情况设计数据存储结构。生成的每项任务需要有独立且唯一的编号或特征，这样才能在之后的流程中方便控制。

#### 任务调度器

在任务调度时，要获得当前能够加载的插件列表以及任务列表。通过任务分配的方式将两者进行结合。Python已经有比较好用的插件，例如apscheduler或者huey等等。咱们在研发时追求使用比较方便推荐使用huey，但若稳定性要求较高则推荐apscheduler。任务调度器实现，将两者列表通过调度器分配执行。对于huey的使用进行简单演示。

    
    
    代码示例：
    【Huey.py】
    from huey import RedisHuey, crontab
    huey = RedisHuey('my-app', host='redis.myapp.com')
    @huey.task()
    def add_numbers(a, b):
        return a + b
    @huey.task(retries=2, retry_delay=60)
    def flaky_task(url):
        # This task might fail, in which case it will be retried up to 2 times
        # with a delay of 60s between retries.
        return this_might_fail(url)
    @huey.periodic_task(crontab(minute='0', hour='3'))
    def nightly_backup():
        sync_all_data()
    

#### 日志输出

每次个步骤执行之后，都应该有良好的日志输出，这样如果某流程出现问题，方便定位问题。推荐使用logging模块。

    
    
    代码示例：
    import logging
    logging.basicConfig(level=logging.INFO,format='%(asctime)s-%(levelname)s-%(message)s')
    try:
    (关键逻辑)
    except Exception as e:
    logger.warning(“告警信息”,e)
    else:
    logger.info(“提示信息”)
    

#### 控制器

对于整体的流程进行控制，起到中转的作用的同时也将扫描器的执行结果进行输出。模块所涉及的只有各个模块之间的调用逻辑关系，就不再老生常谈。

### 总结

轻量级插件扫描器的逻辑功能咱们已经进行阐述和了解，它的优势在于研发难度低、研发速度快，但是不足之处检测逻辑全依靠于插件对于插件研发者功底要求较高，这种模型觉得比较适合中小型工具开发和维护。对于商业插件扫描器，还需要进一步研究和讨论。

