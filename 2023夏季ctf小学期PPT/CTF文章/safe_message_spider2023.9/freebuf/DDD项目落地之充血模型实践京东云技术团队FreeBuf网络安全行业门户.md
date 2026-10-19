# 背景：

充血模型是DDD分层架构中实体设计的一种方案，可以使关注点聚焦于业务实现，可有效提升开发效率、提升可维护性；

# 1、DDD项目落地整体调用关系

调用关系图中的Entity为实体，从进入领域服务（Domin）时开始使用，直到最后返回。![](https://image.3001.net/images/20230807/1691373879_64d05137818e020453b0f.png!small)

# 2、实体设计

充血模型是实体设计的一种方法，简单来说，就是一种带有具体行为方法和聚合关联关系的特殊实体；

关于实体设计，需要明白的关键词为：领域服务->聚合->聚合根->实体->贫血模型->充血模型

![](https://image.3001.net/images/20230807/1691374105_64d05219a47d0bf2f3c2e.png!small)

## 聚合与聚合根:

聚合是一种关联关系，而聚合根就是这个关系成立的基础，没有聚合根，这个聚合关系就无法成立；

举个例子，存在3个实体：用户、用户组、用户组关联关系，这3个实体形成的关联关系就是聚合，而用户实体就是这个聚合中的聚合根；

![](https://image.3001.net/images/20230807/1691374106_64d0521a1e791e8ea9185.png!small)

  

## 实体：

定义在领域层，是领域层的重要元素，从领域划分到工程实践落地，都应该围绕实体进行，DDD中的实体和数据库表不只是1对1关系，可能是1对多或者仅为内存中的对象；

## 贫血模型：

实体不带有任何行为方法，也不带有聚合关联关系，作用基本相当于值对象（ValueObject），仅作为值传递的对象，和传统三层项目架构中的实体具有相同作用，不建议使用。补充说明：一般我们使用的DTO就可以被当做是值对象

![](https://image.3001.net/images/20230807/1691374106_64d0521a88a53cbfddca2.png!small)

  

## 充血模型：

实体中带有具有行为方法和聚合关联关系，行为方法是说create、save、delete等封装了一类可以指代行为的方法，比如在用户实体对象中具有用户组实体的引用，这样当我们需要操作用户组时，只通过用户实体进行操作就可以。

工程实践中，建议采用充血模型，好处是隐藏胶水代码，提升代码可读性，使关注点聚焦于业务实现。

![](https://image.3001.net/images/20230807/1691374107_64d0521b0169b290c288c.png!small)

## 充血模型在实践中的问题：

行为代码量过多，导致实体内部臃肿膨胀，难以阅读，难以维护，对于这种问题，我们需要根据实体行为的代码量多少来采取不同的解决方案。

## 解决方案：

场景1：行为不会导致实体臃肿的情况下，在实体中完成行为定义

    
    
    publicCooperateServicePackageConfigsave(){// 直接调用基础设施层进行保存cooperateServicePackageConfigRepository.save(this);returnthis;}

场景2：行为导致实体臃肿的情况下，采用外部定义行为的方式，核心思想是借助其他类实现行为代码定义，将臃肿代码外移，保留干净的实体行为：

1）创建工具类，将某个实体中的行为定义其中，实体负责调用该工具类

    
    
    publicCooperateServicePackageConfigsave(){// 将处理过程放在工具类中ServicePackageSaveUtils.save(this);returnthis;}

2）创建新实体，将该实体的使用场景明确至某个细分行为，比如一个聚合根（ExampleEntity）的保存可能涉及到5个实体的保存，那么我们定义一个ExampleSaveEntity实体，专门用来处理该聚合下的保存行为

![](https://image.3001.net/images/20230807/1691374107_64d0521b69f5021cb892f.png!small)

## 实践经验：

1、关于spring bean注入：充血模型在实体中使用静态注入方法实现。例：

    
    
    privateLabelInfoRepositorylabelInfoRepository =ApplicationContextUtils.getBean(LabelInfoRepository.class);

2、充血模型的实体序列化，排除非必要属性，在一些redis对象缓存时可能会用到。例：

    
    
    // 使用注解排除序列化属性@Getter(AccessLevel.NONE)privateLabelInfoRepositorylabelInfoRepository =ApplicationContextUtils.getBean(LabelInfoRepository.class);
    
    
    // 使用注解排除序列化属性@JSONField(serialize =false)privateServicePackageConfigservicePackageConfig;
    
    
    // 使用注解排除序列化 get 方法@Transient@JSONField(serialize =false)publicstaticCooperateServicePackageRepositoryQuerygetAllCodeQuery(LongcontractId){CooperateServicePackageRepositoryQueryrepositoryQuery =newCooperateServicePackageRepositoryQuery();repositoryQuery.setContractIds(com.google.common.collect.Lists.newArrayList(contractId));repositoryQuery.setCode(RightsPlatformConstants.CODE_ALL);returnrepositoryQuery;}

3、利用Set方法建立聚合绑定关系。例：

    
    
    publicvoidsetServiceSkuInfos(List<ServiceSkuInfo>serviceSkuInfos){if(CollectionUtils.isEmpty(serviceSkuInfos)){return;}this.serviceSkuInfos =serviceSkuInfos;List<String>allSkuNoSet =serviceSkuInfos
                                    .stream().map(one ->one.getSkuNo()).collect(Collectors.toList());StringskuJoinStr =Joiner.on(GlobalConstant.SPLIT_CHAR).join(allSkuNoSet);this.setSkuNoSet(skuJoinStr);}

> 作者：京东健康 张君毅
>
> 来源：京东云开发者社区

