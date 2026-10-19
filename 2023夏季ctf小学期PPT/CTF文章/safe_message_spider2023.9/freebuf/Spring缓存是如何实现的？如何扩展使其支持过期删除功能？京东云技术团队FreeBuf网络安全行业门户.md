**前言：** 在我们的应用中，有一些数据是通过rpc获取的远端数据，该数据不会经常变化，允许客户端在本地缓存一定时间。

该场景逻辑简单，缓存数据较小，不需要持久化，所以不希望引入其他第三方缓存工具加重应用负担，非常适合使用Spring Cache来实现。

但有个问题是，我们希望将这些rpc结果数据缓存起来，并在一定时间后自动删除，以实现在一定时间后获取到最新数据。类似Redis的过期时间。

接下来是我的调研步骤和开发过程。

## Spring Cache 是什么？

Spring Cache 是 Spring 的一个缓存抽象层，作用是在方法调用时自动缓存返回结果，以提高系统性能和响应速度。  
目标是简化缓存的使用，提供一致的缓存访问方式，使开发人员能够轻松快速地将缓存添加到应用程序中。  
应用于方法级别，在下次调用相同参数的方法时，直接从缓存中获取结果，而不必执行实际的方法体。

## 适用场景？

包括但不限于：

  * 频繁访问的方法调用，可以通过缓存结果来提高性能

  * 数据库查询结果，可以缓存查询结果以减少数据库访问

  * 外部服务调用结果，可以缓存外部服务的响应结果以减少网络开销

  * 计算结果，可以缓存计算结果以加快后续计算速度

## 优缺点

优点：

  * 提高应用的性能，避免重复计算或查询。

  * 减少对底层资源的访问，如数据库或远程服务，从而减轻负载。

  * 简化代码，通过注解的方式实现缓存逻辑，而不需要手动编写缓存代码。

缺点：

  * 需要占用一定的内存空间来存储缓存数据。

  * 可能导致数据不一致问题，如果缓存的数据发生变化，但缓存没有及时更新，可能会导致脏数据的问题。（所以需要及时更新缓存）

  * 可能引发缓存穿透问题，当大量请求同时访问一个不存在于缓存中的键时，会导致请求直接落到底层资源，增加负载。

## 重要组件

  1. CacheManager：缓存管理器，用于创建、配置和管理缓存对象。可以配置具体的缓存实现，如 Ehcache、Redis。

  2. Cache：缓存对象，用于存储缓存数据，提供了读取、写入和删除缓存数据的方法。

  3. 常用注解：

    * @Cacheable：被调用时，会检查缓存中是否已存在，若有，则直接返回缓存结果，否则执行方法并将结果存入缓存，适用于只读操作。

    * @CachePut：则每次都会执行方法体，并将结果存入缓存，即每次都会更新缓存中的数据，适用于写操作。

    * @CacheEvict：被调用时，Spring Cache 会清除对应的缓存数据。

## 使用方式

  1. 配置缓存管理器（CacheManager）：使用 `@EnableCaching`注解启用缓存功能，并配置具体的缓存实现。

  2. 在方法上添加缓存注解：使用 `@Cacheable`、`@CacheEvict`、`@CachePut`等注解标记需要被缓存的方法。

  3. 调用被缓存的方法：当调用被标记为缓存的方法时，Spring Cache 会检查缓存中是否已有该方法的缓存结果。

  4. 根据缓存结果返回数据：如果缓存中已有结果，则直接从缓存中返回；否则，执行方法并将结果存入缓存。

  5. 根据需要清除或更新缓存：使用 `@CacheEvict`、`@CachePut`注解可以在方法调用后清除或更新缓存。  
通过以上步骤，Spring Cache 可以自动管理缓存的读写操作，从而简化缓存的使用和管理。

## Spring Boot默认使用哪种实现，及其优缺点：

Spring
Boot默认使用`ConcurrentMapCacheManager`作为缓存管理器的实现，适用于简单的、单机的、对缓存容量要求较小的应用场景。

  * 优点：

    1. 简单轻量：没有外部依赖，适用于简单的应用场景。

    2. 内存存储：缓存数据存储在内存中的`ConcurrentMap`中，读写速度快，适用于快速访问和频繁更新的数据。

    3. 多缓存实例支持：支持配置多个命名缓存实例，每个实例使用独立的`ConcurrentMap`存储数据，可以根据不同的需求配置多个缓存实例。

  * 缺点：

    1. 单机应用限制：`ConcurrentMapCacheManager`适用于单机应用，缓存数据存储在应用的内存中，无法实现分布式缓存。

    2. 有限的容量：由于缓存数据存储在内存中，`ConcurrentMapCacheManager`的容量受限于应用的内存大小，对于大规模数据或高并发访问的场景可能存在容量不足的问题。

    3. 缺乏持久化支持：`ConcurrentMapCacheManager`不支持将缓存数据持久化到磁盘或其他外部存储介质，应用重启后缓存数据会丢失。

## 如何让`ConcurrentMapCacheManager`支持过期自动删除

前言也提到了，我们的场景逻辑简单，缓存数据较小，不需要持久化，不希望引入其他第三方缓存工具加重应用负担，适合使用`ConcurrentMapCacheManager`。所以扩展下`ConcurrentMapCacheManager`也许是最简单的实现。

### 方案设计

为此，我设计了三种方案：

  1. 开启定时任务，扫描缓存，定时删除所有缓存；该方式简单粗暴，统一定时删除，但不能针对单条数据进行过期操作。

  2. 开启定时任务，扫描缓存，并将单条过期的缓存数据删除。

  3. 访问缓存数据之前，判断是否过期，若过期则重新执行方法体，并将结果覆盖原缓存数据。

上述2、3方案都更贴近目标，且都有一个共同的难点，即如何判断该缓存是否过期？或如何存放缓存的过期时间？  
既然没有好办法，那就走一波源码找找思路吧！

### 源码解析

`ConcurrentMapCacheManager`中定义了一个`cacheMap`(如下代码)，用于存储所有缓存名及对应缓存对象。

    
    
    private final ConcurrentMap<String, Cache> cacheMap = new ConcurrentHashMap<>(16);
    

`cacheMap`中的存放的`Cache`的具体类型为`ConcurrentMapCache`，  
而`ConcurrentMapCache`的内部定义了一个`store`(如下代码)，用于存储该缓存下所有key、value，即真正的缓存数据。

    
    
    private final ConcurrentMap<Object, Object> store;
    

其关系图为：

![img_2.png](https://image.3001.net/images/20230821/1692585258_64e2cd2aaa145f8f018aa.png!small)

以下为测试代码，为一个查询增加缓存操作：cacheName=getUsersByName,key为参数name的值，value为查询用户集合。

    
    
    @Service
    public class UserServiceImpl implements UserService {
        @Autowired
        private UserMapper userMapper;
    
        @Override
        @Cacheable(value = "getUsersByName", key = "#name")
        public List<GyhUser> getUsersByName(String name) {
            return userMapper.getUsersByName(name);
        }
    }
    

当程序调用到此方法前，会自动进入缓存拦截器`CacheInterceptor`，进而进入`ConcurrentMapCacheManager`的`getCache`方法，获取对应的缓存实例，若不存在，则生成一个。  
![img_1.png](https://image.3001.net/images/20230821/1692585259_64e2cd2b26ae500069e99.png!small)  
然后从缓存实例中查找缓存数据，找到则返回，找不到则执行目标方法。  
![img_3.png](https://image.3001.net/images/20230821/1692585259_64e2cd2bda60b355743b4.png!small)

执行完目标方法后，将返回结果放到缓存中。  
![img_4.png](https://image.3001.net/images/20230821/1692585260_64e2cd2c57fcc30252468.png!small)

### 实现自动过期删除

根据上面的代码跟踪可以发现，缓存数据key/value存放在具体的缓存实例`ConcurrentMapCache`的`store`中，且get和put前后，有我可以操作的空间。

  1. 那么，如果我将value重新包装一下，将缓存时间封装进去，并在get和put前后，将真正的缓存数据解析出来，供开发者使用，是否可以实现呢？说干就干！

    
    
    /**
     * 缓存数据包装类，保证缓存数据及插入时间
     */
    public class ExpireCacheWrap {
        /**
         * 缓存数据
         */
        private final Object value;
        /**
         * 插入时间
         */
        private final Long insertTime;
    
        public ExpireCacheWrap(Object value, Long insertTime) {
            this.value = value;
            this.insertTime = insertTime;
        }
    
        public Object getValue() {
            return value;
        }
    
        public Long getInsertTime() {
            return this.insertTime;
        }
    }
    

  2. 自定义一个`Cache`类，继承`ConcurrentMapCache`，扩展get、put方法，实现对缓存时间的记录和解析

    
    
    /**
     * 缓存过期删除
     */
    public class ExpireCache extends ConcurrentMapCache {
        public ExpireCache(String name) {
            super(name);
        }
    
        @Override
        public ValueWrapper get(Object key) {
            // 解析缓存对象时，拿到value，去掉插入时间。对于业务中缓存的使用逻辑无感知无侵入，无需调整相关代码
            ValueWrapper valueWrapper = super.get(key);
            if (valueWrapper == null) {
                return null;
            }
            Object storeValue = valueWrapper.get();
            storeValue = storeValue != null ? ((ExpireCacheWrap) storeValue).getValue() : null;
            return super.toValueWrapper(storeValue);
        }
    
        @Override
        public void put(Object key, @Nullable Object value) {
            // 插入缓存对象时，封装对象信息：缓存内容+插入时间
            value = new ExpireCacheWrap(value, System.currentTimeMillis());
            super.put(key, value);
        }
    }
    

  3. 自定义缓存管理器，将自定义的`ExpireCache`，替换默认的`ConcurrentMapCache`

    
    
    /**
     * 缓存管理器
     */
    public class ExpireCacheManager extends ConcurrentMapCacheManager {
        @Override
        protected Cache createConcurrentMapCache(String name) {
            return new ExpireCache(name);
        }
    }
    

  4. 将自定义的缓存管理器`ExpireCacheManager`注入到容器中

    
    
    @Configuration
    class ExpireCacheConfiguration {
        @Bean
        public ExpireCacheManager cacheManager() {
            ExpireCacheManager cacheManager = new ExpireCacheManager();
            return cacheManager;
        }
    }
    

  5. 开启定时任务，自动删除过期缓存

    
    
    /**
     * 定时执行删除过期缓存
     */
    @Component
    @Slf4j
    public class ExpireCacheEvictJob {
    
        @Autowired
        private ExpireCacheManager cacheManager;
        /**
         * 缓存名与缓存时间
         */
        private static Map<String, Long> cacheNameExpireMap;
        // 可以优化到配置文件或字典中
        static {
            cacheNameExpireMap = new HashMap<>(5);
            cacheNameExpireMap.put("getUserById", 180000L);
            cacheNameExpireMap.put("getUsersByName", 300000L);
        }
    
        /**
         * 5分钟执行一次
         */
        @Scheduled(fixedRate = 300000)
        public void cacheEvict() {
            Long now = System.currentTimeMillis();
            // 获取所有缓存
            Collection<String> cacheNames = cacheManager.getCacheNames();
            for (String cacheName : cacheNames) {
                // 该类缓存设置的过期时间
                Long expire = cacheNameExpireMap.get(cacheName);
                // 获取该缓存的缓存内容集合
                Cache cache = cacheManager.getCache(cacheName);
                ConcurrentMap<Object, Object> store = (ConcurrentMap) cache.getNativeCache();
                Set<Object> keySet = store.keySet();
                // 循环获取缓存键值对，根据value中存储的插入时间，判断key是否已过期，过期则删除
                keySet.stream().forEach(key -> {
                    // 缓存内容包装对象
                    ExpireCacheWrap value = (ExpireCacheWrap) store.get(key);
                    // 缓存内容插入时间
                    Long insertTime = value.getInsertTime();
                    if ((insertTime + expire) < now) {
                        cache.evict(key);
                        log.info("key={},insertTime={},expire={},过期删除", key, insertTime, expire);
                    }
                });
            }
    
        }
    }
    

* * *

通过以上操作，实现了让`ConcurrentMapCacheManager`支持过期自动删除，并且对开发者基本无感知无侵入，只需要在配置文件中配置缓存时间即可。

但是如果我的项目已经支持了第三方缓存如Redis，秉着不用白不用的原则，又该如何将该功能嫁接到Redis上呢？

正正好我们的项目最近在引入R2m，就试着搞一下吧^-^。

未完待续~Thanks~

> 作者：京东科技 郭艳红
>
> 来源：京东云开发者社区

