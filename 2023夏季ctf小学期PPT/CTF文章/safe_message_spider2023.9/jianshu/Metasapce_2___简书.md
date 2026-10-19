Metasapce-2

[ 程序员札记](https://www.jianshu.com/u/6cee1dbc3f25)关注赞赏支持

# Metasapce-2

一、VirtualSpaceList  
VirtualSpaceList在hotspot
src/share/vm/memory/metaspace.cpp中，表示一个VirtualSpaceNode链表，负责创建和维护所有的VirtualSpaceNode。其定义的属性如下：

  

image.png

属性比较简单，重点关注以下方法的实现。

1、构造和析构函数

    
    
    VirtualSpaceList::VirtualSpaceList(size_t word_size) :
                                       _is_class(false),
                                       _virtual_space_list(NULL),
                                       _current_virtual_space(NULL),
                                       _reserved_words(0),
                                       _committed_words(0),
                                       _virtual_space_count(0) {
      //获取锁expand_lock
      MutexLockerEx cl(SpaceManager::expand_lock(),
                       Mutex::_no_safepoint_check_flag);
      //创建一个新的virtual_space     
      create_new_virtual_space(word_size);
    }
     
    bool VirtualSpaceList::create_new_virtual_space(size_t vs_word_size) {
      assert_lock_strong(SpaceManager::expand_lock());
      //创建compressed class的VirtualSpace不会走到此分支
      if (is_class()) {
        assert(false, "We currently don't support more than one VirtualSpace for"
                      " the compressed class space. The initialization of the"
                      " CCS uses another code path and should not hit this path.");
        return false;
      }
      
      if (vs_word_size == 0) {
        assert(false, "vs_word_size should always be at least _reserve_alignment large.");
        return false;
      }
     
      size_t vs_byte_size = vs_word_size * BytesPerWord;
      //内存取整
      assert_is_size_aligned(vs_byte_size, Metaspace::reserve_alignment());
     
      //创建一个新的节点
      VirtualSpaceNode* new_entry = new VirtualSpaceNode(vs_byte_size);
      if (!new_entry->initialize()) {
         //初始化失败，返回false
        delete new_entry;
        return false;
      } else {
        //初始化成功，校验结果
        assert(new_entry->reserved_words() == vs_word_size,
            "Reserved memory size differs from requested memory size");
        //同步结果
        OrderAccess::storestore();
        link_vs(new_entry);
        return true;
      }
    }
     
    void VirtualSpaceList::link_vs(VirtualSpaceNode* new_entry) {
      //插入到链表中
      if (virtual_space_list() == NULL) {
          set_virtual_space_list(new_entry);
      } else {
        current_virtual_space()->set_next(new_entry);
      }
      set_current_virtual_space(new_entry);
      //增加计数
      inc_reserved_words(new_entry->reserved_words());
      inc_committed_words(new_entry->committed_words());
      inc_virtual_space_count();
     
      if (TraceMetavirtualspaceAllocation && Verbose) {
        //打印日志
        VirtualSpaceNode* vsl = current_virtual_space();
        vsl->print_on(gclog_or_tty);
      }
    }
     
    void VirtualSpaceList::inc_reserved_words(size_t v) {
      assert_lock_strong(SpaceManager::expand_lock());
      _reserved_words = _reserved_words + v;
    }
     
    void VirtualSpaceList::inc_committed_words(size_t v) {
      assert_lock_strong(SpaceManager::expand_lock());
      _committed_words = _committed_words + v;
     
      assert_committed_below_limit();
    }
     
    #define assert_committed_below_limit()                             \
      assert(MetaspaceAux::committed_bytes() <= MaxMetaspaceSize,      \
          err_msg("Too much committed memory. Committed: " SIZE_FORMAT \
                  " limit (MaxMetaspaceSize): " SIZE_FORMAT,           \
              MetaspaceAux::committed_bytes(), MaxMetaspaceSize));
     
    void VirtualSpaceList::inc_virtual_space_count() {
      assert_lock_strong(SpaceManager::expand_lock());
      _virtual_space_count++;
    }
     
    VirtualSpaceList::VirtualSpaceList(ReservedSpace rs) :
                                       _is_class(true),
                                       _virtual_space_list(NULL),
                                       _current_virtual_space(NULL),
                                       _reserved_words(0),
                                       _committed_words(0),
                                       _virtual_space_count(0) {
      MutexLockerEx cl(SpaceManager::expand_lock(),
                       Mutex::_no_safepoint_check_flag);                 
      VirtualSpaceNode* class_entry = new VirtualSpaceNode(rs);
      bool succeeded = class_entry->initialize();
      if (succeeded) {
        link_vs(class_entry);
      }
    }
     
     
    VirtualSpaceList::~VirtualSpaceList() {
      //从链表头元素开始遍历，释放所有的VirtualSpaceNode
      VirtualSpaceListIterator iter(virtual_space_list());
      while (iter.repeat()) {
        VirtualSpaceNode* vsl = iter.get_next();
        delete vsl;
      }
    }
    

VirtualSpaceListIterator的实现非常简单，如下：

image.png

2、get_new_chunk  
get_new_chunk用于获取一个新的满足大小要求的Metachunk，是VirtualSpaceList的核心方法，其调用链如下：

image.png

源码实现如下：

    
    
    Metachunk* VirtualSpaceList::get_new_chunk(size_t chunk_word_size, size_t suggested_commit_granularity) {
     
      //从当前的VirtualSpaceNode节点分配一个Metachunk
      Metachunk* next = current_virtual_space()->get_chunk_vs(chunk_word_size);
      
      if (next != NULL) {
        //分配成功则返回
        return next;
      }
     
      //当前节点内存不足，需要扩展创建一个新的节点，扩展的量是根据要求分配的chunk_word_size内存大小计算的，而不是当前节点剩余的已提交内存
      //对chunk_word_size做内存取整
      size_t min_word_size       = align_size_up(chunk_word_size,              Metaspace::commit_alignment_words());
      size_t preferred_word_size = align_size_up(suggested_commit_granularity, Metaspace::commit_alignment_words());
      if (min_word_size >= preferred_word_size) {
        // Can happen when humongous chunks are allocated.
        preferred_word_size = min_word_size;
      }
      //按照min_word_size重新创建一个新的VirtualSpaceNode
      bool expanded = expand_by(min_word_size, preferred_word_size);
      if (expanded) {
         //如果创建成功，则使用新的节点创建一个Metachunk
        next = current_virtual_space()->get_chunk_vs(chunk_word_size);
        assert(next != NULL, "The allocation was expected to succeed after the expansion");
      }
     
       return next;
    }
     
     
    bool VirtualSpaceList::expand_by(size_t min_words, size_t preferred_words) {
      //校验参数
      assert_is_size_aligned(min_words,       Metaspace::commit_alignment_words());
      assert_is_size_aligned(preferred_words, Metaspace::commit_alignment_words());
      assert(min_words <= preferred_words, "Invalid arguments");
     
      //MetaspaceGC根据当前已经提交的总内存量和Metaspace最大内存量判断能否扩展
      if (!MetaspaceGC::can_expand(min_words, this->is_class())) {
        return  false;
      }
      size_t allowed_expansion_words = MetaspaceGC::allowed_expansion();
      if (allowed_expansion_words < min_words) {
        return false;
      }
     
      //因为preferred_words和allowed_expansion_words都是大于或者等于min_words，所以取两者的最小值也能满足要求
      size_t max_expansion_words = MIN2(preferred_words, allowed_expansion_words);
     
      //尝试当前节点扩展
      bool vs_expanded = expand_node_by(current_virtual_space(),
                                        min_words,
                                        max_expansion_words);
      //扩展成功
      if (vs_expanded) {
        return true;
      }
      //节点创建时申请的reserved_size的剩余空间不足导致扩展失败，回收当前节点
      retire_current_virtual_space();
     
      //取两者间的最大值，并做内存取整
      size_t grow_vs_words = MAX2((size_t)VirtualSpaceSize, preferred_words);
      grow_vs_words = align_size_up(grow_vs_words, Metaspace::reserve_alignment_words());
      //创建一个新的节点
      if (create_new_virtual_space(grow_vs_words)) {
         //pre_committed即创建的时候已经完成commited
        if (current_virtual_space()->is_pre_committed()) {
          // The memory was pre-committed, so we are done here.
          assert(min_words <= current_virtual_space()->committed_words(),
              "The new VirtualSpace was pre-committed, so it"
              "should be large enough to fit the alloc request.");
          return true;
        }
        //非pre_committed，需要手动commited
        return expand_node_by(current_virtual_space(),
                              min_words,
                              max_expansion_words);
      }
     
      return false;
    }
     
    bool VirtualSpaceList::expand_node_by(VirtualSpaceNode* node,
                                          size_t min_words,
                                          size_t preferred_words) {
      size_t before = node->committed_words();
      //节点expand事假调用VirtualSpace::expand_by方法扩展，如果成功返回true
      bool result = node->expand_by(min_words, preferred_words);
     
      size_t after = node->committed_words();
     
      // after and before can be the same if the memory was pre-committed.
      assert(after >= before, "Inconsistency");
      //增加已提交的内存量
      inc_committed_words(after - before);
     
      return result;
    }
     
    void VirtualSpaceList::retire_current_virtual_space() {
      assert_lock_strong(SpaceManager::expand_lock());
     
      VirtualSpaceNode* vsn = current_virtual_space();
     
      ChunkManager* cm = is_class() ? Metaspace::chunk_manager_class() :
                                      Metaspace::chunk_manager_metadata();
      //回收当前节点
      vsn->retire(cm);
    }
    

3、purge  
purge方法用于清理掉VirtualSpaceList中空闲的即没有任何Metachunk的VirtualSpaceNode节点，当VirtualSpaceList关联的ClassLoaderData被垃圾回收器清理掉了就会触发此方法，其调用链如下：

image.png

其源码实现如下：

    
    
    void VirtualSpaceList::purge(ChunkManager* chunk_manager) {
      //校验是否在安全点
      assert(SafepointSynchronize::is_at_safepoint(), "must be called at safepoint for contains to work");
      //校验获取锁
      assert_lock_strong(SpaceManager::expand_lock());
      
      VirtualSpaceNode* purged_vsl = NULL;
      //链表头
      VirtualSpaceNode* prev_vsl = virtual_space_list();
      VirtualSpaceNode* next_vsl = prev_vsl;
      while (next_vsl != NULL) {
        VirtualSpaceNode* vsl = next_vsl;
        next_vsl = vsl->next();
        //如果不包含任何Metachunk且不是当前节点，因为当前节点可能会被使用
        if (vsl->container_count() == 0 && vsl != current_virtual_space()) {
          //从链表中移除
          if (prev_vsl == vsl) {
           //如果是头节点，将头结点的下一个节点作为头结点
            // This is the case of the current node being the first node.
            assert(vsl == virtual_space_list(), "Expected to be the first node");
            set_virtual_space_list(vsl->next());
          } else {
            prev_vsl->set_next(vsl->next());
          }
          //回收该节点
          vsl->purge(chunk_manager);
          //减少计数器
          dec_reserved_words(vsl->reserved_words());
          dec_committed_words(vsl->committed_words());
          dec_virtual_space_count();
          purged_vsl = vsl;
          //释放节点
          delete vsl;
        } else {
          prev_vsl = vsl;
        }
      }
    }
    

二、ChunkManager  
1、定义  
ChunkManager用来管理全局的所有空闲Metachunk，与之类似的BlockFreelist用来管理所有的空闲Metablock。ChunkManager的定义位于metaspace.cpp中，定义的属性如下：

image.png

枚举值NumberOfFreeLists的定义如下：

image.png

即_free_chunks是一个长度为3的ChunkList数组，ChunkList是表示一个链表的模板类FreeList的别名，如下：

  

image.png

每个ChunkList对应一个固定大小的Metachunk列表，参考构造方法的实现，如下：

image.png

传入的specialized_size，small_size，medium_size实际是一个枚举值，参考Metaspace::global_initialize()中ChunkManager的初始化，如下：

image.png

ChunkTreeDictionary也是一个别名，一个支持查找和排序的二叉树模板类的别名，如下：

image.png

_humongous_dictionary表示大小跟上面这三种不一致的特殊的Metachunk链表，参考ChunkManager::list_index方法的实现，如下图：

  

image.png

free_chunks(MediumIndex)->size()并非返回这个Metachunk链表元素的个数，而是包含的Metachunk的大小。重点关注以下方法的实现。

2、 chunk_freelist_allocate  
chunk_freelist_allocate用于从空闲Metachunk链表中查找一个满足指定大小要求的Metachunk，该方法的调用链如下：

  

image.png

源码实现如下：

    
    
    Metachunk* ChunkManager::chunk_freelist_allocate(size_t word_size) {
     //获取锁
     assert_lock_strong(SpaceManager::expand_lock());
     //校验两个计数器的正确
     slow_locked_verify();
    
     //查找满足要求的Metachunk
     Metachunk* chunk = free_chunks_get(word_size);
     if (chunk == NULL) {
       return NULL;
     }
      //查找成功，校验结果
     assert((word_size <= chunk->word_size()) ||
            (list_index(chunk->word_size()) == HumongousIndex),
            "Non-humongous variable sized chunk");
     if (TraceMetadataChunkAllocation) {
       size_t list_count;
       //判断word_size对应哪种类型的Metachunk，获取对应类型的Metachunk链表的长度
       if (list_index(word_size) < HumongousIndex) {
         ChunkList* list = find_free_chunks_list(word_size);
         list_count = list->count();
       } else {
         list_count = humongous_dictionary()->total_count();
       }
       //打印日志
       gclog_or_tty->print("ChunkManager::chunk_freelist_allocate: " PTR_FORMAT " chunk "
                           PTR_FORMAT "  size " SIZE_FORMAT " count " SIZE_FORMAT " ",
                           this, chunk, chunk->word_size(), list_count);
       locked_print_free_chunks(gclog_or_tty);
     }
    
     return chunk;
    }
    
    void slow_locked_verify() {
       //metaspace_slow_verify默认为false，dubug模式下为true
       if (metaspace_slow_verify) {
         locked_verify();
       }
     }
    
    void ChunkManager::locked_verify() {
     locked_verify_free_chunks_count();
     locked_verify_free_chunks_total();
    }
    
    void ChunkManager::locked_verify_free_chunks_count() {
     assert_lock_strong(SpaceManager::expand_lock());
     //校验_free_chunks_count正确
     assert(sum_free_chunks_count() == _free_chunks_count,
       err_msg("_free_chunks_count " SIZE_FORMAT " is not the"
              " same as sum " SIZE_FORMAT, _free_chunks_count,
              sum_free_chunks_count()));
    }
    
    //统计总的空闲chunk数量
    size_t ChunkManager::sum_free_chunks_count() {
     assert_lock_strong(SpaceManager::expand_lock());
     size_t count = 0;
     //遍历数组_free_chunks
     for (ChunkIndex i = ZeroIndex; i < NumberOfFreeLists; i = next_chunk_index(i)) {
       ChunkList* list = free_chunks(i);
       if (list == NULL) {
         continue;
       }
       count = count + list->count();
     }
     count = count + humongous_dictionary()->total_free_blocks();
     return count;
    }
    
    void ChunkManager::locked_verify_free_chunks_total() {
     assert_lock_strong(SpaceManager::expand_lock());
     //校验_free_chunks_total正确
     assert(sum_free_chunks() == _free_chunks_total,
       err_msg("_free_chunks_total " SIZE_FORMAT " is not the"
              " same as sum " SIZE_FORMAT, _free_chunks_total,
              sum_free_chunks()));
    }
    
    //返回所有空闲chunk的总的内存大小
    size_t ChunkManager::sum_free_chunks() {
     assert_lock_strong(SpaceManager::expand_lock());
     size_t result = 0;
     //遍历数组_free_chunks
     for (ChunkIndex i = ZeroIndex; i < NumberOfFreeLists; i = next_chunk_index(i)) {
       ChunkList* list = free_chunks(i);
    
       if (list == NULL) {
         continue;
       }
       //链表中每个chunk的大小都是list->size()
       result = result + list->count() * list->size();
     }
     result = result + humongous_dictionary()->total_size();
     return result;
    }
    
    
    
    Metachunk* ChunkManager::free_chunks_get(size_t word_size) {
     //校验获取锁
     assert_lock_strong(SpaceManager::expand_lock());
     //校验计数器
     slow_locked_verify();
    
     Metachunk* chunk = NULL;
     //如果是通用规格的Metachunk
     if (list_index(word_size) != HumongousIndex) {
       //获取对应的链表
       ChunkList* free_list = find_free_chunks_list(word_size);
       assert(free_list != NULL, "Sanity check");
       //获取链表头元素
       chunk = free_list->head();
    
       if (chunk == NULL) {
         return NULL;
       }
    
       //不为空，则将头元素从链表中移除
       free_list->remove_chunk(chunk);
    
       if (TraceMetadataChunkAllocation && Verbose) {
         //打印日志
         gclog_or_tty->print_cr("ChunkManager::free_chunks_get: free_list "
                                PTR_FORMAT " head " PTR_FORMAT " size " SIZE_FORMAT,
                                free_list, chunk, chunk->word_size());
       }
     } else {
       //如果是特殊规格，则在humongous链表中查找大于等于word_size的Metachunk
       chunk = humongous_dictionary()->get_chunk(
         word_size,
         FreeBlockDictionary<Metachunk>::atLeast);
    
       if (chunk == NULL) {
         return NULL;
       }
    
       if (TraceMetadataHumongousAllocation) {
         //查找成功，打印日志
         size_t waste = chunk->word_size() - word_size;
         gclog_or_tty->print_cr("Free list allocate humongous chunk size "
                                SIZE_FORMAT " for requested size " SIZE_FORMAT
                                " waste " SIZE_FORMAT,
                                chunk->word_size(), word_size, waste);
       }
     }
    
     //修改计数器
     dec_free_chunks_total(chunk->word_size());
     //删除对前后节点的引用
     chunk->set_next(NULL);
     chunk->set_prev(NULL);
     //增加Metachunk所属的VirtualSpaceNode的计数器
     chunk->container()->inc_container_count();
    
     slow_locked_verify();
     return chunk;
    }
    
    ChunkList* ChunkManager::find_free_chunks_list(size_t word_size) {
     ChunkIndex index = list_index(word_size);
     assert(index < HumongousIndex, "No humongous list");
     return free_chunks(index);
    }
    
    ChunkList* ChunkManager::free_chunks(ChunkIndex index) {
     assert(index == SpecializedIndex || index == SmallIndex || index == MediumIndex,
            err_msg("Bad index: %d", (int)index));
    
     return &_free_chunks[index];
    }
    
     void dec_free_chunks_total(size_t v) {
       assert(_free_chunks_count > 0 &&
                _free_chunks_total > 0,
                "About to go negative");
       //总个数减1         
       Atomic::add_ptr(-1, &_free_chunks_count);
       jlong minus_v = (jlong) - (jlong) v;
       //总内存空间减少v
       Atomic::add_ptr(minus_v, &_free_chunks_total);
     }
    
    3、remove_chunk / return_chunks
    remove_chunk是将某个Metachunk从ChunkManager中移除，return_chunks是将某个Metachunk添加到ChunkManager中，这两者的调用链如下：
    
    ![image.png](https://upload-images.jianshu.io/upload_images/26273155-9d24ef72095b81ce.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
    
    
    
    
    两者实现的源码如下：
    
    void ChunkManager::remove_chunk(Metachunk* chunk) {
     size_t word_size = chunk->word_size();
     //根据大小匹配对应的空闲chunk链表，然后从链表中移除
     ChunkIndex index = list_index(word_size);
     if (index != HumongousIndex) {
       free_chunks(index)->remove_chunk(chunk);
     } else {
       humongous_dictionary()->remove_chunk(chunk);
     }
    
     //减少计数器
     dec_free_chunks_total(chunk->word_size());
    }
    
    //return_chunks方法添加的Metachunk都是通用规格的
    void ChunkManager::return_chunks(ChunkIndex index, Metachunk* chunks) {
     if (chunks == NULL) {
       return;
     }
     //找到匹配的链表
     ChunkList* list = free_chunks(index);
     assert(list->size() == chunks->word_size(), "Mismatch in chunk sizes");
     assert_lock_strong(SpaceManager::expand_lock());
     Metachunk* cur = chunks;
    
     while (cur != NULL) {
       assert(cur->container() != NULL, "Container should have been set");
       //增加Metachunk所属的VirtualSpaceNode的计数器
       cur->container()->dec_container_count();
       //获取下一个节点
       Metachunk* next = cur->next();
       DEBUG_ONLY(cur->set_is_tagged_free(true);)
       //将cur设置为链表头
       list->return_chunk_at_head(cur);
       cur = next;
     }
    }
    

三、SpaceManager  
SpaceManager的定义位于metaspace.cpp中，用于给Metaspace提供内存管理接口，其包含的属性如下：

  * Mutex* const _lock; //内存分配的锁
  * Metaspace::MetadataType _mdtype; //Metaspace的类型
  * Metachunk* _chunks_in_use[NumberOfInUseLists] // SpaceManager使用的Metachunk的数组，总共有4个元素，即3种标准规格，加上一个特殊规格的chunk，每个chunk通过next属性构成一个链表，链表中的chunk如果不是当前chunk都会被retire，即把剩余空间分配成MetaBlock放入BlockFreelist中。
  * Metachunk* _current_chunk; //SpaceManager当前使用的Metachunk
  * static uint const _small_chunk_limit; //SpaceManager所能分配的small chunks的数量上限，ClassType类型的Metaspace没有此限制
  * size_t _allocated_blocks_words; //已分配的所有block的内存大小
  * size_t _allocated_chunks_words; //已分配的chunk的内存大小
  * size_t _allocated_chunks_count; //已分配的chunk的个数
  * BlockFreelist _block_freelists; //负责管理空闲block的BlockFreelist
  * static const char* _expand_lock_name; //_expand_lock的name属性
  * static const int _expand_lock_rank; //_expand_lock的rank属性
  * static Mutex* const _expand_lock;

_expand_lock和_small_chunk_limit是静态初始化的，如下图：

image.png

重点关注以下方法的实现。

1、构造和析构函数

    
    
    SpaceManager::SpaceManager(Metaspace::MetadataType mdtype,
                               Mutex* lock) :
      _mdtype(mdtype),
      _allocated_blocks_words(0),
      _allocated_chunks_words(0),
      _allocated_chunks_count(0),
      _lock(lock)
    {
      initialize();
    }
     
    void SpaceManager::initialize() {
      Metadebug::init_allocation_fail_alot_count();
      //初始化数组元素
      for (ChunkIndex i = ZeroIndex; i < NumberOfInUseLists; i = next_chunk_index(i)) {
        _chunks_in_use[i] = NULL;
      }
      _current_chunk = NULL;
      if (TraceMetadataChunkAllocation && Verbose) {
        //打印日志
        gclog_or_tty->print_cr("SpaceManager(): " PTR_FORMAT, this);
      }
    }
     
    SpaceManager::~SpaceManager() {
      //校验计数器_allocated_chunks_words的正确
      assert(sum_capacity_in_chunks_in_use() == allocated_chunks_words(),
        err_msg("sum_capacity_in_chunks_in_use() " SIZE_FORMAT
                " allocated_chunks_words() " SIZE_FORMAT,
                sum_capacity_in_chunks_in_use(), allocated_chunks_words()));
      //获取锁
      MutexLockerEx fcl(SpaceManager::expand_lock(),
                        Mutex::_no_safepoint_check_flag);
      //校验ChunkManager的计数器的正确
      chunk_manager()->slow_locked_verify();
      //将MetaspaceAux中的计数器减少
      dec_total_from_size_metrics();
     
      if (TraceMetadataChunkAllocation && Verbose) {
        //打印日志
        gclog_or_tty->print_cr("~SpaceManager(): " PTR_FORMAT, this);
        locked_print_chunks_in_use_on(gclog_or_tty);
      }
     
      // 增加空闲的chunk的数量和空闲chunk的内存大小
      chunk_manager()->inc_free_chunks_total(allocated_chunks_words(),
                                             sum_count_in_chunks_in_use());
     
      for (ChunkIndex i = ZeroIndex; i < HumongousIndex; i = next_chunk_index(i)) {
        if (TraceMetadataChunkAllocation && Verbose) {
          gclog_or_tty->print_cr("returned %d %s chunks to freelist",
                                 sum_count_in_chunks_in_use(i),
                                 chunk_size_name(i));
        }
        //遍历_chunks_in_use中的Chunk，将其归还到ChunkManager
        Metachunk* chunks = chunks_in_use(i);
        chunk_manager()->return_chunks(i, chunks);
        set_chunks_in_use(i, NULL);
        if (TraceMetadataChunkAllocation && Verbose) {
          gclog_or_tty->print_cr("updated freelist count %d %s",
                                 chunk_manager()->free_chunks(i)->count(),
                                 chunk_size_name(i));
        }
        assert(i != HumongousIndex, "Humongous chunks are handled explicitly later");
      }
     
     
      // Humongous chunks
      if (TraceMetadataChunkAllocation && Verbose) {
        gclog_or_tty->print_cr("returned %d %s humongous chunks to dictionary",
                                sum_count_in_chunks_in_use(HumongousIndex),
                                chunk_size_name(HumongousIndex));
        gclog_or_tty->print("Humongous chunk dictionary: ");
      }
      //获取Humongous chunk，因为大小不规整，不能通过return_chunks方法添加到ChunkManager中
      Metachunk* humongous_chunks = chunks_in_use(HumongousIndex);
     
      while (humongous_chunks != NULL) {
     
        if (TraceMetadataChunkAllocation && Verbose) {
          gclog_or_tty->print(PTR_FORMAT " (" SIZE_FORMAT ") ",
                              humongous_chunks,
                              humongous_chunks->word_size());
        }
        //校验Humongous chunk的内存大小是经过内存取整的
        assert(humongous_chunks->word_size() == (size_t)
               align_size_up(humongous_chunks->word_size(),
                                 smallest_chunk_size()),
               err_msg("Humongous chunk size is wrong: word size " SIZE_FORMAT
                       " granularity %d",
                       humongous_chunks->word_size(), smallest_chunk_size()));
        //获取下一个chunk
        Metachunk* next_humongous_chunks = humongous_chunks->next();
        //减少VirtualSpaceNode中的计数器
        humongous_chunks->container()->dec_container_count();
        //归还到_humongous_dictionary中
        chunk_manager()->humongous_dictionary()->return_chunk(humongous_chunks);
        humongous_chunks = next_humongous_chunks;
      }
      if (TraceMetadataChunkAllocation && Verbose) {
        gclog_or_tty->cr();
        gclog_or_tty->print_cr("updated dictionary count %d %s",
                         chunk_manager()->humongous_dictionary()->total_count(),
                         chunk_size_name(HumongousIndex));
      }
      chunk_manager()->slow_locked_verify();
    }
     
    size_t SpaceManager::sum_capacity_in_chunks_in_use() const {
      if (UseConcMarkSweepGC) {
         //CMS不需要使用Metaspace lock，所以不用遍历校验
        return allocated_chunks_words();
      } else {
        MutexLockerEx cl(lock(), Mutex::_no_safepoint_check_flag);
        size_t sum = 0;
        for (ChunkIndex i = ZeroIndex; i < NumberOfInUseLists; i = next_chunk_index(i)) {
          Metachunk* chunk = chunks_in_use(i);
          //遍历所有的Metachunk
          while (chunk != NULL) {
            sum += chunk->word_size();
            chunk = chunk->next();
          }
        }
      return sum;
      }
    }
     
    Metachunk* chunks_in_use(ChunkIndex index) const { return _chunks_in_use[index]; }
     
    size_t allocated_chunks_words() const { return _allocated_chunks_words; }
     
    ChunkManager* chunk_manager() const { return Metaspace::get_chunk_manager(_mdtype); }
     
    void SpaceManager::dec_total_from_size_metrics() {
      //将MetaspaceAux的计数减少
      MetaspaceAux::dec_capacity(mdtype(), allocated_chunks_words());
      //扣减所有block的内存空间
      MetaspaceAux::dec_used(mdtype(), allocated_blocks_words());
      //扣减Metachunk自身占用的内存空间
      MetaspaceAux::dec_used(mdtype(), allocated_chunks_count() * Metachunk::overhead());
    }
     
    size_t allocated_chunks_words() const { return _allocated_chunks_words; }
     
    size_t allocated_blocks_words() const { return _allocated_blocks_words; }
     
    size_t allocated_chunks_count() const { return _allocated_chunks_count; }
    

2、allocate / deallocate  
allocate方法用来分配一个指定大小的内存块，优先从BlockFreelist中分配，分配失败从当前chunk中分配，还是失败则创建一个新的chunk，从新chunk中分配；deallocate用于释放这个内存块，将内存块作为MetaBlock归还到BlockFreelist中，两者的调用链如下：

image.png

image.png

两者的实现如下：

    
    
    MetaWord* SpaceManager::allocate(size_t word_size) {
      MutexLockerEx cl(lock(), Mutex::_no_safepoint_check_flag);
      //获取取整后的字宽数
      size_t raw_word_size = get_raw_word_size(word_size);
      BlockFreelist* fl =  block_freelists();
      MetaWord* p = NULL;
      //从BlockFreelist中分配需要遍历，成本比较贵，所以只有当BlockFreelist对应的内存比较大的时候才尝试从BlockFreelist中分配
      //allocation_from_dictionary_limit是一个固定值，固定值4K
      if (fl->total_size() > allocation_from_dictionary_limit) {
        p = fl->get_block(raw_word_size);
      }
      if (p == NULL) {
        //从当前chunk中分配，如果内存不足则创建一个新的chunk，从新chunk中分配
        p = allocate_work(raw_word_size);
      }
     
      return p;
    }
     
    void SpaceManager::deallocate(MetaWord* p, size_t word_size) {
      assert_lock_strong(_lock);
      //获取取整后的字宽数
      size_t raw_word_size = get_raw_word_size(word_size);
      size_t min_size = TreeChunk<Metablock, FreeList<Metablock> >::min_size();
      assert(raw_word_size >= min_size,
             err_msg("Should not deallocate dark matter " SIZE_FORMAT "<" SIZE_FORMAT, word_size, min_size));
      //将其作为MetaBlock放到BlockFreelist中       
      block_freelists()->return_block(p, raw_word_size);
    }
     
    Mutex* lock() const { return _lock; }
     
     size_t get_raw_word_size(size_t word_size) {
        size_t byte_size = word_size * BytesPerWord;
        //byte_size最低大于Metablock的大小
        size_t raw_bytes_size = MAX2(byte_size, sizeof(Metablock));
        //向上内存取整
        raw_bytes_size = align_size_up(raw_bytes_size, Metachunk::object_alignment());
     
        size_t raw_word_size = raw_bytes_size / BytesPerWord;
        assert(raw_word_size * BytesPerWord == raw_bytes_size, "Size problem");
     
        return raw_word_size;
      }
     
    BlockFreelist* block_freelists() const {
        return (BlockFreelist*) &_block_freelists;
      }
     
    MetaWord* SpaceManager::allocate_work(size_t word_size) {
      assert_lock_strong(_lock);
     
      // Is there space in the current chunk?
      MetaWord* result = NULL;
       
      //DumpSharedSpaces表示Dump出共享的space到一个文件中，默认为false
      //如果DumpSharedSpaces为true则只尝试从当前的chunk中分配，如果分配失败，返回NULL由调用方负责处理
      if (DumpSharedSpaces) {
        assert(current_chunk() != NULL, "should never happen");
        inc_used_metrics(word_size);
        return current_chunk()->allocate(word_size); // caller handles null result
      }
     
      if (current_chunk() != NULL) {
        //从当前的chunk中分配
        result = current_chunk()->allocate(word_size);
      }
     
      if (result == NULL) {
        //当前chunk可用空间不足导致分配失败，则扩展一个新的chunk，从新的chunk中分配
        result = grow_and_allocate(word_size);
      }
     
      if (result != NULL) {
        //如果分配成功，增加计数
        inc_used_metrics(word_size);
        assert(result != (MetaWord*) chunks_in_use(MediumIndex),
               "Head of the list is being allocated");
      }
     
      return result;
    }
     
    void SpaceManager::inc_used_metrics(size_t words) {
      // Add to the per SpaceManager total
      Atomic::add_ptr(words, &_allocated_blocks_words);
      // Add to the global total
      MetaspaceAux::inc_used(mdtype(), words);
    }
     
    MetaWord* SpaceManager::grow_and_allocate(size_t word_size) {
      //校验参数
      assert(vs_list()->current_virtual_space() != NULL,
             "Should have been set");
      assert(current_chunk() == NULL ||
             current_chunk()->allocate(word_size) == NULL,
             "Don't need to expand");
      //获取锁expand_lock
      MutexLockerEx cl(SpaceManager::expand_lock(), Mutex::_no_safepoint_check_flag);
     
      if (TraceMetadataChunkAllocation && Verbose) {
        size_t words_left = 0;
        size_t words_used = 0;
        if (current_chunk() != NULL) {
          words_left = current_chunk()->free_word_size();
          words_used = current_chunk()->used_word_size();
        }
        //打印日志
        gclog_or_tty->print_cr("SpaceManager::grow_and_allocate for " SIZE_FORMAT
                               " words " SIZE_FORMAT " words used " SIZE_FORMAT
                               " words left",
                                word_size, words_used, words_left);
      }
     
      //计算新chunk的大小
      size_t chunk_word_size = calc_chunk_size(word_size);
      //首先从ChunkManager的空闲列表中查找，查找失败则VirtualSpaceList创建一个新的chunk
      Metachunk* next = get_new_chunk(chunk_word_size);
     
      MetaWord* mem = NULL;
     
      if (next != NULL) {
        //将新chunk添加到_chunks_in_use数组中
        add_chunk(next, false);
        //使用新chunk分配内存
        mem = next->allocate(word_size);
      }
     
      // Track metaspace memory usage statistic.
      track_metaspace_memory_usage();
     
      return mem;
    }
     
    size_t SpaceManager::calc_chunk_size(size_t word_size) {
     
      //判断采用MediumChunk还是SmallChunk
      size_t chunk_word_size;
      if (chunks_in_use(MediumIndex) == NULL &&
          sum_count_in_chunks_in_use(SmallIndex) < _small_chunk_limit) {
        chunk_word_size = (size_t) small_chunk_size();
        if (word_size + Metachunk::overhead() > small_chunk_size()) {
          chunk_word_size = medium_chunk_size();
        }
      } else {
        chunk_word_size = medium_chunk_size();
      }
     
      //按照SpecializedChunk的内存取整
      size_t if_humongous_sized_chunk =
        align_size_up(word_size + Metachunk::overhead(),
                      smallest_chunk_size());
      chunk_word_size =
        MAX2((size_t) chunk_word_size, if_humongous_sized_chunk);
      
      //is_humongous为false时，chunk_word_size就是SmallChunk
      //is_humongous为true时，chunk_word_size就是MediumChunk,word_size大于MediumChunk，算出来的if_humongous_sized_chunk肯定大于chunk_word_size
      //取最大值时，chunk_word_size变成if_humongous_sized_chunk
      assert(!SpaceManager::is_humongous(word_size) ||
             chunk_word_size == if_humongous_sized_chunk,
             err_msg("Size calculation is wrong, word_size " SIZE_FORMAT
                     " chunk_word_size " SIZE_FORMAT,
                     word_size, chunk_word_size));
      if (TraceMetadataHumongousAllocation &&
          SpaceManager::is_humongous(word_size)) {
        gclog_or_tty->print_cr("Metadata humongous allocation:");
        gclog_or_tty->print_cr("  word_size " PTR_FORMAT, word_size);
        gclog_or_tty->print_cr("  chunk_word_size " PTR_FORMAT,
                               chunk_word_size);
        gclog_or_tty->print_cr("    chunk overhead " PTR_FORMAT,
                               Metachunk::overhead());
      }
      return chunk_word_size;
    }
     
    size_t small_chunk_size()       const { return small_chunk_size(is_class()); }
     
    size_t medium_chunk_size()      const { return medium_chunk_size(is_class()); }
     
    static size_t small_chunk_size(bool is_class)       { return is_class ? ClassSmallChunk : SmallChunk; }
     
    static size_t medium_chunk_size(bool is_class)      { return is_class ? ClassMediumChunk : MediumChunk; }
     
    size_t smallest_chunk_size()    const { return smallest_chunk_size(is_class()); }
     
    static size_t smallest_chunk_size(bool is_class)    { return specialized_chunk_size(is_class); }
     
    static size_t specialized_chunk_size(bool is_class) { return is_class ? ClassSpecializedChunk : SpecializedChunk; }
     
    bool is_humongous(size_t word_size) { return word_size > medium_chunk_size(); }
     
    Metachunk* SpaceManager::get_new_chunk(size_t chunk_word_size) {
      //首先从空闲的chunk列表中查找
      Metachunk* next = chunk_manager()->chunk_freelist_allocate(chunk_word_size);
     
      if (next == NULL) {
        //查找失败，从VirtualSpaceList中分配一个新的chunk
        next = vs_list()->get_new_chunk(chunk_word_size,
                                        medium_chunk_bunch());
      }
     
      if (TraceMetadataHumongousAllocation && next != NULL &&
          SpaceManager::is_humongous(next->word_size())) {
          //打印日志
        gclog_or_tty->print_cr("  new humongous chunk word size "
                               PTR_FORMAT, next->word_size());
      }
     
      return next;
    }
     
    VirtualSpaceList* vs_list()   const { return Metaspace::get_space_list(_mdtype); }
     
    void SpaceManager::add_chunk(Metachunk* new_chunk, bool make_current) {
     
      assert(new_chunk != NULL, "Should not be NULL");
      assert(new_chunk->next() == NULL, "Should not be on a list");
      //将其重置成初始状态
      new_chunk->reset_empty();
     
      //根据chunk的大小找到匹配的链表
      ChunkIndex index = chunk_manager()->list_index(new_chunk->word_size());
      //如果是规整的chunk
      if (index != HumongousIndex) {
         //将当前chunk的剩余空间分配成block，放入BlockFreelist中，避免空间浪费
        retire_current_chunk();
        //将新的chunk设置为当前chunk，原来的chunk作为当前chunk的next节点
        set_current_chunk(new_chunk);
        new_chunk->set_next(chunks_in_use(index));
        set_chunks_in_use(index, new_chunk);
      } else {
        
        if (make_current) {
          //将新chunk设置为当前chunk，SpaceManager::grow_and_allocate中调用时永远传false，Metaspace::initialize_first_chunk中调用时传true
          //只有启动类加载器对应的metaspace才会将_current_chunk设置为一个humongous chunk
          set_current_chunk(new_chunk);
        }
       
        new_chunk->set_next(chunks_in_use(HumongousIndex));
        set_chunks_in_use(HumongousIndex, new_chunk);
     
        assert(new_chunk->word_size() > medium_chunk_size(), "List inconsistency");
      }
     
      //增加计数
      inc_size_metrics(new_chunk->word_size());
     
      assert(new_chunk->is_empty(), "Not ready for reuse");
      if (TraceMetadataChunkAllocation && Verbose) {
        gclog_or_tty->print("SpaceManager::add_chunk: %d) ",
                            sum_count_in_chunks_in_use());
        new_chunk->print_on(gclog_or_tty);
        //打印日志
        chunk_manager()->locked_print_free_chunks(gclog_or_tty);
      }
    }
     
    void SpaceManager::retire_current_chunk() {
      if (current_chunk() != NULL) {
        //获取剩余的内存
        size_t remaining_words = current_chunk()->free_word_size();
        if (remaining_words >= TreeChunk<Metablock, FreeList<Metablock> >::min_size()) {
          //如果大于最小值，则将其变成block放到BlockFreelist中，避免空间浪费
          block_freelists()->return_block(current_chunk()->allocate(remaining_words), remaining_words);
          inc_used_metrics(remaining_words);
        }
      }
    }
     
    void SpaceManager::inc_size_metrics(size_t words) {
      assert_lock_strong(SpaceManager::expand_lock());
      // Total of allocated Metachunks and allocated Metachunks count
      // for each SpaceManager
      _allocated_chunks_words = _allocated_chunks_words + words;
      _allocated_chunks_count++;
      // Global total of capacity in allocated Metachunks
      MetaspaceAux::inc_capacity(mdtype(), words);
      MetaspaceAux::inc_used(mdtype(), Metachunk::overhead());
    }
    

3、get_initial_chunk_size  
get_initial_chunk_size用于获取初始chunk的大小，其调用链如下：

image.png

源码如下：

    
    
    size_t SpaceManager::get_initial_chunk_size(Metaspace::MetaspaceType type) const {
      size_t requested;
     
      if (is_class()) {
        switch (type) {
        case Metaspace::BootMetaspaceType:       requested = Metaspace::first_class_chunk_word_size(); break;
        case Metaspace::ROMetaspaceType:         requested = ClassSpecializedChunk; break;
        case Metaspace::ReadWriteMetaspaceType:  requested = ClassSpecializedChunk; break;
        case Metaspace::AnonymousMetaspaceType:  requested = ClassSpecializedChunk; break;
        case Metaspace::ReflectionMetaspaceType: requested = ClassSpecializedChunk; break;
        default:                                 requested = ClassSmallChunk; break;
        }
      } else {
        switch (type) {
        case Metaspace::BootMetaspaceType:       requested = Metaspace::first_chunk_word_size(); break;
        case Metaspace::ROMetaspaceType:         requested = SharedReadOnlySize / wordSize; break;
        case Metaspace::ReadWriteMetaspaceType:  requested = SharedReadWriteSize / wordSize; break;
        case Metaspace::AnonymousMetaspaceType:  requested = SpecializedChunk; break;
        case Metaspace::ReflectionMetaspaceType: requested = SpecializedChunk; break;
        default:                                 requested = SmallChunk; break;
        }
      }
     
      //将requested 适配到标准的chunk size
      const size_t adjusted = adjust_initial_chunk_size(requested);
     
      assert(adjusted != 0, err_msg("Incorrect initial chunk size. Requested: "
             SIZE_FORMAT " adjusted: " SIZE_FORMAT, requested, adjusted));
     
      return adjusted;
    }
     
    size_t SpaceManager::adjust_initial_chunk_size(size_t requested) const {
      return adjust_initial_chunk_size(requested, is_class());
    }
     
    size_t SpaceManager::adjust_initial_chunk_size(size_t requested, bool is_class_space) {
      size_t chunk_sizes[] = {
          specialized_chunk_size(is_class_space),
          small_chunk_size(is_class_space),
          medium_chunk_size(is_class_space)
      };
     
      //从小到大依次遍历
      for (size_t i = 0; i < ARRAY_SIZE(chunk_sizes); i++) {
        if (requested <= chunk_sizes[i]) {
          return chunk_sizes[i];
        }
      }
     
      return requested;
    }
    

枚举MetaspaceType表示元空间的类型，其定义如下：

image.png

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [深入理解Memcache原理](https://www.jianshu.com/p/1fb379ebaa9a)

1.为什么要使用memcache 由于网站的高并发读写需求，传统的关系型数据库开始出现瓶颈，例如： 1）对数据库的...

[苏文星](https://www.jianshu.com/u/944b2c8e47a0)阅读 1,685评论 0赞 5

  * [【Hybrid开发高级系列】WebPack模块化专题](https://www.jianshu.com/p/c915685b5c88)

1 Webpack 1.1 概念简介 1.1.1 WebPack是什么 1、一个打包工具 2、一个模块加载工具 3...

[Kevin_Junbaozi](https://www.jianshu.com/u/dfae73bde753)阅读 6,294评论 0赞 16

  * [android 音频总结](https://www.jianshu.com/p/5389a9abe2b9)

Android音频系统详解 参考好文: Android 音频系统：从 AudioTrack 到 AudioFlin...

[爱雨520](https://www.jianshu.com/u/73e1ae3fa1f6)阅读 12,040评论 2赞 5

  * [借助gdb调试glibc代码学习House of Orange](https://www.jianshu.com/p/57a5c9a492aa)

1．准备工作 学习了CTF比赛中的一种堆利用方法—house of orange，看了很多师傅们的博客和一些国外网...

[静析机言](https://www.jianshu.com/u/fd954951a7f2)阅读 355评论 0赞 0

  * [无标题文章](https://www.jianshu.com/p/c4ef040ff984)

转至元数据结尾创建： 董潇伟，最新修改于： 十二月 23, 2016 转至元数据起始第一章:isa和Class一....

[40c0490e5268](https://www.jianshu.com/u/40c0490e5268)阅读 1,488评论 0赞 9

 