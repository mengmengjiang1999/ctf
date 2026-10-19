**作者：贾世闻**

我们在开发应用后端系统的时候经常要和各种数据库、缓存等资源打交道。这一期，我们聊聊如何访问redis 并将资源池化。

在一个应用后端程序访问redis主要要做的工作有两个，单例和池化。

在后端应用集成redis，我们主要用到以下几个crate:​ ​once_cell​​​、​ ​redis-rs​​​、​
​r2d2​​​.once_cell 实现单例；redis-rs 是 redis的 rust 驱动；r2d2 是一个池化连接的工具包。本期代码均出现在​
​fullstack-rs​​​项目中。​ ​fullstack-rs​​​是我新开的一个实验性项目，目标是做一个类似​ ​gin-vue-admin​​的集成开发框架。

redis资源的定义主要是在​
​[github.com/jiashiwen/f…](https://link.juejin.cn?target=https%3A%2F%2Fgithub.com%2Fjiashiwen%2Ffullstack-rs%2Fblob%2Fmain%2Fbackend%2Fsrc%2Fresources%2Fredis_resource.rs%25E2%2580%258B%25E2%2580%258B%25C2%25A0%25E4%25B8%25AD%25E5%25AE%259E%25E7%258E%25B0%25E7%259A%2584%25E3%2580%2582
"https://github.com/jiashiwen/fullstack-rs/blob/main/backend/src/resources/redis_resource.rs%E2%80%8B%E2%80%8B%C2%A0%E4%B8%AD%E5%AE%9E%E7%8E%B0%E7%9A%84%E3%80%82")

一、redis-rs 封装

在实际开发中，我们面对的redis资源可能是单实例也有可能是集群，在这里我们对redis-rs进行了简单封装，便于适应这两种情况。

    
    
    #[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize, Clone)]
    #[serde(rename_all = "lowercase")]
    pub struct RedisInstance {
        #[serde(default = "RedisInstance::urls_default")]
        pub urls: Vec<String>,
        #[serde(default = "RedisInstance::password_default")]
        pub password: String,
        #[serde(default = "RedisInstance::instance_type_default")]
        pub instance_type: InstanceType,
    }
    复制代码

RedisInstance,定义redis资源的描述，与配置文件相对应。详细的配置描述可以参考 ​
​[github.com/jiashiwen/f…](https://link.juejin.cn?target=https%3A%2F%2Fgithub.com%2Fjiashiwen%2Ffullstack-rs%2Fblob%2Fmain%2Fbackend%2Fsrc%2Fconfigure%2Fconfig_global.rs%25E2%2580%258B%25E2%2580%258B%25C2%25A0%25E6%2596%2587%25E4%25BB%25B6%25E4%25B8%25AD
"https://github.com/jiashiwen/fullstack-rs/blob/main/backend/src/configure/config_global.rs%E2%80%8B%E2%80%8B%C2%A0%E6%96%87%E4%BB%B6%E4%B8%AD")RedisConfig
和 RedisPool 两个 struct 描述。

    
    
    #[derive(Clone)]
    pub enum RedisClient {
        Single(redis::Client),
        Cluster(redis::cluster::ClusterClient),
    }
    
    
    impl RedisClient {
        pub fn get_redis_connection(&self) -> RedisResult<RedisConnection> {
            return match self {
                RedisClient::Single(s) => {
                    let conn = s.get_connection()?;
                    Ok(RedisConnection::Single(Box::new(conn)))
                }
                RedisClient::Cluster(c) => {
                    let conn = c.get_connection()?;
                    Ok(RedisConnection::Cluster(Box::new(conn)))
                }
            };
        }
    }
    
    
    pub enum RedisConnection {
        Single(Box<redis::Connection>),
        Cluster(Box<redis::cluster::ClusterConnection>),
    }
    
    
    impl RedisConnection {
        pub fn is_open(&self) -> bool {
            return match self {
                RedisConnection::Single(sc) => sc.is_open(),
                RedisConnection::Cluster(cc) => cc.is_open(),
            };
        }
    
    
        pub fn query<T: FromRedisValue>(&mut self, cmd: &redis::Cmd) -> RedisResult<T> {
            return match self {
                RedisConnection::Single(sc) => match sc.as_mut().req_command(cmd) {
                    Ok(val) => from_redis_value(&val),
                    Err(e) => Err(e),
                },
                RedisConnection::Cluster(cc) => match cc.req_command(cmd) {
                    Ok(val) => from_redis_value(&val),
                    Err(e) => Err(e),
                },
            };
        }
    }
    复制代码

RedisClient 和 RedisConnection 对redis 的链接进行了封装，用来实现统一的调用接口。

二、基于 r2d2 实现 redis 连接池

以上，基本完成的reids资源的准备工作，下面来实现一个redis链接池。

    
    
    #[derive(Clone)]
    pub struct RedisConnectionManager {
        pub redis_client: RedisClient,
    }
    
    
    impl r2d2::ManageConnection for RedisConnectionManager {
        type Connection = RedisConnection;
        type Error = RedisError;
    
    
        fn connect(&self) -> Result<RedisConnection, Self::Error> {
            let conn = self.redis_client.get_redis_connection()?;
            Ok(conn)
        }
    
    
        fn is_valid(&self, conn: &mut RedisConnection) -> Result<(), Self::Error> {
            match conn {
                RedisConnection::Single(sc) => {
                    redis::cmd("PING").query(sc)?;
                }
                RedisConnection::Cluster(cc) => {
                    redis::cmd("PING").query(cc)?;
                }
            }
            Ok(())
        }
    
    
        fn has_broken(&self, conn: &mut RedisConnection) -> bool {
            !conn.is_open()
        }
    }
    复制代码

利用 r2d2 来实现连接池需要实现 r2d2::ManageConnection trait。connect 函数获取连接；is_valid
函数校验连通性；has_broken 判断连接是否崩溃不可用。

    
    
    pub fn gen_redis_conn_pool() -> Result<Pool<RedisConnectionManager>> {
        let config = get_config()?;
        let redis_client = config.redis.instance.to_redis_client()?;
        let manager = RedisConnectionManager { redis_client };
        let pool = r2d2::Pool::builder()
            .max_size(config.redis.pool.max_size as u32)
            .min_idle(Some(config.redis.pool.mini_idle as u32))
            .connection_timeout(Duration::from_secs(
                config.redis.pool.connection_timeout as u64,
            ))
            .build(manager)?;
        Ok(pool)
    }
    复制代码

gen_redis_conn_pool 函数用来生成一个 redis 的连接池，根据配置文件来指定连接池的最大连接数，最小闲置连接以及连接超时时长。

三、连接池单例实现****

在后端开发中，对于单一资源一般采取单例模式避免重复产生实例的开销。下面来聊一聊如果构建一个全局的 redis 资源。

这一部分代码在​
​[github.com/jiashiwen/f…](https://link.juejin.cn?target=https%3A%2F%2Fgithub.com%2Fjiashiwen%2Ffullstack-rs%2Fblob%2Fmain%2Fbackend%2Fsrc%2Fresources%2Finit_resources.rs%25E2%2580%258B%25E2%2580%258B%25C2%25A0%25E6%2596%2587%25E4%25BB%25B6%25E4%25B8%25AD%25E3%2580%2582
"https://github.com/jiashiwen/fullstack-rs/blob/main/backend/src/resources/init_resources.rs%E2%80%8B%E2%80%8B%C2%A0%E6%96%87%E4%BB%B6%E4%B8%AD%E3%80%82")

    
    
    pub static GLOBAL_REDIS_POOL: OnceCell<r2d2::Pool<RedisConnectionManager>> = OnceCell::new();
    复制代码

利用 OnceCell 构建全局静态变量。

    
    
    fn init_global_redis() {
        GLOBAL_REDIS_POOL.get_or_init(|| {
            let pool = match gen_redis_conn_pool() {
                Ok(it) => it,
                Err(err) => panic!("{}", err.to_string()),
            };
            pool
        });
    }
    复制代码

init_global_redis 函数，用来初始化 GLOBAL_REDIS_POOL
全局静态变量。在一般的后端程序中，资源是强依赖，所以，初始化简单粗暴，要么成功要么 panic。

四、资源调用

准备好 redis 资源后，我们聊聊如何调用。

调用例子在这里​
​[github.com/jiashiwen/f…](https://link.juejin.cn?target=https%3A%2F%2Fgithub.com%2Fjiashiwen%2Ffullstack-rs%2Fblob%2Fmain%2Fbackend%2Fsrc%2Fhttpserver%2Fservice%2Fservice_redis.rs%25E2%2580%258B%25E2%2580%258B
"https://github.com/jiashiwen/fullstack-rs/blob/main/backend/src/httpserver/service/service_redis.rs%E2%80%8B%E2%80%8B")

    
    
    pub fn put(kv: KV) -> Result<()> {
        let conn = GLOBAL_REDIS_POOL.get();
        return match conn {
            Some(c) => {
                c.get()?
                    .query(redis::cmd("set").arg(kv.Key).arg(kv.Value))?;
                Ok(())
            }
            None => Err(anyhow!("redis pool not init")),
        };
    }
    复制代码

​
​[github.com/jiashiwen/f…](https://link.juejin.cn?target=https%3A%2F%2Fgithub.com%2Fjiashiwen%2Ffullstack-rs%2Ftree%2Fmain%2Fbackend%25E2%2580%258B%25E2%2580%258B%25C2%25A0%25E8%25BF%2599%25E4%25B8%25AA%25E5%25B7%25A5%25E7%25A8%258B%25E9%2587%258C%25E6%259C%2589%25E4%25BB%258Ehttp%25E5%2585%25A5%25E5%258F%25A3%25E5%25BC%2580%25E5%25A7%258B%25E5%2588%25B0%25E5%2586%2599%25E5%2585%25A5redis%25E7%259A%2584%25E5%25AE%258C%25E6%2595%25B4%25E6%25B5%2581%25E7%25A8%258B%25EF%25BC%258Chttp
"https://github.com/jiashiwen/fullstack-rs/tree/main/backend%E2%80%8B%E2%80%8B%C2%A0%E8%BF%99%E4%B8%AA%E5%B7%A5%E7%A8%8B%E9%87%8C%E6%9C%89%E4%BB%8Ehttp%E5%85%A5%E5%8F%A3%E5%BC%80%E5%A7%8B%E5%88%B0%E5%86%99%E5%85%A5redis%E7%9A%84%E5%AE%8C%E6%95%B4%E6%B5%81%E7%A8%8B%EF%BC%8Chttp")server
不在本文讨论之列，就不赘述了，有兴趣的同学可以去github看看。

咱们下期见。

