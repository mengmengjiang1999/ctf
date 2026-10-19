## 一 现状・问题

随着需求不断迭代，业务系统的业务代码突飞猛进，在你自豪于自己的代码量产出很高时，有没有回头看看线上真正的客户使用 **量** 又有多少呢？

~
费事费力耗费大量人力成本～上线的功能，可能一年没人使用，如果不进行适当的下线，就会增加系统维护成本，此时就需要计划删除无用代码。但是我们怎么知道真实线上的一行行代码层面，是否真实在使用，或者真实没人用，
**怎么可以放心删除下线功能呢！**

## 二 分析原因

 **实际上多数业务系统都会存在这个通病：线上僵尸代码**

  * 可能是前期产品对业务场景没有分析到位
  * 可能是研发期间需求功能偏离了正确方向
  * 可能是上线后因外界因素使客户业务量下降
  * ······

## 三 采取措施

问产品经理哪些能下线？ **NO** 没人敢承诺

观测 UMP 接口是否有流量？ **NO** 只知道接口维度，有流量的接口难道所有代码都有用么

 **使用 jacoco（Java Code Coverage）进行线上代码分析，对系统做瘦身。**

Jacoco 本质上是一个测试覆盖率工具，通过 ASM 字节码增强技术在源代码中加入探针从而获取代码覆盖率。Jacoco 主要是通过 Jave agent
在 main 函数执行之前通过指定方法在执行的代码中加入探针来记录代码是否被执行过。

> Java agent 是 Java 提供的一个启动参数，有别于代理方式的动态增强和 annotation processor
> 的编译时增强，该参数通过指定路径的 jar 包中的 premain 方法将在 main 方法执行之前被调用增强源代码，通过实现该方法我们可以对加载的
> Class 文件进行修改源代码增强，使用此技术的还有大部分 APM 工具。

[https://www.jacoco.org/jacoco/trunk/doc/index.html](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fwww.jacoco.org%2Fjacoco%2Ftrunk%2Fdoc%2Findex.html)

## 四。实践步骤

### 4.1 依赖 jacoco.ant

在工程内的 pom 中引入 jar 依赖

    
    
    <dependency>
        <groupId>org.jacoco</groupId>
        <artifactId>org.jacoco.ant</artifactId>
        <version>0.8.3</version>
    </dependency>
    <dependency>
         <groupId>org.apache.ant</groupId>
         <artifactId>ant</artifactId>
         <version>1.9.9</version>
     </dependency>
    
    
    
    

### 4.2 赋能 Rest 请求

添加一个 url 地址，通过 ant 执行 dump task 用于 Dump Coverage 文件，避免使用配置文件且同时需要运维同事帮忙操作的问题。

    
    
    @RestController
    @RequestMapping("/coverage")
    public class CoverageController {
    
        @PostMapping("dump")
        @NoCheckMenuPermission
        public Result<Boolean> dumpCoverageFile() {
            DumpTask dumpTask = new DumpTask();
            // dump文件地址
            dumpTask.setDestfile(new File("/export/Data/coverage/code-cover.exec"));
            // 多次dump追加形式
            dumpTask.setAppend(true);
            // 选一个空闲接口即可
            dumpTask.setPort(8840);
            // 默认本机
            dumpTask.setAddress("127.0.0.1");
            dumpTask.execute();
            return Result.succeed(true);
        }
    }
    
    
    
    

### 4.3 嵌入 jacocoagent

由于 jacoco 需要在服务端由 jacocoagent 增强的 jar 包，为了避免需要麻烦运维同事，通过 maven 依赖我们可以发现
org.jacoco.agent 这个 jar 包中包含由 jacocoagent 这个包，所以通过在部署的启动脚本添加以下命令即可通过解压的方式获得该
jar 包！

 **java 启动参数添加如下：存在多个 javaagent 时比如 pfinder 之类在其后添加即可。**

    
    
    #decompress file 解压依赖，获得jacocoagent.jar包，避免需要联系运维上传包
    jar -xvf $BASEDIR/lib/org.jacoco.agent-0.8.3.jar
    
    
    
    
    
    
    -javaagent:$BASEDIR/bin/jacocoagent.jar=includes=com.jdwl.*,output=tcpserver,port=8840,address=127.0.0.1 -Xverify:none
    
    
    
    

![1691977836_64d9886ce6a272b3e41c3.png!small?1691977837496](https://image.3001.net/images/20230814/1691977836_64d9886ce6a272b3e41c3.png!small?1691977837496)

> premain 方法中我们可以通过 Instrumention 的 addTransformer 添加 ClassFileTransformer
> 接口的实现类，该接口中仅有一个方法如下，通过实现 ClassTransformer 我们可以定义自己的代码增强方法。可以使用 ASM，亦可以使用
> javasist 等高级类库。

> 相关实践：Diving Into Bytecode Manipulation: Creating an Audit Log With ASM and
> Javassist | New Reli

### 4.4 JDOS 资源预留

> 资源预留 /export 目录自定义处理

  *  **增加配置脚本 /home/admin/clean_export.sh（** 脚本默认内容上增加了 **& & $9 != "coverage"** **）**

输出的文件路径为 /export/Data/coverage/code-cover.exec

    
    
    #! /bin/bash
    
    ls -lh /export | awk 'NR >1 {print}' | awk '{if ($9 != "Data") print $9}' | xargs -i /bin/rm -rf /export/{} > /dev/null 2>&1
    ls -lh /export/Data | awk 'NR >1 {print}' | awk '{if ($9 != "jdos.jd.com" && $9 != "coverage") print $9}' | xargs -i /bin/rm -rf /export/Data/{} > /dev/null 2>&1
    
    
    
    

![1691977847_64d98877948fbeb914f5d.png!small?1691977848063](https://image.3001.net/images/20230814/1691977847_64d98877948fbeb914f5d.png!small?1691977848063)

### 4.5 下载 cover 文件

/export/Data/coverage/code-cover.exec

![1691977857_64d98881ed1f68b920dd2.png!small?1691977858361](https://image.3001.net/images/20230814/1691977857_64d98881ed1f68b920dd2.png!small?1691977858361)

登录堡垒机终端

    
    
    cd /export/Data/coverage
    
    

jdos 下载文件

    
    
    curl -s up.bastion.jd.com/file/up | bash
    
    

### 4.6 分析代码

 **打开 idea - > run -> show coverage data 选择对应的 exec 文件即可获取服务端的代码覆盖情况。**

 **绿色覆盖（活跃代码）**

![1691977864_64d98888eb5ae7fe0a392.png!small?1691977865398](https://image.3001.net/images/20230814/1691977864_64d98888eb5ae7fe0a392.png!small?1691977865398)

 **红色未覆盖（僵尸代码）**

![1691977871_64d9888f2324dab2bf146.png!small?1691977872001](https://image.3001.net/images/20230814/1691977871_64d9888f2324dab2bf146.png!small?1691977872001)

 **Reference**

  1. JaCoCo - Documentatio
  2. javaagent 使用指南 - rickiyang - 博客园 ([cnblogs.com](https://www.oschina.net/action/GoToLink?url=http%3A%2F%2Fcnblogs.com)
  3. 使用 Jacoco 统计服务端代码覆盖情况实践 - M104 - 博客园 ([cnblogs.com](https://www.oschina.net/action/GoToLink?url=http%3A%2F%2Fcnblogs.com)
  4. Diving Into Bytecode Manipulation: Creating an Audit Log With ASM and Javassist | New Reli

## 五。效能提升

### 5.1 需求交付效率提升

#### 5.1.1 缩短需求交付周期

因为僵尸代码删除，减少开发需求的范围，降低老代码认知成本，降低测试回归成本。

 **需求交付周期整体呈缩短趋势！2023/1 月落地实践，之前需求交付周期约 15 天，之后约 12 天。**

![1691977892_64d988a4546680f274672.png!small?1691977892788](https://image.3001.net/images/20230814/1691977892_64d988a4546680f274672.png!small?1691977892788)

#### 5.1.2 降低开发阶段停留时长

僵尸代码大量存在，研发认知需求改动点负荷很高，需要耗费大量时间成本。

 **2023/1 月落地后，开发阶段时长缩短到 4 天 以下（由 4.54 缩短至 3.11，缩短约 31%）** ，呈明显 **缩短趋势！**

![1691977900_64d988ac23b615d999338.png!small?1691977900764](https://image.3001.net/images/20230814/1691977900_64d988ac23b615d999338.png!small?1691977900764)

### 5.2 人效提升

#### 5.2.1 降低研发认知负荷

删除无用僵尸代码， **圈复杂度会大幅度降低，重复代码块也会降低** ，则研发认知负荷也会随之降低！

平均系统重复代码块数从 31 下降至 27 左右，降低了系统维护成本！

![1691977908_64d988b4048b98a21ceb5.png!small?1691977908370](https://image.3001.net/images/20230814/1691977908_64d988b4048b98a21ceb5.png!small?1691977908370)

#### 5.2.2 提升人均需求吞吐量

因为减少人力认知成本，缩小需求范围，所以会直接 **提升** 需求的吞吐量！

 **自从 2023/1 月落地实践后，人均需求的吞吐量也大幅度提升，从之前 1.5 提升到 2.5 左右。**

![1691977915_64d988bb6c21e3e54c312.png!small?1691977916061](https://image.3001.net/images/20230814/1691977915_64d988bb6c21e3e54c312.png!small?1691977916061)

### 5.3 过程质量提升

#### 5.3.1 减少自动化 bug 数

由于存量僵尸代码减少，则整体回滚用例和场景变得精简，黄金流程也不会被僵尸代码干扰，则自动化 bug 数也有明显 **下降趋势** ！

 **随着 2023 年 1 月以来的不断实践，自动化发现的 bug 数也逐月递减，从 11 个 / 月 - > 9 个 / 月 -> 6 个 / 月 ->
5 个 / 月。**

![1691977926_64d988c642c2a94d29423.png!small?1691977930461](https://image.3001.net/images/20230814/1691977926_64d988c642c2a94d29423.png!small?1691977930461)

#### 5.3.2 提升单测覆盖率

自从 2023 年 1 月落地实践后，随着删除掉大量僵尸代码，整体代码总量在减少，无效代码被无情下线，同时提升了单测代码覆盖率，呈 **上升趋势** ！
**单测行覆盖率从 51.33% - > 52.28%，提升系统质量！**

![1691977933_64d988cdcb7a26c32a7bf.png!small?1691977934374](https://image.3001.net/images/20230814/1691977933_64d988cdcb7a26c32a7bf.png!small?1691977934374)

![1691977945_64d988d908801c37c8712.png!small?1691977945538](https://image.3001.net/images/20230814/1691977945_64d988d908801c37c8712.png!small?1691977945538)

## 六。简要总结

  * 随着需求不断迭代交付，业务代码必然不断累积，运维成本不断升高，如果线上无用功能的代码一直残留，对研发来说是巨大的累赘！对于此类代码约定俗成为 **“僵尸代码”** 。
  * 赶快利用 jacoco 探针深入分析系统的一行行代码，看到线上功能运行最真实的一面，参照代码的覆盖情况，针对性下线和删除僵尸代码， **让系统瘦身，让研发减负！**

> 作者：京东物流 周奕儒
>
> 来源：京东云开发者社区 自猿其说 Tech

