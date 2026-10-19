# 1\. CCSP简介  

![图1.png](https://image.3001.net/images/20200203/1580740737_5e3830814bf45.png!small)

(ISC)2与云安全联盟Cloud Security Alliance (CSA)合作，于2015年针对云安全推出了一项专业认证项目，即Certified
Cloud Security Professional（CCSP），该认证秉承了(ISC)2系列认证的诸多优点，包括供应商无关性（Vendor
Agnostic），“英亩之宽、英尺之深”，ISO/IEC 17024认证，等等。CCSP认证特别适合的组织角色如下（包括但不限于）：  

    
    
    企业架构师/云架构师
    安全架构师/安全管理员/安全工程师/安全顾问
    首席信息官CIO/首席信息安全官CISO
    安全主管/IT主管/IT经理  
    

CCSP认证与另一云安全热门认证CCSK相比，前者侧重于更深入、更前言和基于实际经验的云安全知识体系，后者则强调广泛的、实践的和作为基线的云安全知识，二者的关系如下图所示：  

![图2.png](https://image.3001.net/images/20200203/1580740833_5e3830e1734a1.png!small)

值得注意的是，(ISC)2此前发布了新的CCSP考试大纲，并已于2019年8月1日开始生效，但就目前笔者掌握的各类备考资料，包括官方Common Base
Knowledge（CBK），尚未对新版考试大纲进行适应性更新，新旧考试大纲的比较将在第3章解读。

就CCSP新大纲而言，获取CCSP认证需要通过的考试形式为多项选择题（4个选项中选择1个最佳答案），以及排序题、连线题等新题型，考试时长为3个小时，共计125道题。考试大纲将云安全知识体系分为6个知识域，每个知识域在考试中的占比如下：

![图3.png](https://image.3001.net/images/20200203/1580740867_5e383103549fa.png!small)

CCSP认证考试由(ISC)2委托Pearson VUE全球授权考试中心进行，考试方式为Computer Based
Test（CBT），即在考试中心提供的计算机上答题，考试结束后一般会立即输出是否通过的结果。由于CCSP认证考试目前在中国大陆尚无考点，因此获取该认证需要赴境外参加考试。

根据(ISC)2提供的持证人员统计，截止2020年1月1日，CCSP全球持证人员为6916名，其中43名来自中国大陆。预计随着业务驱动下的云计算的快速增长，全球CCSP持证人员的数量将进一步增长。

# 2\. CCSP与CISSP的关系  

作为(ISC)2和CSA的合作项目，CCSP认证既融合了CSA在云安全领域的持续研究和最佳实践，同时也保持与(ISC)2的安全认证知识体系的一脉相承。相信许多同行与笔者一样此前已持有CISSP认证，而CCSP可以认为是CISSP安全知识体系在云上的应用和拓展，因此，笔者总结了CISSP的8个安全知识域与CCSP的映射关系，如下图所示：  

![图4.png](https://image.3001.net/images/20200203/1580740965_5e383165d686e.png!small)  

## D1-Cloud Concepts, Architecture and Design  

CISSP无对应知识域。

## D2-Cloud Data Security  

CISSP-D2：数据安全生命周期在云中的应用，关注云环境下的多租户数据机密性、数据销毁、数据保留、数据发现问题。

## D3-Cloud Platform & Infrastructure Security  

CISSP-D3：数据中心物理安全，关注云数据中心的冗余策略、访问控制、安全审计问题；

CISSP-D3：基础设施安全，关注云数据中心的电力/通信冗余、业务连续性/灾难恢复（BC/DR）设计问题。

## D4-Cloud Application Security  

CISSP-D5：身份与访问管理（IAM）的应用，关注云应用程序特别是SaaS的身份认证和授权问题，以及云访问安全代理CASB的应用；

CISSP-D6：安全测试技术如漏洞测试、渗透测试、静态应用程序安全测试（SAST）、动态应用程序安全测试（DAST）等在云环境下的应用；

CISSP-D8：软件安全开发生命周期在云应用程序安全开发中的应用。

## D5-Cloud Security Operations  

CISSP-D7：事件管理、问题管理、变更管理、配置管理、补丁管理等运营安全管理在云环境下的应用；

CISSP-D7：BC/DR在云环境下的策略和过程；

CISSP-D7：电子取证技术在云环境下的应用，特别是对多租户的影响考虑。

## D6-Legal, Risk and Compliance  

CISSP-D1：企业架构、安全架构在云环境下的应用；

CISSP-D1：云环境下对于知识产权如版权、商标、专利、商业秘密的特定考虑；

CISSP-D1：各国信息安全/隐私法律法规对于云数据中心的合规性要求，特别是跨越多个司法管辖区的云环境的合规性难题。

# 3\. 新考纲变化解读  

(ISC)2此前发布了新版考试大纲Exam
Outline并已于2019年8月1日生效，相比较上一个版本的考试大纲（2015年4月生效），新版考试大纲依据云计算的发展现状，以及知识体系的完备性和一致性，做了一些调整。从总体上看，笔者认为变化不大，使用现有的学习材料足够通过考试。

新版考试的变化如下：

## D1-Cloud Concepts, Architecture and Design

1.2 Impact of Related Technologies (e.g., machine learning, artificial
intelligence, blockchain, Internet of Things (IoT), containers, quantum
computing) – _新增_

1.3 Virtualization Security (e.g., container security) – _新增_

##  D2-Cloud Data Security  

2.1 Data Dispersion – _新增_

2.4 Implement Data Discovery Structured Data, Unstructured Data – _新增_

2.7 Legal Hold – _新增_

##  D3-Cloud Platform & Infrastructure Security  

3.2 Design a Secure Data Center – _调整，包含在旧大纲的D5中_

##  D4-Cloud Application Security  

4.5 Third Party Software Management, Validated Open Source Software – _新增_

4.7 Cloud Access Security Broker (CASB) – _新增_

##  D5-Cloud Security Operations  

5.5 Collect, Acquire and Preserve Digital Evidence – _新增_

5.7 Manage Security Operations – _新增_

##  D6-Legal, Risk and Compliance  

6.2 Standard Privacy Requirements (e.g., International Organization for
Standardization/International Electrotechnical Commission (ISO/IEC) 27018,
Generally Accepted Privacy Principles (GAPP), General Data Protection
Regulation (GDPR)) – _新增_

#  4\. 备考实践（个人经验）  

## 4.1. 教材选择  

截止目前，CCSP认证考试可供参考的资料有6册，分别是：  

![图5.png](https://image.3001.net/images/20200203/1580741205_5e383255eecf5.png!small)

其中：

    
    
    “CCSP Official Study Guide”已于2019年12月发布了第二版，与新版考试大纲完全匹配；
    “CCSP CBK”将于2020年4月发布第三版，预计与新版考试大纲匹配。  
    

4.2. 学习建议  

尽管CCSP认证要求具有云相关的工作经验，以理解云安全知识体系，但是仅从通过CCSP认证考试的角度，笔者建议按照如下3个阶段学习备考：

 **阶段1：** 阅读教材，建议有云相关专业背景或实际经验的同行阅读“CCSP Official Study
Guide”，这本教材的优点是按照云安全体系的逻辑结构重新组织CCSP考试大纲的6个知识域，字里行间中无不体现作者对云安全实践的深刻理解；然而，建议具有较少云相关专业背景的同行阅读“CCSP
CBK”，这本教材以教科书式的语言详细描述了考试大纲的所有知识点，是一本不可多得的云安全零基础读本。

 **阶段2：** 模拟练习，完成“CCSP Practice Tests”和“CCSP Practice
Exams”两本习题集，笔者认为本阶段关注的不是正确率，而是通过完成这两本习题集掌握CCSP认证考试的出题思路和方法，更重要的是，对于错题需要重新回到教材中的相关章节进行研读，甚至需要查询网络资料和相关标准。

 **阶段3：** 冲刺，在阶段2的基础上查缺补漏，如果精力允许可以阅读CBK列出的相关标准（尽管笔者认为Official Study
Guide和CBK的内容足够通过考试），最后按照考试时间和题量完成1-2套模拟题，保持最佳心理状态直至完成考试。

## 4.3. 考点选择  

目前，由于中国大陆的Pearson
VUE考试中心尚未开考CCSP认证，因此中国大陆周边相对交通便利的考试地点有：中国香港、中国台湾、韩国、日本、新加坡。笔者选择距离中国首都最近的考点：韩国首尔考试中心。该中心位于韩国首尔中区的首尔交易所（The
Exchange
Seoul），附近酒店林立，住宿条件优越；有地铁和首尔火车站，交通便利；也有闻名遐迩的明洞购物街区和南大门市场，可以在考试后适当放松休憩，是比较理想的考点。此外，笔者赴韩考试期间，无论酒店食宿，还是参加考试，使用简单的英文都是可以正常交流的。

![图6.png](https://image.3001.net/images/20200203/1580741284_5e3832a4f0525.png!small)

## 4.4. 关于语言

关于CCSP认证考试的语言，是许多同行比较关注的，由于采用全球统一的英文考试，因此需要掌握一些IT特别是安全相关的英文词汇。笔者在学习备考中，收集记录不认识的英文词汇大于200余个，这些词汇很多都与笔者不太熟悉的领域如机房物理环境和IT基础设施相关。总的来看，英文不会是通过CCSP考试的根本障碍。

# 5. 后记  

通过CCSP认证一方面使得持证者获得高水平的认证和认可，展现自己的卓越和专业；另一方面，由于CCSP有着良好的知识体系，这将指导持证人在组织中审视和洞察云迁移和云运营的安全问题，为组织目标服务，从这个角度看，CCSP只是一个起点。

祝愿同行顺利通过CCSP考试获得认证，共同维护职业声誉，推动行业发展。

# 6. 参考资料  

1\. 云安全专家（CCSP）认证Pearson VUE香港考试攻略

<https://www.freebuf.com/articles/others-articles/194023.html>

2\. 认证云安全专家（CCSP）考试攻略

<https://www.freebuf.com/articles/others-articles/156324.html>

  

  

  

  

  

  

  

  

  

  

