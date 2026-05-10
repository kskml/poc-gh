# Apache Kafka — Complete Interview Questions & Answers (2025–2026 Edition)

> **Level:** Senior/Architect (10+ Years Java/Spring Boot)  
> **Coverage:** Latest company questions, Scenario-based, Tricky, Real-time production issues, KRaft mode, Kafka 3.x+ features  
> **Total Questions:** 200+

---

## Table of Contents

- [Section 1: Kafka Fundamentals & Architecture](#section-1-kafka-fundamentals--architecture)
- [Section 2: Topic, Partition & Segments — Deep Dive](#section-2-topic-partition--segments--deep-dive)
- [Section 3: Producer Internals & Advanced Patterns](#section-3-producer-internals--advanced-patterns)
- [Section 4: Consumer Internals & Advanced Patterns](#section-4-consumer-internals--advanced-patterns)
- [Section 5: Consumer Group & Rebalance](#section-5-consumer-group--rebalance)
- [Section 6: Offset Management & Delivery Semantics](#section-6-offset-management--delivery-semantics)
- [Section 7: Kafka Storage & Log Internals](#section-7-kafka-storage--log-internals)
- [Section 8: Replication & ISR](#section-8-replication--isr)
- [Section 9: Kafka Controller & KRaft Mode](#section-9-kafka-controller--kraft-mode)
- [Section 10: Kafka Security](#section-10-kafka-security)
- [Section 11: Kafka Monitoring & Operations](#section-11-kafka-monitoring--operations)
- [Section 12: Kafka Performance Tuning](#section-12-kafka-performance-tuning)
- [Section 13: Kafka Connect](#section-13-kafka-connect)
- [Section 14: Kafka Streams](#section-14-kafka-streams)
- [Section 15: Schema Registry & Avro/Protobuf](#section-15-schema-registry--avroprotobuf)
- [Section 16: Spring Boot + Kafka Integration](#section-16-spring-boot--kafka-integration)
- [Section 17: Kafka in Microservices Architecture](#section-17-kafka-in-microservices-architecture)
- [Section 18: Exactly-Once Semantics & Transactions](#section-18-exactly-once-semantics--transactions)
- [Section 19: Disaster Recovery & Multi-Datacenter](#section-19-disaster-recovery--multi-datacenter)
- [Section 20: Real-Time Production Scenario Questions](#section-20-real-time-production-scenario-questions)
- [Section 21: Tricky & Gotcha Questions](#section-21-tricky--gotcha-questions)
- [Section 22: Kafka vs Alternatives — Comparison Questions](#section-22-kafka-vs-alternatives--comparison-questions)
- [Section 23: Design & Architecture Questions](#section-23-design--architecture-questions)
- [Section 24: Kafka 3.x/4.x Features & KRaft Migration](#section-24-kafka-3x4x-features--kraft-migration)

---

## Section 1: Kafka Fundamentals & Architecture

### Q1: What is Apache Kafka and why is it called a distributed event streaming platform?

**Answer:**
Apache Kafka is a distributed event streaming platform used for high-performance data pipelines, streaming analytics, data integration, and mission-critical applications. It is called a "distributed event streaming platform" because it combines three capabilities:

1. **Publish/Subscribe Message Queue** — It works as a traditional message broker where producers publish events and consumers subscribe to them.
2. **Durable Storage** — Kafka durably persists events on disk with configurable retention, allowing consumers to replay events. This is fundamentally different from traditional JMS brokers that delete messages after consumption.
3. **Stream Processing** — With Kafka Streams library, you can process events in real-time as they arrive.

Kafka is designed as a distributed system from the ground up — it runs as a cluster of brokers, partitions data across nodes, replicates for fault tolerance, and scales horizontally. The "event streaming" paradigm treats data as a continuous flow of events (facts that happened) rather than static records in a database.

**Key distinction from traditional messaging:** In JMS/RabbitMQ, messages are consumed and removed. In Kafka, events are appended to an immutable log and remain until retention expires. Multiple consumers can independently read the same event at their own pace.

---

### Q2: Explain the core components of Kafka architecture with their roles.

**Answer:**

```
┌─────────────────────────────────────────────────────────────────┐
│                      Kafka Cluster                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │ Broker 0 │  │ Broker 1 │  │ Broker 2 │                      │
│  │(Controller│  │          │  │          │                      │
│  │ Leader)  │  │          │  │          │                      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                      │
│       │              │              │                            │
│  ┌────▼──────────────▼──────────────▼─────┐                    │
│  │        ZooKeeper / KRaft               │                    │
│  │    (Metadata & Coordination)           │                    │
│  └────────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Producer    │    │   Topic      │    │  Consumer    │
│  (writes)    │───▶│  (log)       │───▶│  (reads)     │
└──────────────┘    └──────────────┘    └──────────────┘
```

| Component | Role |
|-----------|------|
| **Broker** | A Kafka server node that stores data and serves client requests. Each broker has a unique broker.id. |
| **Topic** | A logical category/feed name to which events are published. Topics are partitioned and replicated. |
| **Partition** | An ordered, immutable sequence of records. The unit of parallelism in Kafka. |
| **Producer** | Client that publishes events to topics. Chooses which partition to write to. |
| **Consumer** | Client that reads events from topics. Tracks its position using offsets. |
| **Consumer Group** | A group of consumers that collectively consume a topic; each partition is assigned to exactly one consumer in the group. |
| **ZooKeeper/KRaft** | Manages broker metadata, controller election, and ACL configuration. KRaft replaces ZooKeeper in Kafka 3.x+. |
| **Controller** | A special broker responsible for partition leadership election, broker failure detection, and administrative operations. |

---

### Q3: How does Kafka differ from traditional message brokers like RabbitMQ, ActiveMQ, or IBM MQ?

**Answer:**

This is a frequently asked architecture-level question. The fundamental difference lies in the **pull-based, log-centric** design of Kafka vs. the **push-based, queue-centric** design of traditional brokers.

| Aspect | Kafka | Traditional MQ (RabbitMQ/ActiveMQ) |
|--------|-------|-----------------------------------|
| **Message Model** | Publish-Subscribe with durable log | Both Point-to-Point and Pub-Sub |
| **Consumption** | Pull-based (consumer asks for data) | Push-based (broker pushes to consumer) |
| **Message Retention** | Retained based on time/size policy | Deleted after acknowledgment |
| **Replay** | Consumers can replay from any offset | No replay once acknowledged |
| **Ordering** | Per-partition ordering guaranteed | Per-queue ordering only |
| **Throughput** | Millions of msgs/sec | Tens of thousands of msgs/sec |
| **Backpressure** | Consumer controls pace (pull model) | Broker must handle slow consumers |
| **Scaling** | Horizontal (add partitions/brokers) | Often vertical or limited horizontal |
| **Message Priority** | No native priority support | Supports message priority queues |
| **Routing** | Topic-based (simple) | Complex routing (exchange types, JMS selectors) |
| **Protocol** | Custom binary protocol over TCP | AMQP, STOMP, MQTT, OpenWire |

**When to choose Kafka:** High-throughput event streaming, log aggregation, real-time analytics, event sourcing, microservices choreography, situations where replay is needed.

**When to choose traditional MQ:** Request-reply patterns, complex routing, message priority, individual message acknowledgment, JMS compliance requirements, workflow orchestration.

---

### Q4: What is an event in Kafka? How is it different from a message?

**Answer:**
In Kafka terminology, an **event** (also called a record or message) is a combination of:

1. **Key** (optional) — Used for partitioning strategy and log compaction
2. **Value** (required) — The actual payload (can be JSON, Avro, Protobuf, bytes)
3. **Timestamp** — Either set by producer (CreateTime) or broker (LogAppendTime)
4. **Headers** (optional, since Kafka 0.11) — Key-value metadata pairs

An **event** semantically represents something that happened (e.g., "OrderPlaced", "PaymentProcessed"). A **message** is a more generic term used in traditional messaging. The event-driven mindset is important: events are immutable facts. You don't "update" an event — you publish a new one (e.g., "OrderCancelled").

The RecordBatch format (introduced in Kafka 0.11) groups multiple records for efficient compression and batching, which is a key performance optimization.

---

### Q5: What is the role of ZooKeeper in Kafka and why is it being removed (KRaft)?

**Answer:**

ZooKeeper has been the metadata store for Kafka since its inception. It manages:

1. **Broker Registration** — Brokers register themselves as ephemeral nodes in ZooKeeper
2. **Controller Election** — Only one broker can be the controller; ZooKeeper ensures this via leader election
3. **Topic/Partition Metadata** — Which partitions exist, who are leaders, ISR lists
4. **ACLs** — Security access control lists
5. **Consumer Offset (legacy)** — In older Kafka versions, offsets were stored in ZooKeeper (now in `__consumer_offsets` topic)

**Why remove ZooKeeper (KRaft migration)?**

- **Operational Complexity** — Running and maintaining a separate ZooKeeper ensemble is operationally expensive
- **Scalability Bottleneck** — Metadata requests go through ZooKeeper, limiting the number of partitions a cluster can support (~200K partitions max with ZooKeeper)
- **Inconsistency Risk** — Two metadata stores (ZooKeeper + broker cache) can get out of sync
- **Slow Controller Failover** — Controller election through ZooKeeper can take 30+ seconds

**KRaft (Kafka Raft)** mode, available since Kafka 2.8 (preview) and production-ready in Kafka 3.3+, replaces ZooKeeper with an internal Raft-based consensus protocol. A quorum of KRaft controllers manages metadata internally. Benefits include:
- Millions of partitions supported
- Faster controller failover (sub-second)
- Simpler deployment (no ZooKeeper ensemble)
- Single source of truth for metadata

---

### Q6: Explain the Kafka protocol and how clients communicate with brokers.

**Answer:**
Kafka uses a custom binary TCP protocol, not HTTP or AMQP. Key aspects:

1. **Binary Protocol** — All requests and responses are binary-encoded for efficiency. There's no text-based overhead.
2. **Request/Response Model** — Clients send requests with a correlation_id and receive responses
3. **API Keys** — Each request type has an API key (e.g., Produce=0, Fetch=1, Metadata=3, OffsetCommit=8)
4. **Versioning** — Each API has versions; clients negotiate the highest supported version
5. **Connection Management** — Clients maintain persistent TCP connections to brokers (not per-request)
6. **Batching** — Produce and Fetch requests batch multiple records for efficiency

The network flow:
```
Producer → Broker: ProduceRequest (batched records)
Broker → Producer: ProduceResponse (offsets + errors)
Consumer → Broker: FetchRequest (topic, partition, offset)
Broker → Consumer: FetchResponse (batched records)
```

**Bootstrap Servers:** Clients only need to know one or more broker addresses initially. They then fetch full cluster metadata to discover all brokers and partition leaders. This is why `bootstrap.servers` can be a subset of all brokers.

---

### Q7: What is a broker in Kafka? Can a single broker be a Kafka cluster?

**Answer:**
A **broker** is a single Kafka server process. It:

- Stores topic partitions on disk
- Handles produce/fetch requests from clients
- Replicates data from other brokers (for replica partitions)
- Participates in controller election

**Yes, a single broker can technically be a Kafka cluster**, but it would have:
- No replication (replication.factor=1)
- No fault tolerance (if broker dies, all data unavailable)
- Limited throughput

A production Kafka cluster typically has 3+ brokers (minimum for a replication factor of 3 with leader election). Enterprise clusters often run 5–15+ brokers.

---

### Q8: How does Kafka achieve high throughput and low latency?

**Answer:**
Kafka achieves this through several design decisions:

1. **Sequential I/O (Append-Only Log)** — Kafka appends to disk sequentially, which is orders of magnitude faster than random writes (600MB/s sequential vs 100KB/s random on typical HDDs). This is the single biggest design insight.

2. **Zero-Copy Transfer** — When consumers fetch data, Kafka uses the OS `sendfile()` syscall to transfer data directly from disk to network socket, bypassing user-space copying. The data path is: Disk → OS Page Cache → Network Socket (no JVM heap involvement).

3. **Page Cache Utilization** — Kafka does NOT cache data in the JVM heap. Instead, it relies on the OS page cache. This avoids GC pauses and allows data to persist in memory even after broker restarts.

4. **Batching** — Producers batch records before sending; consumers fetch batches. This amortizes network round-trips.

5. **Compression** — Batches can be compressed (gzip, snappy, lz4, zstd) at the producer, and the entire batch is compressed/decompressed as a unit, saving network and storage.

6. **Partition Parallelism** — Topics are split into partitions, enabling parallel writes and reads across multiple brokers.

7. **Pull-Based Consumption** — Consumers pull data at their own rate, avoiding backpressure issues in push-based systems.

---

## Section 2: Topic, Partition & Segments — Deep Dive

### Q9: What is a topic in Kafka? How are topics different from queues?

**Answer:**
A **topic** is a logical channel or category to which records are published. It is:

- **Immutable log** — Records are appended and never modified in place
- **Multi-subscriber** — Multiple consumer groups can independently consume the same topic
- **Retained** — Records persist based on retention policy (time-based: `retention.ms`, size-based: `retention.bytes`, or compaction: `cleanup.policy=compact`)
- **Partitioned** — Split across multiple partitions for parallelism

**Topic vs Queue comparison:**

| Feature | Kafka Topic | JMS Queue |
|---------|-------------|-----------|
| Consumption | Multiple groups independently | One consumer gets the message |
| Retention | Time/size-based | Until consumed |
| Replay | Possible via offset reset | Not possible |
| Ordering | Per-partition | Per-queue |
| Semantics | Publish-subscribe log | Point-to-point |

---

### Q10: What is a partition? Why do we need partitions?

**Answer:**
A **partition** is an ordered, immutable sequence of records appended to a commit log. Each partition is:

- A single unit of parallelism
- Stored on one broker as the leader, with replicas on other brokers
- An independent log with its own offset sequence starting from 0
- The unit of assignment to consumers in a group

**Why partitions exist:**

1. **Scalability** — A single partition limits throughput to what one broker can handle. Partitions distribute load across brokers.
2. **Parallelism** — Multiple consumers in a group can read different partitions concurrently.
3. **Ordering Guarantee** — Within a partition, records are strictly ordered by offset. This is a key guarantee that enables stateful processing.

**Partition count formula:**
```
Target Throughput / Partition Throughput = Min Partitions
```
For example, if you need 100 MB/s and each partition handles 10 MB/s, you need at least 10 partitions.

**Trade-off:** More partitions = more parallelism but also more file handles, more memory for leader election, longer recovery time, and more overhead for the controller.

---

### Q11: How are partitions distributed across brokers?

**Answer:**
Kafka distributes partition replicas across brokers to ensure:

1. **Even replica distribution** — Each broker gets roughly the same number of replicas
2. **Leader distribution** — Each broker leads roughly the same number of partitions
3. **Rack awareness** — If `broker.rack` is configured, replicas are spread across racks

**Assignment algorithm (default):**

```
Step 1: Assign replica 0 (leader) using round-robin across brokers
Step 2: Assign subsequent replicas by shifting by a random increment
Step 3: If rack-aware, shift across racks first, then brokers within racks
```

For a topic with 6 partitions and replication factor 3 across 3 brokers:
```
Partition 0: Broker 0 (leader), Broker 1, Broker 2
Partition 1: Broker 1 (leader), Broker 2, Broker 0
Partition 2: Broker 2 (leader), Broker 0, Broker 1
Partition 3: Broker 0 (leader), Broker 2, Broker 1  (shifted)
Partition 4: Broker 1 (leader), Broker 0, Broker 2
Partition 5: Broker 2 (leader), Broker 1, Broker 0
```

You can also use a custom `PartitionAssignor` for specific placement requirements.

---

### Q12: What is a segment in Kafka? Explain the segment file structure.

**Answer:**
Each partition is divided into **segments** — individual files on disk. A segment consists of three files:

```
<partition-dir>/
  ├── 00000000000000000000.log      ← Actual messages (RecordBatch)
  ├── 00000000000000000000.index    ← Offset → byte position mapping
  ├── 00000000000000000000.timeindex← Timestamp → offset mapping
  ├── 00000000000005367851.log      ← Next segment (active)
  ├── 00000000000005367851.index
  └── 00000000000005367851.timeindex
```

**How segments work:**

1. **Active Segment** — The last segment is the active one; new records are always appended here.
2. **Rolling** — When the active segment reaches `segment.bytes` (default 1GB) or `segment.ms` (default 7 days), it's "rolled" and a new active segment is created.
3. **Naming** — Segments are named by the base offset (offset of the first message in the segment).
4. **Sparse Indexing** — The `.index` file maps every Nth offset to its byte position (controlled by `index.interval.bytes`, default 4096). This keeps the index small while allowing binary search + sequential scan.

**Offset lookup process:**
```
1. Binary search in .index file to find the closest offset ≤ target
2. Seek to that byte position in .log file
3. Scan sequentially from there until the desired offset is found
```

The `.timeindex` file maps timestamps to offsets, enabling time-based retrieval (e.g., "give me all messages after 10:00 AM").

---

### Q13: How does Kafka handle partition count changes? Can you reduce partitions?

**Answer:**

**Increasing partitions:** You can increase partitions at any time using:
```bash
kafka-topics.sh --alter --topic my-topic --partitions 10
```

Key considerations:
- New partitions are assigned to brokers automatically
- **Key ordering breaks** — If a producer uses key-based partitioning, increasing partitions changes the hash mapping. A key that previously went to partition 3 might now go to partition 7. This breaks the guarantee that all records with the same key are in the same partition.
- New consumers in the group will trigger a rebalance to pick up new partitions

**Decreasing partitions:** **Not possible** in Kafka. The reason is fundamental to Kafka's architecture:

1. Partitioning uses modulo arithmetic: `partition = hash(key) % num_partitions`
2. If you reduce from 8 to 4 partitions, records that were in partitions 4-7 have nowhere logical to go
3. Merging partitions would require rewriting the entire log, and the ordering of merged data is undefined
4. Deleting specific partitions would break consumer offset tracking

**Workaround for reducing partitions:** Create a new topic with fewer partitions and migrate data using MirrorMaker or a custom Kafka Streams job.

---

### Q14: What is log compaction? How does it work internally?

**Answer:**
Log compaction (`cleanup.policy=compact`) ensures that Kafka retains at least the **last known value** for each message key in a topic. Unlike delete-based retention (which removes old segments entirely), compaction removes older records with the same key while preserving the latest.

**Internal process:**

```
Before Compaction:              After Compaction:
Offset  Key    Value            Offset  Key    Value
0       K1     "Alice"          0       K1     "Alice" (kept as latest)
1       K2     "Bob"            1       K2     "Robert"(kept as latest)
2       K3     "Charlie"        2       K3     "Charlie"(kept as latest)
3       K1     "Alicia"         3       K1     "Alicia" (kept - latest for K1)
4       K2     "Robert"         ─       ─       (K2 old value removed)
5       K4     "Diana"          5       K4     "Diana"
```

**How compaction runs:**

1. Compaction runs in a background thread per partition
2. It works on **segments** — only completed (non-active) segments are compacted
3. Two-phase process:
   - **Phase 1:** Read the segment, build a map of key → latest offset
   - **Phase 2:** Write a new segment containing only the latest value for each key
4. The old segment files are swapped with the new ones (atomic replace)
5. Records with `null` key are always removed during compaction
6. A **tombstone** (record with null value) marks a key for deletion; it's retained for `delete.retention.ms` (default 24 hours) to give consumers time to see it

**Use cases:** Change Data Capture (CDC), maintaining latest state (user profiles, configuration), event sourcing snapshots, `__consumer_offsets` topic.

---

### Q15: What is the relationship between partitions and consumer group parallelism?

**Answer:**

The cardinal rule: **The number of consumers in a group that can actively consume from a topic is limited by the number of partitions.**

```
Scenario 1: 6 partitions, 3 consumers
  Consumer A → Partitions 0, 1
  Consumer B → Partitions 2, 3
  Consumer C → Partitions 4, 5

Scenario 2: 6 partitions, 6 consumers
  Consumer A → Partition 0
  Consumer B → Partition 1
  ...
  Consumer F → Partition 5

Scenario 3: 6 partitions, 10 consumers
  Consumer A → Partition 0
  ...
  Consumer F → Partition 5
  Consumer G → IDLE (no partition assigned)
  Consumer H → IDLE
  Consumer I → IDLE
  Consumer J → IDLE
```

**Implications:**
- If you need 20 consumers for parallel processing, you need at least 20 partitions
- Idle consumers are waste of resources — they serve as standby for failover
- Over-partitioning (e.g., 100 partitions for 3 consumers) adds overhead without benefit
- When a consumer fails, its partitions are redistributed to surviving consumers

---

## Section 3: Producer Internals & Advanced Patterns

### Q16: Walk through the complete path of a message from producer to broker.

**Answer:**

```
Producer Flow:
                                                    
1. Producer.send()                                  
       │                                            
2. Serializer (key + value)                         
       │                                            
3. Partitioner (select partition)                   
       │                                            
4. RecordAccumulator (batch by partition)           
       │                                            
5. Sender thread (per-broker batches)               
       │                                            
6. Compress (if enabled)                            
       │                                            
7. Network Client (NIO) → Broker                    
       │                                            
8. Broker appends to leader replica log             
       │                                            
9. ISR replicas fetch & acknowledge                 
       │                                            
10. Broker sends ProduceResponse                    
       │                                            
11. Producer callback executed                      
```

**Detailed steps:**

1. **`KafkaProducer.send()`** — The producer's `send()` method is asynchronous. It returns a `Future<RecordMetadata>` immediately. The call is thread-safe.

2. **Serialization** — Key and value serializers convert objects to bytes. Custom serializers or the built-in ones (StringSerializer, ByteArraySerializer, etc.) are used.

3. **Partitioning** — The partitioner determines which partition the record goes to:
   - If a partition is specified, use it directly
   - If no partition but a key exists: `Utils.murmur2(key) % numPartitions` (default)
   - If no key and no partition: Sticky Partitioner (Kafka 2.4+) batches records to a single partition, then rotates, improving batching efficiency
   - Custom partitioner: Implement `Partitioner` interface

4. **RecordAccumulator** — Records are buffered in the accumulator, grouped by topic-partition. The `batch.size` (default 16KB) determines the maximum batch size. The `linger.ms` (default 0) controls how long to wait before sending an incomplete batch.

5. **Sender Thread** — A background daemon thread takes batches from the accumulator, groups them by the destination broker, and sends them as ProduceRequests.

6. **Compression** — If enabled, the entire batch is compressed as a unit (not individual records). This is far more efficient.

7. **Network Send** — The NetworkClient uses Java NIO to send requests over TCP connections.

8. **Broker Append** — The leader broker appends the batch to the local log.

9. **Replication** — ISR replicas fetch the data (or receive it in the produce request if `acks=all`).

10. **Response** — The broker sends back offsets and any errors.

11. **Callback** — The producer's callback is invoked on the sender thread's I/O thread. **Important:** Callbacks should be fast; slow callbacks block the sender thread.

---

### Q17: What are the different acks configurations and their trade-offs?

**Answer:**

| `acks` | Behavior | Durability | Latency | Use Case |
|--------|----------|------------|---------|----------|
| `acks=0` | Fire and forget; producer doesn't wait for any acknowledgment | Lowest — data can be lost if broker crashes before writing | Lowest | Metrics, logs where loss is acceptable |
| `acks=1` | Leader writes to its log and acknowledges; doesn't wait for replicas | Medium — data lost if leader crashes before replicas catch up | Medium | General use, some data loss acceptable |
| `acks=all` | Leader waits for all in-sync replicas to acknowledge | Highest — data not lost unless all ISR brokers crash simultaneously | Highest | Financial data, critical events |

**With `acks=all`:**
- The number of required acknowledgments equals the current ISR size, NOT the replication factor. If ISR has shrunk (e.g., only 2 of 3 replicas are in ISR), only 2 acknowledgments are needed.
- `min.insync.replicas` (broker/topic config) provides a safety net: if ISR falls below this count, the broker rejects produce requests with `NOT_ENOUGH_REPLICAS`. This prevents writing to an under-replicated partition.
- **Best practice:** `acks=all` + `min.insync.replicas=2` + `replication.factor=3`

**Common interview trap:** "Does `acks=all` guarantee no data loss?" — No, not absolutely. If all ISR replicas crash simultaneously, data can still be lost. It guarantees durability only as long as at least one ISR replica survives.

---

### Q18: Explain the producer's batching mechanism and why it matters.

**Answer:**
Kafka's producer batches records for the same topic-partition together before sending. This is critical for throughput.

**Key configurations:**

1. **`batch.size`** (default 16KB) — Maximum batch size in bytes. When a batch reaches this size, it's sent immediately, regardless of `linger.ms`.

2. **`linger.ms`** (default 0) — Time to wait before sending a batch. With `linger.ms=0`, batches are sent as soon as the sender thread is ready. With `linger.ms=5`, the producer waits up to 5ms for more records to accumulate.

3. **`buffer.memory`** (default 32MB) — Total memory available for batching. If exhausted, `send()` blocks (up to `max.block.ms`) or throws `TimeoutException`.

**The throughput-latency trade-off:**

```
batch.size=16KB, linger.ms=0    → Low latency, lower throughput
batch.size=64KB, linger.ms=10   → Medium latency, high throughput  
batch.size=128KB, linger.ms=50  → Higher latency, very high throughput
```

**How it works internally:**
```
RecordAccumulator:
  ┌─────────────────────────────────────┐
  │ TopicPartition-0 → [Batch1] [Batch2]│
  │ TopicPartition-1 → [Batch1]         │
  │ TopicPartition-2 → [Batch1] [Batch2]│
  └─────────────────────────────────────┘
  Sender thread drains batches per broker:
  Broker-0: [TP0-Batch1, TP2-Batch1] → ProduceRequest
  Broker-1: [TP1-Batch1, TP0-Batch2] → ProduceRequest
```

**Sticky Partitioner (Kafka 2.4+):** When no key is specified, the sticky partitioner sends all records to a single partition until the batch is full or `linger.ms` expires. This maximizes batch size and throughput. Then it rotates to a new partition.

---

### Q19: How does the producer handle retries and idempotence?

**Answer:**

**Retries (`retries` config, default Integer.MAX_VALUE in Kafka 3.x):**

When a produce request fails, the producer can automatically retry. Retriable errors include:
- `LEADER_NOT_AVAILABLE` — Partition leader election in progress
- `NOT_ENOUGH_REPLICAS` — ISR below `min.insync.replicas`
- `NETWORK_EXCEPTION` — Transient network issue
- `REQUEST_TIMED_OUT` — Broker didn't respond in time

**The retry-ordering problem:** Without idempotence, retries can cause duplicates. If the broker successfully wrote the batch but the response was lost (network issue), the producer will retry, causing the same batch to be written twice.

**Idempotent Producer (`enable.idempotence=true`, default since Kafka 3.0):**

The idempotent producer prevents duplicates on retries by assigning each producer a **Producer ID (PID)** and a **Sequence Number** per topic-partition:

```
Broker tracks: PID + TopicPartition → Last Sequence Number

ProduceRequest contains: PID + Sequence Number

Broker logic:
  If sequence == expected     → Accept (normal case)
  If sequence < expected      → Reject as duplicate (already written)
  If sequence > expected      → Out of order (gap) → Reject
```

**Important caveat:** Idempotence only prevents duplicates within a single producer session. If a producer restarts, it gets a new PID, so duplicates across restarts are NOT prevented. For cross-session deduplication, you need Kafka Transactions or application-level idempotence.

**`max.in.flight.requests.per.connection`:**
- For idempotent producer: Must be ≤ 5 (Kafka enforces this)
- For non-idempotent with retries: If > 1, retries can reorder batches (Batch 2 sent after Batch 1, Batch 1 retries and ends up after Batch 2). Set to 1 for strict ordering with retries.

---

### Q20: What is a custom partitioner? When would you implement one?

**Answer:**
A custom partitioner lets you control which partition a record goes to, beyond the default key-hash strategy.

**Implementation:**
```java
public class RegionPartitioner implements Partitioner {
    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                         Object value, byte[] valueBytes, Cluster cluster) {
        int numPartitions = cluster.partitionCountForTopic(topic);
        if (key instanceof String) {
            String region = ((String) key).split("-")[0]; // e.g., "US-order123"
            switch (region) {
                case "US": return 0;
                case "EU": return 1;
                case "APAC": return 2;
                default: return numPartitions - 1;
            }
        }
        return 0;
    }
    // ... configure() and close() methods
}
```

**Use cases for custom partitioners:**

1. **Geographic Partitioning** — Route events from specific regions to specific partitions/brokers for data locality
2. **Hot Key Mitigation** — Distribute a high-volume key across multiple partitions while keeping low-volume keys together
3. **Tenant Isolation** — Multi-tenant systems where each tenant's data must go to specific partitions
4. **Priority Processing** — Route high-priority events to dedicated partitions consumed by dedicated consumers
5. **Co-location** — Ensure related entities (e.g., same customer's orders and payments) land in the same partition for ordered processing

**Caution:** Custom partitioners can create partition skew. Monitor partition sizes and lag to ensure even distribution.

---

### Q21: How do you handle the "buffer exhausted" scenario in producers?

**Answer:**

The `buffer.memory` (default 32MB) controls the total memory the producer can use for batching. When this buffer is full:

1. `send()` blocks for up to `max.block.ms` (default 60 seconds)
2. If still full after that, `TimeoutException` is thrown

**Root causes:**
- Producer sending faster than the broker can accept
- Broker is down or slow, causing backpressure
- `batch.size` too large, causing many incomplete batches
- Too many partitions leading to many small batches

**Solutions:**
- Increase `buffer.memory` (careful with heap usage)
- Reduce `batch.size` to send smaller batches more frequently
- Increase `linger.ms` to accumulate more records per batch, reducing the number of batches
- Monitor `record-error-rate` and `record-queue-time-avg` metrics
- Use async send with callbacks instead of `Future.get()` to avoid blocking
- Add circuit breaker / rate limiter in the producer application
- Scale the broker or increase partitions

---

## Section 4: Consumer Internals & Advanced Patterns

### Q22: Walk through the complete consumer poll loop and its internals.

**Answer:**

```java
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        processRecord(record);
    }
    consumer.commitSync(); // or commitAsync()
}
```

**What happens inside `poll()`:**

1. **Coordinator Discovery** — Consumer finds the Group Coordinator for its group
2. **Join Group** — If not already joined, consumer sends JoinGroupRequest
3. **Sync Group** — After rebalance, consumer receives its partition assignment
4. **Fetch Data** — Consumer sends FetchRequests to leaders of assigned partitions
5. **Return Records** — Fetched records are returned to the caller

**Internal architecture:**

```
Consumer Network Thread:
  ┌───────────────────────────────────────┐
  │ 1. Send FetchRequest to Broker A      │
  │ 2. Send FetchRequest to Broker B      │
  │ 3. Process FetchResponse from A       │
  │ 4. Process FetchResponse from B       │
  │ 5. Add records to completedFetches    │
  └───────────────────────────────────────┘

Application Thread (poll()):
  1. Check for completedFetches
  2. Deserialize records
  3. Apply interceptors
  4. Return ConsumerRecords
```

**Key configurations:**
- `fetch.min.bytes` (default 1B) — Minimum data the broker should return for a fetch request
- `fetch.max.wait.ms` (default 500ms) — Maximum time to wait before responding to a fetch
- `fetch.max.bytes` (default 50MB) — Maximum data returned in a single fetch
- `max.poll.records` (default 500) — Maximum records returned in a single poll()
- `max.partition.fetch.bytes` (default 1MB) — Maximum data per partition per fetch

---

### Q23: What is the consumer poll model? Why is it pull-based instead of push-based?

**Answer:**
Kafka uses a **pull model** where consumers explicitly request data from brokers. This is a deliberate design choice with important implications.

**Advantages of pull-based:**

1. **Natural Backpressure** — Consumers control the rate at which they consume. A slow consumer simply polls less frequently. In a push model, the broker must handle slow consumers (buffer, drop, or block).

2. **Batching Efficiency** — Consumers can request large batches in a single fetch, amortizing network overhead. Push systems often deliver one message at a time.

3. **Consumer Autonomy** — Consumers can rewind, skip, or replay from any offset. They control their position.

4. **Simpler Broker** — The broker doesn't need to track which consumers are ready, managing delivery queues, or handle flow control per consumer.

**Disadvantages of pull-based:**

1. **Latency** — There's inherent latency between when a message is available and when the consumer polls for it. Mitigated by long-polling (`fetch.max.wait.ms`).

2. **Busy-waiting** — If there's no data, consumers might busy-poll. Mitigated by `fetch.min.bytes` and `fetch.max.wait.ms` which make the broker hold the request until enough data accumulates or timeout expires.

3. **Complex Consumer Logic** — Consumers must manage the poll loop, heartbeats, and offset commits, which adds complexity compared to a simple message listener.

---

### Q24: How does a consumer know which broker to fetch from?

**Answer:**

The consumer maintains a **metadata cache** that maps topic-partitions to their current leader brokers.

**Metadata refresh flow:**

1. **Initial bootstrap** — Consumer connects to any broker from `bootstrap.servers` and sends a MetadataRequest
2. **Response** — Broker returns: topic-partition list, leader for each partition, ISR, and broker endpoints
3. **Cache** — Consumer caches this metadata locally
4. **Refresh triggers:**
   - `metadata.max.age.ms` (default 5 minutes) — Periodic refresh
   - Leader change — If a fetch returns `NOT_LEADER_OR_FOLLOWER`, consumer refreshes metadata
   - New topic/partition access — If consumer tries to fetch from a partition not in cache
5. **Connection** — Consumer establishes TCP connections to all brokers that lead its assigned partitions

**Important:** The consumer doesn't fetch from replica brokers — it always fetches from the **leader** of each partition. Followers only serve as backups.

---

### Q25: What happens if a consumer takes too long to process records?

**Answer:**

Two critical timers in the consumer:

1. **`max.poll.interval.ms`** (default 5 minutes) — Maximum time between two `poll()` calls. If the consumer doesn't call `poll()` within this time, it's considered dead and kicked out of the group, triggering a rebalance.

2. **`session.timeout.ms`** (default 45 seconds in Kafka 3.x, or 10 seconds depending on version) — Heartbeat timeout. The consumer must send heartbeats within this interval. The background heartbeat thread handles this, so processing doesn't affect heartbeats directly.

**Scenario: Processing takes too long**
```
Time 0:00 - Consumer polls, gets 500 records
Time 0:01 - Heartbeat thread sends heartbeat ✓
Time 0:02 - Heartbeat thread sends heartbeat ✓  (processing still ongoing)
Time 0:03 - Heartbeat thread sends heartbeat ✓
Time 4:00 - Still processing (haven't called poll in 4 min)
Time 5:01 - max.poll.interval.ms exceeded!
         → Coordinator marks consumer as dead
         → Rebalance triggered
         → Consumer gets CommitFailedException on next commit
```

**Solutions:**
- Increase `max.poll.interval.ms` for long processing
- Reduce `max.poll.records` to process fewer records per poll
- Use pause/resume: `consumer.pause()` to stop fetching while processing, `consumer.resume()` when ready
- Offload processing to a thread pool, but manage offsets carefully
- Use the new consumer assignment (manual) instead of group subscription

---

### Q26: Explain static group membership in Kafka consumers.

**Answer:**
**Static group membership** (Kafka 2.3+) allows a consumer to leave and rejoin a group without triggering a rebalance, as long as it rejoins within `session.timeout.ms`.

**Configuration:**
```properties
group.instance.id=consumer-1  # Unique, stable identifier
session.timeout.ms=300000     # 5 minutes
```

**How it works:**
- Without static membership: When a consumer leaves, its partitions are immediately reassigned
- With static membership: When a consumer with a `group.instance.id` disconnects, the coordinator keeps its partition assignment for `session.timeout.ms`. If it rejoins within this period, it gets its old partitions back without a full rebalance.

**Benefits:**
1. **Reduced Rebalances** — Brief network disruptions or restarts don't trigger rebalances
2. **Sticky Assignments** — Consumers keep their partitions, preserving local caches and state
3. **Critical for Kafka Streams** — State stores are tied to partitions; rebalances require expensive state restoration

**Use case:** In a Kubernetes environment where pods restart frequently, static membership prevents the entire consumer group from rebalancing every time a pod restarts.

---

### Q27: What is the difference between assign() and subscribe() in Kafka consumer?

**Answer:**

| Aspect | `subscribe()` | `assign()` |
|--------|---------------|------------|
| **Partition Assignment** | Automatic (by group coordinator) | Manual (you specify) |
| **Rebalance** | Yes — triggered on join/leave/failure | No — static assignment |
| **Consumer Group** | Required (must set `group.id`) | Not needed |
| **Offset Management** | Committed to `__consumer_offsets` | Still committed to `__consumer_offsets` (if `enable.auto.commit=true`) |
| **Topic Pattern** | Supports regex pattern subscription | Must specify exact partitions |
| **Use Case** | Most applications — managed assignment | Custom assignment logic, testing, consuming specific partitions |

**Important:** You cannot call both `subscribe()` and `assign()` on the same consumer instance. Doing so throws `IllegalStateException`.

**When to use `assign()`:**
- Consuming from a specific partition (e.g., for debugging)
- Custom partition assignment logic beyond what built-in assignors provide
- Simple single-consumer use cases where rebalance overhead is unnecessary
- Testing scenarios

---

## Section 5: Consumer Group & Rebalance

### Q28: What is a consumer group? How does Kafka ensure each partition is consumed by only one consumer in a group?

**Answer:**

A **consumer group** is a set of consumers that jointly consume a topic. Kafka ensures that **each partition is consumed by exactly one consumer within the group**, but the same partition can be consumed by consumers in different groups (hence pub-sub semantics).

**Mechanism:**
1. The **Group Coordinator** (a specific broker) manages the group's membership and partition assignment
2. When a consumer joins, it sends a `JoinGroupRequest` to the coordinator
3. The coordinator selects a **group leader** (the first consumer to join, not the Kafka controller)
4. The group leader runs the **partition assignor** algorithm to distribute partitions
5. The coordinator sends the assignment to all consumers in a `SyncGroupResponse`
6. Each consumer only fetches from its assigned partitions

**Enforcement:** The coordinator tracks which consumer is assigned which partition. If two consumers somehow try to consume the same partition, the coordinator's assignment ensures only one gets it. There's no distributed lock — it's enforced by the coordinator's authoritative assignment.

**Cross-group consumption:** Multiple consumer groups can consume the same topic independently. Each group has its own offset tracking.

```
Topic "orders" (3 partitions)

Group "inventory-service":         Group "analytics-service":
  Consumer A → P0, P1               Consumer X → P0
  Consumer B → P2                   Consumer Y → P1
                                     Consumer Z → P2
```

---

### Q29: Explain the consumer group rebalance process step by step.

**Answer:**

A **rebalance** redistributes partitions among consumers in a group. It's triggered by:
- Consumer joining the group
- Consumer leaving (clean shutdown or crash)
- Subscription change (new topics matching regex)
- Partition count change (topic altered)

**Step-by-step (Eager protocol — default before Kafka 2.4):**

```
Phase 1: Join Group
  All consumers → Coordinator: JoinGroupRequest (subscriptions, member info)
  Coordinator → Group Leader: Member list + metadata
  Group Leader: Runs assignor, creates assignment map
  
Phase 2: Sync Group
  All consumers → Coordinator: SyncGroupRequest
  Group Leader includes: Assignment map
  Coordinator → All consumers: SyncGroupResponse (their partition assignment)
  
Phase 3: Rebalance Callback
  Each consumer: onPartitionsRevoked() called (for old partitions)
  Each consumer: onPartitionsAssigned() called (for new partitions)
  
Phase 4: Fetch Begins
  Consumers start fetching from newly assigned partitions
```

**Problems with the Eager protocol:**
1. **Stop-the-world** — All consumers stop consuming, revoke all partitions, then get new assignments
2. **Unnecessary shuffling** — Even consumers whose assignment doesn't change revoke and re-acquire partitions
3. **Long rebalance times** — For large groups, can take minutes

**Cooperative Sticky Assignor (Kafka 2.4+)** solves this:
- Only moves partitions that need to be reassigned
- Consumers that keep their partitions never stop consuming
- Two-phase: first compute delta assignment, then verify
- Dramatically reduces rebalance disruption

---

### Q30: What are the different partition assignment strategies?

**Answer:**

| Assignor | Strategy | Rebalance Type | Kafka Version |
|----------|----------|----------------|---------------|
| **Range** | Divides partitions by consumer, assigns contiguous ranges. E.g., 7 partitions, 3 consumers: C1=[0,1,2], C2=[3,4], C3=[5,6] | Eager | 0.9+ |
| **RoundRobin** | Distributes all partitions (across all subscribed topics) one-by-one in round-robin | Eager | 0.9+ |
| **Sticky** | Maintains existing assignments as much as possible during rebalance; minimizes partition movement | Eager | 0.11+ |
| **CooperativeSticky** | Same as Sticky but uses incremental cooperative rebalancing; no stop-the-world | Cooperative | 2.4+ |

**Range Assignor (default):** Can lead to imbalance when consumers subscribe to different topics. If Topic A has 10 partitions and Topic B has 1, C1 gets 5+1=6 partitions while C2 gets 5+0=5.

**RoundRobin Assignor:** More balanced across topics but causes more partition movement during rebalance.

**Sticky Assignor:** Two goals: (1) balance the assignment, (2) minimize movement. When a consumer leaves, only its partitions are redistributed. Others keep theirs.

**CooperativeSticky:** Best of all worlds — sticky assignment + cooperative rebalancing. No stop-the-world. This is the recommended assignor for Kafka 2.4+.

**Configuration:**
```properties
partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor
```

---

### Q31: How do you handle a consumer group with more consumers than partitions?

**Answer:**

When there are more consumers than partitions, the extra consumers remain **idle**. They don't consume any data but they are part of the group.

**Implications:**
- Idle consumers waste resources (memory, connections)
- They serve as **standby** — if an active consumer fails, an idle consumer immediately takes over without a full rebalance
- The coordinator still sends heartbeats and tracks idle consumers
- This is sometimes called a "hot standby" pattern

**When this is acceptable:**
- High-availability requirements where failover must be fast
- Uneven load where you want backup consumers ready
- Testing environments

**When to fix it:**
- Remove extra consumers to save resources
- Increase partition count to match or exceed consumer count
- Use a different consumption pattern (e.g., manual assignment)

**Interview gotcha:** Some candidates think idle consumers help with throughput. They don't — they only help with failover speed. Throughput is limited by active consumers, which is limited by partitions.

---

### Q32: What is the Group Coordinator? How is it different from the Controller?

**Answer:**

| Aspect | Group Coordinator | Controller |
|--------|-------------------|------------|
| **What** | A broker that manages a specific consumer group | A broker that manages the entire cluster |
| **Selection** | Determined by hashing `group.id` → partition of `__consumer_offsets` → leader of that partition | Elected via ZooKeeper/KRaft; only one per cluster |
| **Responsibilities** | Join/sync group, rebalance, offset commits, heartbeat monitoring | Partition leader election, ISR management, topic creation/deletion, broker failure handling |
| **Failure** | Only affects that consumer group | Affects entire cluster until new controller elected |
| **Count** | One per consumer group (could be any broker) | Exactly one per cluster |

**How Group Coordinator is chosen:**
```
1. Hash the group.id: hash("my-group") → partition number
2. That partition of __consumer_offsets has a leader broker
3. That leader broker is the coordinator for "my-group"
```

This means different consumer groups can have different coordinators, distributing the load.

---

## Section 6: Offset Management & Delivery Semantics

### Q33: Where are consumer offsets stored? How has this evolved?

**Answer:**

**Evolution of offset storage:**

| Era | Storage | Details |
|-----|---------|---------|
| Kafka 0.7 | ZooKeeper | `/consumers/<group>/offsets/<topic>/<partition>` — Very slow, not scalable |
| Kafka 0.8.1+ | `__consumer_offsets` topic | Internal compacted topic with 50 partitions (default), replication factor 3 |
| Kafka 2.1+ | Committed offset + Consumer's position | Position is in-memory; committed offset is in the internal topic |

**How `__consumer_offsets` works:**

1. It's an internal topic with `cleanup.policy=compact`
2. Offset commits are key-value pairs: `key = <group, topic, partition>`, `value = <offset, metadata, timestamp>`
3. Compaction ensures only the latest offset per group-topic-partition is retained
4. The Group Coordinator (leader of the corresponding `__consumer_offsets` partition) handles offset commits and fetches

**Consumer position vs committed offset:**
- **Position** (in-memory) — The next offset the consumer will read. Advanced automatically as records are returned by `poll()`.
- **Committed offset** (persisted) — The last offset the consumer has acknowledged processing. Stored in `__consumer_offsets`.

These are separate! A consumer can be at position 1000 but have committed offset 950, meaning records 951-1000 are "in-flight" (delivered but not acknowledged).

---

### Q34: Explain the different offset commit strategies.

**Answer:**

### 1. Auto Commit (`enable.auto.commit=true`, default before Kafka 3.x)
```properties
enable.auto.commit=true
auto.commit.interval.ms=5000  # Every 5 seconds
```
- Consumer automatically commits the last offset returned by `poll()` every `auto.commit.interval.ms`
- **At-least-once by default** — If processing crashes after `poll()` returns records but before processing completes, those records will be re-delivered
- **Risk** — Offsets can be committed before processing completes, leading to data loss if configured incorrectly
- **Kafka 3.x change:** Default changed to `enable.auto.commit=false`

### 2. Synchronous Commit (`commitSync()`)
```java
consumer.commitSync(); // Blocks until commit completes
consumer.commitSync(Collections.singletonMap(tp, new OffsetAndMetadata(offset)));
```
- Blocks until the broker acknowledges the commit
- Safer but slower (round-trip to broker)
- Retries automatically on retriable failures

### 3. Asynchronous Commit (`commitAsync()`)
```java
consumer.commitAsync(new OffsetCommitCallback() {
    @Override
    public void onComplete(Map<TopicPartition, OffsetAndMetadata> offsets, Exception exception) {
        if (exception != null) log.error("Commit failed", exception);
    }
});
```
- Non-blocking; callback invoked when commit completes or fails
- Higher throughput but doesn't retry on failure (to avoid committing out-of-order offsets)
- Risk: If commit fails, the consumer may process duplicates

### 4. Combined Pattern (Best Practice)
```java
try {
    while (true) {
        ConsumerRecords<K, V> records = consumer.poll(Duration.ofMillis(100));
        for (ConsumerRecord<K, V> record : records) {
            process(record);
        }
        consumer.commitAsync(); // Fast async commit for normal operation
    }
} finally {
    consumer.commitSync(); // Guaranteed sync commit on shutdown
}
```

### 5. Per-Partition Commit
```java
Map<TopicPartition, OffsetAndMetadata> offsets = new HashMap<>();
for (ConsumerRecord<K, V> record : records) {
    process(record);
    offsets.put(new TopicPartition(record.topic(), record.partition()),
                new OffsetAndMetadata(record.offset() + 1));
}
consumer.commitSync(offsets); // Commit only processed partitions
```

---

### Q35: What are the delivery semantics in Kafka? Explain at-most-once, at-least-once, and exactly-once.

**Answer:**

### At-Most-Once
```
1. Commit offset first
2. Process records
3. If crash after commit but before processing → Records lost
```
Configuration: `enable.auto.commit=true` with auto-commit before processing
Use case: Metrics, monitoring data where occasional loss is acceptable

### At-Least-Once (Most Common)
```
1. Process records
2. Commit offset after processing
3. If crash after processing but before commit → Records re-delivered (duplicates)
```
Configuration: `enable.auto.commit=false`, manual commit after processing
Use case: Most applications; downstream must handle idempotence

### Exactly-Once (Hardest)
Three aspects to exactly-once:
1. **Producer-Broker** — Idempotent producer prevents duplicate writes
2. **Consumer-Producer** — Kafka transactions (consume-transform-produce)
3. **Consumer-Broker** — Read committed mode (consumer only reads transactionally committed records)

**Implementation:**
```java
// Producer
producer.initTransactions();
try {
    producer.beginTransaction();
    producer.send(record1);
    producer.send(record2);
    producer.sendOffsetsToTransaction(offsets, consumer.groupMetadata());
    producer.commitTransaction();
} catch (ProducerFencedException e) {
    producer.close();
} catch (KafkaException e) {
    producer.abortTransaction();
}
```

**Consumer side:**
```properties
isolation.level=read_committed  # Only read fully committed transactions
```

---

### Q36: How do you reset consumer offsets? What are the strategies?

**Answer:**

**Automatic reset strategies** (`auto.offset.reset`):

| Value | Behavior |
|-------|----------|
| `earliest` | Start from the beginning of the log (oldest available record) |
| `latest` | Start from the end of the log (only new records) |
| `none` | Throw `NoOffsetForPartitionException` if no committed offset exists |

**When does `auto.offset.reset` apply?** Only when the consumer has **no committed offset** for a partition. This happens when:
- New consumer group (never committed before)
- Committed offset has expired (older than `offsets.retention.minutes`)
- Offset was explicitly deleted

**Manual reset using CLI:**
```bash
# Reset to earliest
kafka-consumer-groups.sh --reset-offsets --group my-group --topic my-topic --to-earliest --execute

# Reset to latest
kafka-consumer-groups.sh --reset-offsets --group my-group --topic my-topic --to-latest --execute

# Reset to specific offset
kafka-consumer-groups.sh --reset-offsets --group my-group --topic my-topic --to-offset 5000 --execute

# Shift by amount
kafka-consumer-groups.sh --reset-offsets --group my-group --topic my-topic --shift-by -100 --execute

# Reset to datetime
kafka-consumer-groups.sh --reset-offsets --group my-group --topic my-topic --to-datetime 2025-01-01T00:00:00 --execute
```

**Programmatic reset:**
```java
consumer.seekToBeginning(partitions);
consumer.seekToEnd(partitions);
consumer.seek(partition, offset);
```

**Important:** `seek()` only works with `assign()`, not `subscribe()` (since subscribe uses automatic assignment). However, you can use `seek()` inside `onPartitionsAssigned()` callback after subscribe.

---

### Q37: What happens to offsets when a consumer group is deleted?

**Answer:**

When a consumer group is deleted:
1. All committed offsets for that group are removed from `__consumer_offsets`
2. The group coordinator no longer tracks the group
3. If the same `group.id` is used again, it's treated as a brand new group
4. The `auto.offset.reset` strategy determines where the new group starts consuming

**How to delete:**
```bash
kafka-consumer-groups.sh --delete --group my-group --bootstrap-server localhost:9092
```

**Important caveats:**
- You cannot delete a group that has active members
- If the group has no active members but has committed offsets, it can be deleted
- Deletion is permanent — there's no undo
- After deletion, if you restart consumers with the same `group.id`, they start fresh based on `auto.offset.reset`

**Offset expiration:** Even without explicit deletion, offsets expire after `offsets.retention.minutes` (default 7 days in Kafka 2.x, previously 1 day). If a group doesn't commit for this duration, its offsets are removed. This often causes confusion — a consumer group that was idle for a week suddenly starts from `auto.offset.reset`.

---

## Section 7: Kafka Storage & Log Internals

### Q38: How does Kafka store data on disk? Explain the directory structure.

**Answer:**

Kafka stores data in **log directories** configured by `log.dirs` (comma-separated list of directories).

**Directory structure:**
```
/kafka-logs/                        ← log.dirs
  ├── __consumer_offsets-0/          ← Internal topic partition
  │   ├── 00000000000000000000.log
  │   ├── 00000000000000000000.index
  │   └── 00000000000000000000.timeindex
  ├── __consumer_offsets-1/
  ├── my-topic-0/                   ← User topic partition
  │   ├── 00000000000000000000.log
  │   ├── 00000000000000000000.index
  │   ├── 00000000000000000000.timeindex
  │   ├── 00000000000005367851.log
  │   ├── 00000000000005367851.index
  │   └── 00000000000005367851.timeindex
  ├── my-topic-1/
  ├── my-topic-2/
  ├── recovery-point-offset-checkpoint
  ├── replication-offset-checkpoint
  └── meta.properties               ← broker.id
```

**Key files:**

| File | Purpose |
|------|---------|
| `<base-offset>.log` | The actual message data (RecordBatch format) |
| `<base-offset>.index` | Sparse offset → byte-position index for fast lookup |
| `<base-offset>.timeindex` | Timestamp → offset index for time-based lookups |
| `leader-epoch-checkpoint` | Tracks leader epochs for each partition (prevents data loss during unclean leader election) |
| `recovery-point-offset-checkpoint` | Last flushed offset per partition |
| `replication-offset-checkpoint` | High watermark per replica |

**Multiple log.dirs:** If `log.dirs` specifies multiple directories, Kafka distributes partitions across them. This is useful for:
- Utilizing multiple disks
- Separating high-throughput and low-throughput topics on different disks
- JBOD (Just a Bunch Of Disks) configuration

If one disk fails, only partitions on that disk are affected (unlike RAID where one disk failure can affect all data).

---

### Q39: What is the zero-copy optimization in Kafka?

**Answer:**

Zero-copy is one of Kafka's most important performance optimizations for the **consumer read path**.

**Traditional data transfer (without zero-copy):**
```
1. Application calls read() → OS reads from disk to Page Cache (kernel space)
2. Data copied from Page Cache to Application Buffer (user space)
3. Application calls send() → Data copied from Application Buffer to Socket Buffer (kernel space)
4. Data copied from Socket Buffer to NIC Buffer
Total: 4 copies, 2 context switches
```

**Zero-copy transfer (Kafka's approach using sendfile):**
```
1. Kafka calls FileChannel.transferTo() / sendfile()
2. OS reads from disk to Page Cache
3. Data transferred directly from Page Cache to NIC Buffer (via DMA)
Total: 2 copies (disk→cache, cache→NIC), minimal CPU involvement
```

**Why this matters:**
- Data never enters JVM heap → No GC pressure
- CPU is barely involved → freed for application logic
- Throughput limited by disk/network bandwidth, not CPU
- Works because Kafka doesn't need to inspect or modify the data on the read path

**Prerequisite:** The consumer must read from the beginning of records that are still in the OS page cache. If records have been evicted from cache, they must be read from disk, which is slower but still uses zero-copy for the transfer to network.

**Producer side:** Zero-copy does NOT apply to the produce path — the producer must send data through the JVM (serialization, compression, batching), which involves user-space processing.

---

### Q40: How does Kafka use the OS page cache? Why not cache in JVM?

**Answer:**

Kafka deliberately **avoids caching data in the JVM heap** and instead relies on the **OS page cache**. This is a foundational design decision.

**Why not JVM cache:**
1. **GC Problem** — Caching gigabytes of data in JVM heap causes severe GC pauses (Stop-The-World). A 32GB heap can have GC pauses of seconds.
2. **Process Restart** — JVM cache is lost on broker restart. OS page cache survives process restarts since it's managed by the kernel.
3. **Memory Efficiency** — JVM object overhead is significant (~2x for Java objects vs raw bytes). Page cache stores the exact bytes on disk.
4. **Sizing** — OS can use all free RAM for page cache. JVM heap competes with application logic.

**How page cache helps Kafka:**

```
Producer writes → Broker appends to log → Data enters Page Cache → Eventually flushed to disk
                                                                    ↓
Consumer reads → Broker checks Page Cache → If hit: return from memory (fast!)
                                          → If miss: read from disk (slower)
```

**Key configurations:**
- `log.flush.interval.messages` — Don't set this; let OS handle flushing (default is to let OS flush)
- `log.flush.interval.ms` — Don't set this either; OS flushing is more efficient
- Kafka relies on the OS's dirty page flushing mechanism (Linux: `vm.dirty_ratio`, `vm.dirty_background_ratio`)

**Best practice:** Do NOT force sync flushes. Let the OS manage flushing. Kafka's replication provides durability — data is on multiple brokers' page caches. The probability of all replicas crashing simultaneously with unflushed data is extremely low.

---

### Q41: What is the role of the .index file? Why is it sparse?

**Answer:**

The `.index` file maps **offsets to byte positions** in the `.log` file. It enables fast binary search for a specific offset without scanning the entire log.

**Sparse indexing approach:**

Instead of indexing every offset, Kafka indexes every Nth offset (controlled by `index.interval.bytes`, default 4096 bytes). This means an entry is added to the index for roughly every 4096 bytes of message data.

**Why sparse?**
- **Memory efficiency** — A dense index for a 1GB segment with 1KB messages would have ~1M entries (~24MB per partition). With sparse indexing, it's ~250K entries (~6MB).
- **Mmap friendly** — The index file fits comfortably in memory and can be memory-mapped for fast access.
- **Good enough** — Binary search finds the closest indexed offset, then a short sequential scan finds the exact offset.

**Lookup algorithm:**
```
1. Find the segment: Base offset of segment ≤ target offset
2. Binary search .index file: Find largest offset ≤ target
3. Read byte position from index entry
4. Seek to that position in .log file
5. Scan sequentially from there (typically 0-few messages)
```

**Example:**
```
.index file:
  Offset    Position
  0         0
  33        4120       ← 4120 bytes of messages produced 33 messages
  67        8240
  102       12360

To find offset 50:
  1. Binary search → 33 (largest ≤ 50)
  2. Seek to position 4120 in .log
  3. Scan forward from offset 34 → 35 → ... → 50 ✓
```

---

### Q42: How does Kafka handle disk failure when using multiple log directories?

**Answer:**

When `log.dirs` specifies multiple directories and one disk fails:

**Default behavior:**
1. The broker **shuts down** if any log directory fails (since Kafka 1.0, `log.dir.failure.timeout.ms=30000`)
2. All partitions on the broker become unavailable until the broker is restarted
3. Other brokers take over leadership of the affected partitions

**Configurable behavior:**
```properties
# Time before broker shuts down after disk failure (default 30s)
log.dir.failure.timeout.ms=30000

# In Kafka 2.x+, you can set this to not shut down:
# But there's no clean "skip failed dir" option in community Kafka
```

**Recovery process:**
1. Replace the failed disk
2. Restart the broker
3. The broker detects missing replica data and initiates partition reassignment or fetches from leaders

**Best practices:**
- Use JBOD (Just a Bunch Of Disks) with multiple `log.dirs` on separate disks
- Monitor disk health proactively (SMART stats, disk space)
- Set `log.retention.bytes` to prevent any single disk from filling up
- Use `kafka-reassign-partitions.sh` to move partitions off a failing disk before it fails completely
- Consider `log.dirs` on different mount points for isolation

**Interview insight:** Unlike RAID which provides disk-level redundancy, Kafka provides **partition-level redundancy** through replication. If a disk fails, you lose the replicas on that disk, but other replicas on other brokers still have the data.

---

## Section 8: Replication & ISR

### Q43: Explain Kafka's replication model in detail.

**Answer:**

Kafka replicates each partition across multiple brokers for fault tolerance.

**Key concepts:**

1. **Replica** — A copy of a partition. Each partition has one leader and N-1 followers.
2. **Leader** — Handles all read/write requests for the partition. Producers write to the leader; consumers read from the leader.
3. **Follower** — Passively replicates the leader's log. Does NOT serve client requests (unlike primary-replica systems where replicas can serve reads).
4. **ISR (In-Sync Replicas)** — Replicas that are fully caught up with the leader. Includes the leader + caught-up followers.
5. **High Watermark (HW)** — The offset up to which all ISR replicas have committed. Consumers can only read up to the HW.
6. **LEO (Log End Offset)** — The offset of the next record to be appended. Each replica has its own LEO; the leader tracks all replicas' LEOs.

**Replication flow:**

```
Producer ──write──▶ Leader Broker
                        │
                   ┌────┼────┐
                   │    │    │
              Follower Follower  (ISR)
              pulls    pulls
              data     data
                   │    │
                   ▼    ▼
              LEO=100 LEO=98
              
Leader: LEO=102, HW=min(all ISR LEOs)=98
Consumer reads up to HW=98
```

**Follower fetching:** Followers don't receive data in the produce path (unless using KIP-392 in Kafka 2.4+ for follower fetching). By default, followers send FetchRequests to the leader, which serves two purposes:
1. Replicate data
2. Serve as a heartbeat (proof the follower is alive)

If a follower hasn't fetched within `replica.lag.time.max.ms` (default 30 seconds), it's removed from the ISR.

---

### Q44: What is the High Watermark (HW) and how does it prevent data inconsistency?

**Answer:**

The **High Watermark** is the offset up to which all ISR replicas have committed their data. It's the boundary between "safe" (replicated) and "unsafe" (not yet replicated) data.

**HW update process:**

```
Step 1: Producer writes to leader (LEO advances)
Step 2: Followers fetch from leader, advancing their LEO
Step 3: Leader updates HW = min(LEO of all ISR replicas)
Step 4: Leader includes HW in next FetchResponse to followers
Step 5: Followers update their HW = min(own LEO, leader's HW)
```

**Why HW prevents inconsistency:**

Consider a scenario without HW:
```
1. Leader has LEO=100, Follower has LEO=95
2. Leader crashes
3. Follower becomes new leader with LEO=95
4. Old leader recovers with LEO=100
5. Inconsistency! Old leader has data (95-100) that new leader doesn't have
```

With HW:
```
1. Leader has LEO=100, HW=95 (follower is at 95)
2. Leader crashes
3. Follower becomes new leader with LEO=95, HW=95
4. Old leader recovers, truncates log to HW=95, then fetches from new leader
5. Consistency maintained ✓
```

**Consumer guarantee:** Consumers can only read up to the HW. This ensures consumers never read data that could be rolled back (uncommitted data).

---

### Q45: What is Leader Epoch and how does it improve upon HW-based truncation?

**Answer:**

**Leader Epoch** was introduced in Kafka 0.11 (KIP-101) to address a data loss scenario with HW-based truncation.

**The HW truncation problem:**

```
1. Leader A has messages up to offset 100, HW=80
2. Follower B has messages up to offset 80, HW=80
3. Leader A crashes; Follower B becomes new Leader B
4. Leader B receives new messages: offsets 81-90
5. Leader A restarts, truncates to HW=80
6. Messages 81-100 from original Leader A are LOST!
   (They were committed from A's perspective but HW was 80)
```

**Leader Epoch solution:**

Each time a partition's leader changes, a new **epoch** (monotonically increasing number) is assigned. The `leader-epoch-checkpoint` file stores: `[epoch → startOffset]`.

**How it works:**
```
1. Before becoming leader, new leader writes a new epoch entry
2. When an old leader recovers, instead of truncating to HW, it:
   a. Sends OffsetsForLeaderEpochRequest to the current leader
   b. "What is the last offset for epoch X?" (where X was its last epoch)
   c. Current leader responds with the last offset in that epoch
   d. Old leader truncates to that offset instead of HW
```

**Why this is better:** The leader epoch approach guarantees that replicas truncate to the exact point where they diverged, not to a potentially stale HW. This prevents both data loss and inconsistency.

---

### Q46: What is unclean leader election? Why is it dangerous?

**Answer:**

**Unclean leader election** occurs when a non-ISR replica is elected as leader because no ISR replica is available.

**Scenario:**
```
Topic with replication.factor=3
1. Leader (Broker A) crashes
2. Follower (Broker B) is in ISR → should become leader
3. But Broker B also crashes! 
4. Only Follower (Broker C) is alive, but it's OUT of ISR (lagging)
5. Two options:
   a. Wait for an ISR replica to come back (availability loss)
   b. Elect Broker C as leader (data loss)
```

**Configuration:**
```properties
unclean.leader.election.enable=true   # Allow non-ISR leader (availability > consistency)
unclean.leader.election.enable=false  # Don't allow (consistency > availability, default since Kafka 0.11)
```

**Why dangerous:**
- The out-of-sync replica is missing messages that were committed on the old leader
- When it becomes leader, consumers see the gap (messages are gone)
- The old leader, when it recovers, truncates to match the new leader, permanently losing data
- This violates the guarantee that `acks=all` prevents data loss

**When to enable:**
- When availability is more critical than consistency (e.g., real-time analytics where a gap is acceptable)
- When you have monitoring to detect and alert on under-replicated partitions

**Best practice:** Keep `unclean.leader.election.enable=false` and ensure you have enough brokers and replication factor to avoid the scenario where no ISR replicas are available.

---

### Q47: What happens when a broker goes down? Walk through the complete failover process.

**Answer:**

```
Step 1: Broker B crashes (ZooKeeper/KRaft session expires)

Step 2: Controller detects broker failure
  - ZooKeeper ephemal node deletion or KRaft heartbeat timeout
  - Controller reads the broker's partition assignments

Step 3: Controller elects new leaders for partitions led by Broker B
  - For each partition: Select first replica in ISR that's alive
  - Update ZooKeeper/KRaft metadata
  - Send LeaderAndIsrRequest to new leaders
  - Send UpdateMetadataRequest to all brokers

Step 4: New leaders begin serving requests
  - Producers/consumers may get NOT_LEADER_OR_FOLLOWER errors
  - They refresh metadata and reconnect to new leaders

Step 5: ISR may shrink
  - If Broker B was the only follower, ISR = [Leader only]
  - min.insync.replicas may cause produce failures if ISR < min

Step 6: When Broker B recovers
  - Registers with ZooKeeper/KRaft
  - Controller assigns it as follower for its old partitions
  - Broker B fetches missing data from current leader (recovery process)
  - Once caught up, rejoins ISR

Step 7: Controller may or may not re-elect Broker B as leader
  - By default: No — preferred leader election must be triggered
  - auto.leader.rebalance.enable=true triggers periodic preferred leader election
```

**Recovery for out-of-sync replica:**
- If only a few messages behind: High-throughput recovery (fetch missing messages)
- If significantly behind: Truncation to diverging point + full fetch (using leader epoch)
- If the log is completely gone: Full replication from the leader

---

### Q48: What is preferred leader election? How does it help?

**Answer:**

**Preferred leader** is the first replica in the replica assignment list. For example, if a partition's replica list is `[Broker 0, Broker 1, Broker 2]`, Broker 0 is the preferred leader.

**Why it matters:**
- Over time, leadership can become unevenly distributed due to broker failures and recoveries
- If Broker 0 was the original leader for many partitions but failed and Broker 1 took over, when Broker 0 recovers, it doesn't automatically reclaim leadership
- This creates load imbalance — some brokers handle more leader partitions than others

**How preferred leader election works:**

1. **Automatic** (`auto.leader.rebalance.enable=true`, default): A background thread periodically checks if the preferred leader is in ISR but not the current leader. If so, it triggers a leadership change.

2. **Manual:**
```bash
kafka-leader-election.sh --bootstrap-server localhost:9092 \
  --election-type preferred \
  --topic my-topic --partition 0
```

**Benefits:**
- Even load distribution across brokers
- Predictable data flow patterns (useful for network topology)
- Better utilization of page cache (leaders handle all reads and writes)

**When to trigger manually:**
- After adding new brokers and reassigning partitions
- After replacing a failed broker
- When monitoring shows uneven broker CPU/network usage

---

## Section 9: Kafka Controller & KRaft Mode

### Q49: What is the Kafka Controller? What are its responsibilities?

**Answer:**

The **Controller** is one of the most critical components in a Kafka cluster. It's a special broker (only one per cluster) responsible for managing the cluster's state.

**Responsibilities:**

1. **Partition Leadership Election** — When a broker fails, the controller elects new leaders for all partitions led by that broker
2. **ISR Management** — Updates ISR when replicas join or leave
3. **Broker Management** — Detects broker failures (via ZooKeeper session timeout or KRaft heartbeat)
4. **Topic Management** — Handles topic creation, deletion, and partition changes
5. **Reassignment** — Manages partition reassignment across brokers
6. **ACL Updates** — Propagates ACL changes to all brokers
7. **Metadata Propagation** — Sends UpdateMetadataRequest to all brokers when cluster state changes
8. **Preferred Leader Election** — Runs periodic preferred leader rebalancing

**Controller election:**
- **ZooKeeper mode:** First broker to create `/controller` ephemeral node becomes the controller. If it crashes, another broker creates the node and becomes the new controller.
- **KRaft mode:** The active controller is elected from the KRaft quorum of controller nodes using the Raft consensus protocol.

**Controller failover:**
- On failover, the new controller:
  1. Reads all metadata from ZooKeeper/KRaft
  2. Initializes all partition states
  3. Elects leaders for partitions that need new leaders
  4. Sends UpdateMetadataRequest to all brokers

This failover can be slow with millions of partitions in ZooKeeper mode (30+ seconds). KRaft mode reduces this to sub-second.

---

### Q50: Explain KRaft mode in detail. How does it work without ZooKeeper?

**Answer:**

**KRaft (Kafka Raft)** is Kafka's built-in consensus protocol that replaces ZooKeeper for metadata management.

**Architecture:**

```
KRaft Cluster:
┌──────────────────────────────────────────────────┐
│  Controller Quorum (Raft-based)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Controller│  │Controller│  │Controller│       │
│  │  (Active)│  │(Standby) │  │(Standby) │       │
│  └──────────┘  └──────────┘  └──────────┘       │
│       │              │              │             │
│  ┌────▼──────────────▼──────────────▼─────┐      │
│  │  @__metadata_quorum topic (internal)   │      │
│  │  (Raft log for metadata)               │      │
│  └────────────────────────────────────────┘      │
└──────────────────────────────────────────────────┘

Broker nodes:
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Broker 0 │  │ Broker 1 │  │ Broker 2 │
│(fetches   │  │(fetches   │  │(fetches   │
│ metadata) │  │ metadata) │  │ metadata) │
└──────────┘  └──────────┘  └──────────┘
```

**How KRaft works:**

1. **Controller Quorum** — A set of controller nodes (typically 3 for production) form a Raft quorum. One is the active controller; others are standby.

2. **Metadata Log** — All metadata changes (topic creation, partition assignment, broker registration) are written to an internal Raft log (stored as the `@__metadata_quorum` topic). This is the single source of truth.

3. **Active Controller** — Processes all metadata changes, writes them to the Raft log, and notifies brokers.

4. **Broker Metadata Sync** — Brokers fetch metadata from the active controller (similar to how consumers fetch data). This replaces ZooKeeper watches.

5. **Snapshot** — Periodically, the controller takes a snapshot of the full metadata state to avoid replaying the entire log on startup.

**Advantages over ZooKeeper:**

| Aspect | ZooKeeper | KRaft |
|--------|-----------|-------|
| Partitions supported | ~200K | Millions |
| Controller failover | 30+ seconds | Sub-second |
| Deployment | Separate ZK ensemble | No separate service |
| Metadata consistency | Two systems (ZK + broker) | Single source (Raft log) |
| Scaling | ZK is bottleneck | No bottleneck |

**Migration to KRaft:** Kafka 3.6+ supports migration from ZooKeeper to KRaft without downtime. The process involves:
1. Deploy KRaft controllers alongside ZooKeeper
2. Migrate metadata from ZooKeeper to KRaft
3. Switch brokers to fetch from KRaft controllers
4. Remove ZooKeeper

---

### Q51: What is the difference between combined mode and separated mode in KRaft?

**Answer:**

**Combined Mode (Controller + Broker on same node):**
```
Node 1: [Controller + Broker]
Node 2: [Controller + Broker]
Node 3: [Controller + Broker]
```
- Simpler deployment (fewer nodes)
- Suitable for development and small deployments
- Controller and broker share resources (CPU, memory, disk)
- Must run at least 3 combined nodes for quorum
- Not recommended for large production clusters

**Separated Mode (Dedicated controllers and brokers):**
```
Controller Node 1: [Controller only]
Controller Node 2: [Controller only]
Controller Node 3: [Controller only]

Broker Node 1: [Broker only]
Broker Node 2: [Broker only]
Broker Node 3: [Broker only]
...
```
- Recommended for production
- Controllers are lightweight (only metadata, no data storage)
- Brokers are dedicated to data serving
- Independent scaling of controllers and brokers
- Better fault isolation — broker failures don't affect controller quorum

**Configuration:**
```properties
# Combined mode
process.roles=broker,controller

# Separated mode (controller only)
process.roles=controller

# Separated mode (broker only)
process.roles=broker
```

---

## Section 10: Kafka Security

### Q52: What security features does Kafka provide?

**Answer:**

Kafka provides four layers of security:

### 1. Authentication (Who are you?)
- **SASL/PLAIN** — Username/password (simple, but credentials stored in plaintext or external)
- **SASL/SCRAM-SHA-256/512** — Salted, hashed credentials stored in ZooKeeper/KRaft (more secure)
- **SASL/GSSAPI (Kerberos)** — Enterprise SSO integration
- **SASL/OAUTHBEARER** — OAuth 2.0 token-based authentication (modern, cloud-native)
- **mTLS** — Mutual TLS authentication using client certificates

### 2. Authorization (What can you do?)
- **ACLs (Access Control Lists)** — Fine-grained permissions:
  - Resource: Topic, Cluster, Group, TransactionalId, DelegationToken
  - Operation: Read, Write, Create, Delete, Alter, Describe, ClusterAction
  - Principal: User or group
  - Host: IP address or `*` for any
```bash
kafka-acls.sh --add --allow-principal User:alice --operation Read --topic orders
```
- **Super Users** — Bypass all ACL checks (`super.users=User:admin`)

### 3. Encryption (Is data protected in transit?)
- **TLS/SSL** — Encrypt all communication between clients and brokers, and inter-broker communication
- **At-rest encryption** — Kafka doesn't natively encrypt data at rest; use disk-level encryption (LUKS) or cloud provider encryption

### 4. Audit (Who did what?)
- Not natively built into Kafka
- Achieved through: Custom authorizer logging, interceptors, or external audit systems

**Typical production setup:** mTLS for authentication + TLS for encryption + ACLs for authorization.

---

### Q53: How does SASL/SCRAM authentication work in Kafka?

**Answer:**

SASL/SCRAM (Salted Challenge Response Authentication Mechanism) provides a secure way to authenticate without transmitting passwords.

**Setup process:**

1. **Create SCRAM credentials in ZooKeeper/KRaft:**
```bash
kafka-configs.sh --zookeeper localhost:2181 \
  --alter --add-config 'SCRAM-SHA-256=[password=alice-secret],SCRAM-SHA-512=[password=alice-secret]' \
  --entity-type users --entity-name alice
```

2. **Broker configuration:**
```properties
sasl.enabled.mechanisms=SCRAM-SHA-512
sasl.mechanism.inter.broker.protocol=SCRAM-SHA-512
sasl.mechanism.controller.protocol=SCRAM-SHA-512
listener.name.broker.scram-sha-512.sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required \
  username="admin" \
  password="admin-secret";
```

3. **Client configuration:**
```properties
security.protocol=SASL_SSL
sasl.mechanism=SCRAM-SHA-512
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required \
  username="alice" \
  password="alice-secret";
```

**SCRAM handshake:**
```
Client → Server: SCRAM-SHA-512, client-first-message (username, random nonce)
Server → Client: server-first-message (salt, iteration count, combined nonce)
Client → Server: client-final-message (proof using password + salt + nonce)
Server → Client: server-final-message (server proof)
```

**Advantages over PLAIN:**
- Password never transmitted over the network
- Salt and iteration count make offline attacks difficult
- Credentials stored as salted hash in ZooKeeper/KRaft
- Supports credential rotation without broker restart

---

### Q54: How do you implement authorization in Kafka? Explain ACLs.

**Answer:**

**ACLs (Access Control Lists)** control which principals can perform which operations on which resources.

**ACL structure:**
```
Principal: User:alice
Host: 192.168.1.*
Operation: READ
PermissionType: ALLOW
Resource: Topic:orders
```

**Resource types:**
- `Topic` — Read, Write, Create, Delete, Alter, Describe, DescribeConfigs, AlterConfigs
- `Cluster` — Create, ClusterAction, DescribeConfigs, AlterConfigs, IdempotentWrite, Alter
- `Group` — Read, Describe, Delete
- `TransactionalId` — Describe, Write
- `DelegationToken` — Describe

**Common ACL operations:**
```bash
# Allow alice to read from topic orders
kafka-acls.sh --bootstrap-server localhost:9092 \
  --add --allow-principal User:alice --operation Read --topic orders

# Allow alice to produce to topic orders from specific IP
kafka-acls.sh --bootstrap-server localhost:9092 \
  --add --allow-principal User:alice --operation Write --topic orders --allow-host 10.0.0.5

# Deny bob from deleting any topic
kafka-acls.sh --bootstrap-server localhost:9092 \
  --add --deny-principal User:bob --operation Delete --topic '*'

# Allow group my-group to consume
kafka-acls.sh --bootstrap-server localhost:9092 \
  --add --allow-principal User:alice --operation Read --group my-group

# List all ACLs
kafka-acls.sh --bootstrap-server localhost:9092 --list
```

**Important:** By default, if no ACLs exist, all users have access. To enforce security, set:
```properties
allow.everyone.if.no.acl.found=false
```

**Best practices:**
- Use super users for admin operations
- Grant least privilege per service
- Use wildcard principals with AD/LDAP integration for group-based authorization
- Regularly audit ACLs
- Automate ACL management via CI/CD pipelines

---

### Q55: What is mutual TLS (mTLS) in Kafka? How is it different from one-way TLS?

**Answer:**

**One-way TLS (server authentication):**
- Client verifies the broker's certificate
- Data is encrypted in transit
- Broker does NOT verify the client's identity
- Use case: Encryption only, no client authentication

**Mutual TLS (mTLS):**
- Client verifies the broker's certificate (same as one-way)
- Broker ALSO verifies the client's certificate
- Client must present a valid certificate signed by a trusted CA
- Use case: Both encryption AND authentication

**mTLS Configuration:**

Broker:
```properties
listeners=SSL://:9092
ssl.keystore.location=/var/kafka/broker.keystore.jks
ssl.keystore.password=keystore-pass
ssl.key.password=key-pass
ssl.truststore.location=/var/kafka/broker.truststore.jks
ssl.truststore.password=truststore-pass
ssl.client.auth=required  # Broker requires client certificate
```

Client:
```properties
security.protocol=SSL
ssl.keystore.location=/var/client/client.keystore.jks
ssl.keystore.password=keystore-pass
ssl.key.password=key-pass
ssl.truststore.location=/var/client/client.truststore.jks
ssl.truststore.password=truststore-pass
```

**Certificate management:**
- Each client gets a unique certificate with CN (Common Name) as the principal
- Broker extracts the CN from the client certificate for ACL evaluation
- Certificate rotation can be done without downtime (reload keystore via JMX or Kafka's dynamic config)
- Use a PKI infrastructure (HashiCorp Vault, AWS ACM, etc.) for certificate lifecycle management

---

## Section 11: Kafka Monitoring & Operations

### Q56: What are the most critical Kafka metrics to monitor?

**Answer:**

### Broker Metrics
| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `UnderReplicatedPartitions` | Partitions where ISR < assigned replicas | > 0 for extended time |
| `OfflinePartitionsCount` | Partitions without a leader | > 0 (critical!) |
| `ActiveControllerCount` | Should be exactly 1 | != 1 |
| `BytesInPerSec` / `BytesOutPerSec` | Network throughput | Near network capacity |
| `MessagesInPerSec` | Message rate | Capacity planning |
| `RequestHandlerAvgIdlePercent` | Broker request handler pool utilization | < 0.3 (overloaded) |
| `ReplicationLag` | How far followers are behind leaders | > threshold |
| `DiskUsage` | Disk space per log directory | > 85% |

### Producer Metrics
| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `record-error-rate` | Failed produce attempts | > 0 |
| `record-send-rate` | Successful produces | Drop in rate |
| `request-latency-avg` | Average produce latency | > SLA |
| `record-queue-time-avg` | Time records spend in accumulator | > `linger.ms` significantly |
| `buffer-available-bytes` | Available producer buffer | Near 0 (exhaustion) |

### Consumer Metrics
| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `records-lag-max` | Maximum lag across all partitions | Growing lag |
| `records-consumed-rate` | Consumption rate | Drop in rate |
| `commit-latency-avg` | Offset commit latency | High latency |
| `join-rate` / `sync-rate` | Rebalance frequency | High rate = thrashing |
| `records-per-request-avg` | Records per fetch | Very low = inefficient |

### Under Replicated Partitions (URP)
This is the **most critical metric**. URP > 0 means some partitions don't have all their replicas in sync. Causes:
- Broker down
- Network partition
- Slow follower (disk I/O, CPU)
- Misconfigured `num.recovery.threads.per.data.dir`

---

### Q57: How do you monitor consumer lag? What tools are available?

**Answer:**

**Consumer lag** = Log End Offset (latest offset in the partition) − Committed Offset (consumer's last processed offset)

```
Lag = LEO - Committed Offset = 1050 - 1000 = 50 records behind
```

**Monitoring tools:**

1. **CLI:**
```bash
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group my-group

# Output:
# TOPIC    PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
# orders   0          1000            1050            50
# orders   1          2000            2030            30
```

2. **Kafka Manager / CMAK** — Web UI for cluster management with lag visualization

3. **Burrow (LinkedIn)** — Dedicated lag monitoring tool with:
   - Multi-cluster support
   - SLA-based alerting (not just absolute lag, but lag trend)
   - REST API for integration
   - Evaluation of consumer status (OK, WARNING, ERROR)

4. **Prometheus + JMX Exporter** — Export Kafka JMX metrics to Prometheus, visualize in Grafana

5. **Confluent Control Center** — Commercial tool with comprehensive monitoring

6. **Kafka Exporter** — Prometheus exporter specifically for consumer group lag

**Lag alerting strategies:**

- **Absolute lag** — Alert when lag > N records. Problem: N depends on throughput; 1000 lag might be 1 second or 1 hour.
- **Time-based lag** — Estimate time behind: `lag / consumption_rate = time_behind`. Alert when time_behind > SLA.
- **Trend-based** — Alert when lag is consistently growing (consumer can't keep up) vs. occasional spikes (normal during bursts).

---

### Q58: How do you handle a Kafka cluster that's running out of disk space?

**Answer:**

This is a common production issue. Here's the escalation plan:

### Immediate Actions
1. **Check retention settings** — Are they appropriate?
```bash
kafka-configs.sh --describe --topic my-topic --bootstrap-server localhost:9092
```
2. **Reduce retention** temporarily to free up space:
```bash
kafka-configs.sh --alter --topic my-topic \
  --add-config retention.ms=86400000 --bootstrap-server localhost:9092
```
3. **Delete unused topics** that are consuming space

### Short-term Actions
4. **Trigger log compaction** manually for compacted topics:
```bash
kafka-run-class.sh kafka.admin.LogCompactionTest --topic my-topic ...
```
5. **Add more disk** — If using JBOD, add a new `log.dirs` path
6. **Reassign partitions** — Move partitions from full brokers to less full ones:
```bash
kafka-reassign-partitions.sh --generate ...
kafka-reassign-partitions.sh --execute ...
```

### Long-term Actions
7. **Capacity planning** — Calculate projected growth and provision accordingly
8. **Tiered storage** (Kafka 3.x+ / Confluent) — Move older segments to S3/GCS
9. **Monitoring** — Set up disk usage alerts at 70%, 80%, 85%
10. **Auto-expansion** — Use Kubernetes with dynamic volume provisioning

**Prevention:**
- Monitor `log.size` per topic and per broker
- Set `retention.bytes` in addition to `retention.ms` for belt-and-suspenders
- Use `disk.usage.warn.threshold` and `disk.usage.critical.threshold` broker configs

---

## Section 12: Kafka Performance Tuning

### Q59: How do you tune a Kafka producer for maximum throughput?

**Answer:**

```properties
# Batching — Increase batch size and add delay
batch.size=65536          # 64KB (default 16KB)
linger.ms=20              # Wait up to 20ms for batch to fill

# Compression — Reduce network and storage overhead
compression.type=lz4      # Fastest compression; zstd for best ratio

# Buffer — More memory for batching
buffer.memory=67108864    # 64MB (default 32MB)

# Parallelism — More in-flight requests
max.in.flight.requests.per.connection=5  # (with idempotent enabled, max 5)

# Delivery — Trade durability for speed
acks=1                    # or acks=0 for fire-and-forget

# Retries — Let Kafka handle retries
retries=Integer.MAX_VALUE
enable.idempotence=true   # Prevent duplicates from retries
delivery.timeout.ms=120000 # Total time for delivery including retries
```

**Throughput by acks setting:**
```
acks=0:  ~300K records/sec
acks=1:  ~200K records/sec
acks=all: ~100K records/sec (varies by replication factor and ISR size)
```

**Compression comparison:**

| Algorithm | Compression Ratio | CPU Usage | Use Case |
|-----------|-------------------|-----------|----------|
| none | 1.0 | None | Network not bottleneck |
| gzip | 2.5-3x | High | Limited bandwidth, high storage cost |
| snappy | 1.5-2x | Low | Balanced throughput and compression |
| lz4 | 1.5-2x | Very Low | Maximum throughput with some compression |
| zstd | 2-2.5x | Medium | Best balance (Kafka 2.1+) |

---

### Q60: How do you tune a Kafka consumer for maximum throughput?

**Answer:**

```properties
# Fetch more data per request
fetch.min.bytes=1048576    # 1MB (default 1 byte) — Broker waits until 1MB ready
fetch.max.bytes=52428800   # 50MB (default 50MB) — Max data per fetch
max.partition.fetch.bytes=1048576  # 1MB per partition per fetch

# Process more records per poll
max.poll.records=1000      # (default 500)

# Allow more time for processing
max.poll.interval.ms=600000  # 10 minutes (default 5 min)

# Multiple consumers in group (limited by partitions)
# Ensure partition count >= desired consumer count
```

**Key tuning strategies:**

1. **Increase consumers** — Add more consumers up to the partition count
2. **Increase partitions** — If consumers are maxed out, increase partitions for more parallelism
3. **Batch processing** — Process records in micro-batches instead of one at a time
4. **Thread pool processing** — Use a thread pool for CPU-intensive processing:
```java
ExecutorService executor = Executors.newFixedThreadPool(8);
while (true) {
    ConsumerRecords<K, V> records = consumer.poll(Duration.ofMillis(100));
    List<Future<?>> futures = new ArrayList<>();
    for (ConsumerRecord<K, V> record : records) {
        futures.add(executor.submit(() -> process(record)));
    }
    for (Future<?> f : futures) f.get(); // Wait for all
    consumer.commitSync(); // Commit after all processed
}
```
**Caution:** With thread pool, you lose per-partition ordering guarantee.

5. **Use `pause()` and `resume()`** — When processing is slow, pause fetching to avoid building up lag, then resume when ready

---

### Q61: How do you tune the Kafka broker for better performance?

**Answer:**

### Network & I/O
```properties
# Increase network threads
num.network.threads=8        # (default 3) — Handle more connections

# Increase I/O threads
num.io.threads=16            # (default 8) — Handle more disk I/O

# Increase socket buffer sizes
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

# Increase fetch and produce request sizes
replica.fetch.max.bytes=1048576
replica.fetch.wait.max.ms=500
```

### Disk & Log
```properties
# Multiple data directories (JBOD)
log.dirs=/disk1/kafka-logs,/disk2/kafka-logs,/disk3/kafka-logs

# More recovery threads
num.recovery.threads.per.data.dir=4  # (default 1) — Faster startup/recovery

# Don't force flushes — Let OS handle it
log.flush.interval.messages=10000  # Set high or don't set
log.flush.interval.ms=1000         # Set high or don't set

# Larger segments
log.segment.bytes=1073741824  # 1GB (default)
```

### Replication
```properties
# Faster replica fetching
replica.fetch.min.bytes=1
replica.fetch.backoff.ms=100
num.replica.fetchers=4  # (default 1) — More threads for replication
```

### OS-Level Tuning
```bash
# File descriptors
ulimit -n 100000

# Page cache (don't swap)
vm.swappiness=1

# Dirty page ratio
vm.dirty_ratio=80
vm.dirty_background_ratio=5

# Network
net.core.rmem_max=16777216
net.core.wmem_max=16777216
```

---

### Q62: What is the impact of increasing partitions on performance?

**Answer:**

**Benefits:**
1. More parallelism — More consumers can consume concurrently
2. Higher throughput — Load distributed across more brokers
3. Better disk I/O — More segments being written/read in parallel

**Costs (the dark side of too many partitions):**

1. **File Handles** — Each partition has open file handles for .log, .index, .timeindex. With 10K partitions per broker, that's 30K+ open files. Can hit `ulimit -n`.

2. **Memory Overhead** — 
   - Each partition's index is memory-mapped (mmap)
   - Client metadata for each partition
   - Controller must track all partition states
   - Approximate cost: ~1MB per partition on the controller

3. **Leader Election Time** — When a broker fails, the controller must elect leaders for ALL partitions led by that broker. With 100K partitions, this can take minutes.

4. **Rebalance Time** — More partitions = more assignments = longer rebalance

5. **Throughput Degradation** — Random I/O increases as the OS must seek between many small writes

6. **ZooKeeper Limit** — In ZK mode, ~200K partitions is the practical limit due to ZK's latency

**Guidelines:**
```
Partitions per broker:
  - < 1,000: Comfortable
  - 1,000-2,000: Monitor closely
  - 2,000-4,000: Risky
  - > 4,000: Avoid (unless KRaft mode with powerful hardware)
```

**KRaft improvement:** KRaft mode supports millions of partitions because metadata is managed internally via the Raft log rather than through ZooKeeper.

---

## Section 13: Kafka Connect

### Q63: What is Kafka Connect? Explain its architecture.

**Answer:**

Kafka Connect is a framework for **scalable and reliable streaming of data between Kafka and other systems**. It provides a standardized way to:
- **Source Connector** — Import data from external systems into Kafka (e.g., JDBC, S3, MongoDB)
- **Sink Connector** — Export data from Kafka to external systems (e.g., Elasticsearch, S3, Snowflake)

**Architecture:**

```
┌──────────────────────────────────────────────────┐
│            Kafka Connect Cluster                  │
│  ┌──────────────┐  ┌──────────────┐             │
│  │  Worker 1     │  │  Worker 2     │             │
│  │  ┌─────────┐ │  │  ┌─────────┐ │             │
│  │  │Source C │ │  │  │Sink C   │ │             │
│  │  │(JDBC)   │ │  │  │(ES)     │ │             │
│  │  └─────────┘ │  │  └─────────┘ │             │
│  │  ┌─────────┐ │  │  ┌─────────┐ │             │
│  │  │Sink C   │ │  │  │Source C │ │             │
│  │  │(S3)     │ │  │  │(MongoDB)│ │             │
│  │  └─────────┘ │  │  └─────────┘ │             │
│  └──────────────┘  └──────────────┘             │
│         │                  │                     │
│    ┌────▼──────────────────▼──────┐              │
│    │  config, offset, status      │              │
│    │  topics (internal)           │              │
│    └─────────────────────────────┘              │
└──────────────────────────────────────────────────┘
```

**Key components:**

1. **Workers** — JVM processes running connectors and tasks. Two modes:
   - **Standalone** — Single worker, for testing/simple deployments
   - **Distributed** — Multiple workers, connectors/tasks distributed, automatic failover

2. **Connectors** — JAR plugins that define how to interact with the external system. Three types:
   - **Source Connector** — Reads from external system, produces to Kafka
   - **Sink Connector** — Reads from Kafka, writes to external system
   - **Transformation (SMT)** — Single Message Transform — modifies records in-flight

3. **Tasks** — The actual data processing units. A connector is split into tasks for parallelism. Tasks are distributed across workers.

4. **Internal Topics:**
   - `connect-configs` — Connector configurations
   - `connect-offsets` — Source connector offset tracking
   - `connect-status` — Connector and task status

**Important:** Connectors are just configuration + code. Tasks do the actual work. If a worker fails, its tasks are redistributed to surviving workers (automatic in distributed mode).

---

### Q64: What is Single Message Transform (SMT) in Kafka Connect?

**Answer:**

SMTs are lightweight transformations applied to each record as it flows through Kafka Connect. They allow you to modify records without writing custom code.

**Common SMTs:**

1. **InsertField** — Add a field with static value or record metadata
```json
"transforms": "addInsertTS",
"transforms.addInsertTS.type": "org.apache.kafka.connect.transforms.InsertField$Value",
"transforms.addInsertTS.static.field": "ingestion_timestamp",
"transforms.addInsertTS.static.value": "${now}"
```

2. **ReplaceField** — Include, exclude, or rename fields
```json
"transforms": "removePii",
"transforms.removePii.type": "org.apache.kafka.connect.transforms.ReplaceField$Value",
"transforms.removePii.exclude": "ssn,credit_card,password"
```

3. **MaskField** — Replace sensitive fields with masked values
```json
"transforms": "maskPii",
"transforms.maskPii.type": "org.apache.kafka.connect.transforms.MaskField$Value",
"transforms.maskPii.fields": "ssn",
"transforms.maskPii.replacement": "XXX-XX-XXXX"
```

4. **TimestampRouter** — Route records to topics based on timestamp
```json
"transforms": "route",
"transforms.route.type": "org.apache.kafka.connect.transforms.TimestampRouter",
"transforms.route.topic.format": "logs-${timestamp}",
"transforms.route.timestamp.format": "yyyyMMdd"
```

5. **Flatten** — Flatten nested structures
```json
"transforms": "flatten",
"transforms.flatten.type": "org.apache.kafka.connect.transforms.Flatten$Value",
"transforms.flatten.delimiter": "_"
```

6. **HoistField / ValueToKey** — Restructure records

**Chaining SMTs:**
```json
"transforms": "removePii,addMetadata,flatten",
"transforms.removePii.type": "...",
"transforms.addMetadata.type": "...",
"transforms.flatten.type": "..."
```

**When to use SMTs vs. Kafka Streams:**
- **SMTs:** Simple, single-record transformations (field filtering, renaming, masking)
- **Kafka Streams:** Complex transformations (joins, aggregations, windowing, multi-record processing)

---

### Q65: How does Kafka Connect handle exactly-once delivery for sink connectors?

**Answer:**

**Source Connectors:**
- Kafka Connect tracks source offsets in the `connect-offsets` topic
- On restart, the source connector resumes from the last committed offset
- This provides at-least-once delivery by default
- For exactly-once, the source system must support idempotent reads or the connector must be transactional

**Sink Connectors (Kafka 2.6+ with KIP-618):**
- Kafka Connect supports exactly-once delivery for sink connectors using the **consumer's transactional API**
- The sink task reads records, processes them, and commits both the external system write and the Kafka offset in a single transaction
- Configuration:
```json
"consumer.override.isolation.level": "read_committed",
"errors.tolerance": "all",
"exactly.once.support": "enabled"
```

**Challenges with exactly-once sinks:**
1. **External System Transaction Support** — The external system must support transactions (e.g., databases with JDBC, but not all systems)
2. **Performance** — Two-phase commit adds latency
3. **Partial Failure** — What if the external write succeeds but the offset commit fails?

**Practical approaches:**
1. **Idempotent writes** — Design the sink to be idempotent (upsert with unique key)
2. **Deduplication table** — Track processed offsets in the target system
3. **Exactly-once with transactions** — Use Kafka's transaction API when the sink supports it

---

## Section 14: Kafka Streams

### Q66: What is Kafka Streams? How is it different from Spark Streaming and Flink?

**Answer:**

Kafka Streams is a **client library** for building real-time stream processing applications with Kafka. It is NOT a processing framework — there's no cluster to manage.

**Comparison:**

| Aspect | Kafka Streams | Spark Streaming | Flink |
|--------|---------------|-----------------|-------|
| **Deployment** | Embedded in your app | Separate cluster | Separate cluster |
| **Processing Model** | Event-at-a-time (true streaming) | Micro-batching | Event-at-a-time |
| **State Management** | Built-in (RocksDB + changelog) | Limited (checkpointing) | Built-in (RocksDB + checkpointing) |
| **Exactly-Once** | Yes (transactions) | Yes (checkpointing) | Yes (checkpointing) |
| **Dependency** | Just the library | Spark cluster | Flink cluster |
| **Language** | Java/Scala only | Java, Scala, Python, R | Java, Scala, Python |
| **Windowing** | Event-time, processing-time | Event-time, processing-time | Event-time, processing-time |
| **Interactive Queries** | Yes (queryable state stores) | No | Limited |
| **Scaling** | Add more instances | Add more executors | Add more task managers |

**Key Kafka Streams concepts:**

1. **Topology** — A DAG (Directed Acyclic Graph) of processing nodes
2. **KStream** — A record stream (each record is an event/fact)
3. **KTable** — A changelog stream (each record is an update to a key's value)
4. **GlobalKTable** — A broadcast table available on all instances
5. **State Store** — Local storage for stateful operations (RocksDB by default)
6. **Changelog Topic** — Internal topic backing each state store for fault tolerance

**When to choose Kafka Streams:**
- Processing is Kafka-to-Kafka
- You want lightweight deployment (no cluster)
- You need interactive queries on state
- Your team is Java/Spring Boot focused

**When to choose Flink:**
- Complex event-time processing with late data
- Multi-source/multi-sink (not just Kafka)
- Need advanced windowing or CEP (Complex Event Processing)

---

### Q67: Explain KStream vs KTable vs GlobalKTable with examples.

**Answer:**

### KStream — Event Stream
- Each record is an independent event
- Analogy: A log of events (append-only)
- Operations produce new records for each input

```java
KStream<String, Order> orders = builder.stream("orders");
// Every order event flows through, including duplicates for same key
```

### KTable — Changelog Stream
- Each record is an update to a key's current value
- Analogy: A database table (latest value per key)
- Automatically compacts — only the latest value per key is visible

```java
KTable<String, Customer> customers = builder.table("customers");
// Only the latest customer profile per key is visible
// If a new event arrives for key "C1", old value is replaced
```

### GlobalKTable — Broadcast Changelog
- A copy of the entire table is available on every Kafka Streams instance
- Used for joining with KStream without co-partitioning requirement
- No repartitioning needed since all data is local

```java
GlobalKTable<String, Product> products = builder.globalTable("products");
// Every instance has ALL products — no need for co-partitioning
```

**KStream-KTable Join Example:**
```java
KStream<String, Order> orders = builder.stream("orders");
KTable<String, Customer> customers = builder.table("customers");

KStream<String, EnrichedOrder> enriched = orders.join(
    customers,
    (order, customer) -> new EnrichedOrder(order, customer)
);
```

**Co-partitioning requirement for KStream-KTable join:**
- Both must have the same number of partitions
- Both must be partitioned by the same key
- If not, you must repartition the KStream first

**When to use GlobalKTable instead of KTable:**
- The table is small (fits in memory on each instance)
- Co-partitioning is difficult or impossible
- You need to join on a different key than the partition key

---

### Q68: What is a state store in Kafka Streams? How does fault tolerance work?

**Answer:**

A **state store** is local storage used by stateful operations (aggregations, joins, windowing) in Kafka Streams.

**Types:**

1. **In-Memory State Store** — Fast but limited by memory; lost on restart
```java
StoreBuilder<KeyValueStore<String, Long>> store = Stores
    .keyValueStoreBuilder(Stores.inMemoryKeyValueStore("my-store"), 
                          Serdes.String(), Serdes.Long());
```

2. **Persistent State Store (RocksDB)** — Spills to disk; can handle larger state
```java
StoreBuilder<KeyValueStore<String, Long>> store = Stores
    .keyValueStoreBuilder(Stores.persistentKeyValueStore("my-store"),
                          Serdes.String(), Serdes.Long());
```

3. **Custom State Store** — Implement your own backing store

**Fault Tolerance via Changelog Topics:**

Every state store is backed by a **changelog topic** — an internal compacted Kafka topic that records every state change.

```
State Change Flow:
1. Streams task processes a record
2. State store is updated (e.g., increment counter)
3. Change is written to the changelog topic
4. Record is forwarded downstream

Recovery Flow:
1. Streams instance crashes
2. New instance assigned the same partitions
3. New instance reads the changelog topic from the beginning
4. Rebuilds the state store from changelog events
5. Resumes processing from the last committed offset
```

**Configuration:**
```java
// Enable/disable changelog (disable for in-memory only)
StoreBuilder<KeyValueStore<String, Long>> store = Stores
    .keyValueStoreBuilder(Stores.persistentKeyValueStore("my-store"),
                          Serdes.String(), Serdes.Long())
    .withLoggingEnabled()  // Default: changelog topic created
    .withCachingEnabled(); // Buffer writes for better throughput
```

**Standby tasks:** In a distributed Streams application, you can configure standby tasks that maintain a warm copy of another instance's state store. On failover, the standby takes over immediately without rebuilding from the changelog.

---

### Q69: How does windowing work in Kafka Streams?

**Answer:**

Windowing groups records by time for stateful operations like aggregations and joins.

**Window types:**

1. **Tumbling Window** — Fixed-size, non-overlapping windows
```
|----Window 1----|----Window 2----|----Window 3----|
0s              10s             20s             30s
```
```java
KStream<String, Event> stream = builder.stream("events");
stream.groupByKey()
      .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofSeconds(10)))
      .count()
      .toStream();
```

2. **Hopping Window** — Fixed-size, overlapping windows (slides by hop size)
```
|----Window 1----|
   |----Window 2----|
      |----Window 3----|
0s  5s            15s
    10s           20s
```
```java
.windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofSeconds(10))
                       .advanceBy(Duration.ofSeconds(5)))
```

3. **Sliding Window** — Window centered around each event; used for joins
```
   Event A    Event B
     |          |
  |--Window--|--Window--|
```
```java
stream1.join(stream2, 
    (v1, v2) -> v1 + v2,
    JoinWindows.ofTimeDifferenceWithNoGrace(Duration.ofSeconds(5)));
```

4. **Session Window** — Variable-size based on activity gaps
```
|---Session 1---|          |---Session 2---|
  [E1] [E2] [E3]  gap       [E4] [E5]
```
```java
.groupByKey()
.windowedBy(SessionWindows.ofInactivityGapWithNoGrace(Duration.ofMinutes(5)))
.count()
```

**Grace period:** Since Kafka 3.x, grace periods control how long to wait for late-arriving records before closing a window:
```java
TimeWindows.ofSizeAndGrace(Duration.ofSeconds(10), Duration.ofSeconds(5))
// Window stays open 5 seconds after its end time for late records
```

**Event time vs Processing time:**
- **Event time** — Timestamp in the record (recommended for accurate windowing)
- **Processing time** — Timestamp when the Streams API processes the record
- Kafka Streams uses record timestamps by default (event time)

---

## Section 15: Schema Registry & Avro/Protobuf

### Q70: What is Schema Registry? Why is it needed?

**Answer:**

**Schema Registry** is a separate service (from Confluent, open-source) that provides a centralized schema management layer for Kafka. It solves the problem of **schema evolution** in a distributed system.

**The Problem without Schema Registry:**
```
Producer sends: {"id": 1, "name": "Alice", "email": "alice@test.com"}
Consumer expects: {"id": 1, "name": "Alice"}
Producer updates to: {"id": 1, "name": "Alice", "phone": "555-1234"}
Consumer crashes: Doesn't know what "phone" is
```

**How Schema Registry solves this:**
1. Producers register schemas with the Schema Registry
2. Each Kafka message contains only a **schema ID** (4 bytes) instead of the full schema
3. Consumers fetch the schema from Schema Registry using the ID
4. Schema Registry enforces **compatibility rules** — backward, forward, full, none

**Flow:**
```
1. Producer → Schema Registry: Register schema
2. Schema Registry → Producer: Schema ID = 42
3. Producer → Kafka: [Schema ID: 42][Avro/Protobuf serialized data]
4. Consumer ← Kafka: [Schema ID: 42][data]
5. Consumer → Schema Registry: Get schema for ID 42
6. Schema Registry → Consumer: Schema
7. Consumer deserializes data using schema
```

**Compatibility types:**

| Type | Rule | Use Case |
|------|------|----------|
| **Backward** | New schema can read old data (add optional field with default) | Most common; consumers updated first |
| **Forward** | Old schema can read new data (remove field, old schema ignores new) | Producers updated first |
| **Full** | Both backward and forward | Strictest; most restrictive |
| **None** | No compatibility check | Development only |

**Example of backward-compatible change:**
```json
// Schema V1
{"type": "record", "name": "User", "fields": [
  {"name": "id", "type": "int"},
  {"name": "name", "type": "string"}
]}

// Schema V2 (backward compatible — new optional field with default)
{"type": "record", "name": "User", "fields": [
  {"name": "id", "type": "int"},
  {"name": "name", "type": "string"},
  {"name": "email", "type": "string", "default": ""}
]}
```

---

### Q71: Compare Avro, Protobuf, and JSON Schema for Kafka serialization.

**Answer:**

| Aspect | Avro | Protobuf | JSON Schema |
|--------|------|----------|-------------|
| **Binary Format** | Yes (compact) | Yes (compact + tag-based) | No (text-based JSON) |
| **Schema Evolution** | Excellent (backward/forward/full) | Good (with rules) | Moderate |
| **Code Generation** | Optional (can use GenericRecord) | Yes (protoc compiler) | No (dynamic validation) |
| **Default Values** | Supported | Partial | Supported |
| **Size** | Small (no field tags in payload) | Small (field tags in payload) | Large (field names in payload) |
| **Readability** | Not human-readable | Not human-readable | Human-readable |
| **Performance** | Fast | Faster | Slowest |
| **Schema Registry** | Confluent Schema Registry native | Confluent SR (since 5.x) | Confluent SR |
| **Language Support** | Java, Python, C++, etc. | Java, C++, Go, Python, etc. | Any (JSON is universal) |

**When to use each:**

- **Avro:** Best for Kafka-centric ecosystems. Rich schema evolution. Used by most Kafka Connect connectors. Good when you need runtime schema resolution without code generation.
  
- **Protobuf:** Best when you have polyglot services (Go, C++, Java, etc.). More performant than Avro for small messages. Tag-based encoding means you can add fields without breaking old readers.

- **JSON Schema:** Best for debugging, low-throughput scenarios, or when consumers need to read messages directly (e.g., browser-based consumers). Largest message size overhead.

**Spring Boot Kafka with Avro example:**
```java
// Producer
@Configuration
public class AvroProducerConfig {
    @Bean
    public ProducerFactory<String, User> producerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, KafkaAvroSerializer.class);
        props.put("schema.registry.url", "http://localhost:8081");
        return new DefaultKafkaProducerFactory<>(props);
    }
}

// Consumer
@Configuration
public class AvroConsumerConfig {
    @Bean
    public ConsumerFactory<String, User> consumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, KafkaAvroDeserializer.class);
        props.put("schema.registry.url", "http://localhost:8081");
        props.put("specific.avro.reader", true); // Use generated class
        return new DefaultKafkaConsumerFactory<>(props);
    }
}
```

---

## Section 16: Spring Boot + Kafka Integration

### Q72: How do you configure Kafka in Spring Boot 3.x?

**Answer:**

### Dependencies
```xml
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
    <version>3.2.0</version>
</dependency>
```

### Application Configuration
```yaml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
      acks: all
      retries: 3
      properties:
        enable.idempotence: true
        linger.ms: 10
        batch.size: 32768
    consumer:
      group-id: my-service-group
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      auto-offset-reset: earliest
      enable-auto-commit: false
      properties:
        spring.json.trusted.packages: "*"
        max.poll.records: 100
        max.poll.interval.ms: 300000
    listener:
      ack-mode: manual_immediate
      concurrency: 3
```

### Producer
```java
@Service
public class OrderProducer {
    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;

    public OrderProducer(KafkaTemplate<String, OrderEvent> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void sendOrder(OrderEvent order) {
        ProducerRecord<String, OrderEvent> record = new ProducerRecord<>(
            "orders", order.getOrderId(), order);
        
        kafkaTemplate.send(record).whenComplete((result, ex) -> {
            if (ex != null) {
                log.error("Failed to send order: {}", order.getOrderId(), ex);
                // Handle failure: retry, DLQ, etc.
            } else {
                RecordMetadata metadata = result.getRecordMetadata();
                log.info("Order sent: topic={}, partition={}, offset={}",
                    metadata.topic(), metadata.partition(), metadata.offset());
            }
        });
    }
}
```

### Consumer
```java
@Component
@Slf4j
public class OrderConsumer {

    @KafkaListener(
        topics = "orders",
        groupId = "order-processing-group",
        containerFactory = "kafkaListenerContainerFactory"
    )
    public void processOrder(
            ConsumerRecord<String, OrderEvent> record,
            Acknowledgment acknowledgment) {
        try {
            OrderEvent order = record.value();
            log.info("Processing order: {} from partition {} offset {}",
                order.getOrderId(), record.partition(), record.offset());
            
            // Business logic
            processOrder(order);
            
            // Manual commit after successful processing
            acknowledgment.acknowledge();
        } catch (Exception e) {
            log.error("Failed to process order at offset {}", record.offset(), e);
            // Don't acknowledge — message will be redelivered
            // Or send to DLQ
        }
    }
}
```

---

### Q73: How do you implement error handling and DLQ in Spring Kafka?

**Answer:**

Spring Kafka provides sophisticated error handling through `DefaultErrorHandler` (Spring Kafka 3.x, replaces `SeekToCurrentErrorHandler`).

### Configuration
```java
@Configuration
public class KafkaErrorHandlerConfig {

    @Bean
    public DefaultErrorHandler errorHandler(KafkaTemplate<String, Object> kafkaTemplate) {
        // Retry up to 3 times with exponential backoff
        FixedBackOff backOff = new FixedBackOff(1000L, 3); // 1s delay, 3 retries
        
        // Or exponential backoff
        // ExponentialBackOffWithMaxRetries backOff = new ExponentialBackOffWithMaxRetries(5);
        // backOff.setInitialInterval(1000L);
        // backOff.setMultiplier(2.0);
        // backOff.setMaxInterval(30000L);

        DefaultErrorHandler errorHandler = new DefaultErrorHandler(
            new DeadLetterPublishingRecoverer(kafkaTemplate), backOff
        );

        // Don't retry for these exceptions
        errorHandler.addNotRetryableExceptions(
            DeserializationException.class,
            JsonProcessingException.class,
            IllegalArgumentException.class
        );

        return errorHandler;
    }
}
```

### DLQ (Dead Letter Queue) Configuration
```java
@Bean
public DeadLetterPublishingRecoverer dlqRecoverer(KafkaTemplate<String, Object> template) {
    return new DeadLetterPublishingRecoverer(template,
        (consumerRecord, exception) -> {
            // Route to topic.DLT by default, or customize:
            return new TopicPartition(
                consumerRecord.topic() + ".DLT",
                consumerRecord.partition()
            );
        });
}
```

### Consumer with Error Handler
```java
@KafkaListener(
    topics = "orders",
    groupId = "order-service",
    errorHandler = "errorHandler"
)
public void consume(ConsumerRecord<String, OrderEvent> record) {
    // If this throws, error handler retries then sends to DLQ
    processOrder(record.value());
}
```

### DLQ Consumer (for investigation)
```java
@KafkaListener(topics = "orders.DLT", groupId = "dlt-monitor")
public void consumeDLT(ConsumerRecord<String, byte[]> record,
                       @Header(KafkaHeaders.EXCEPTION_MESSAGE) String errorMsg,
                       @Header(KafkaHeaders.ORIGINAL_TOPIC) String originalTopic) {
    log.error("DLT Message from topic {}: error={}", originalTopic, errorMsg);
    // Alert, manual review, or reprocess
}
```

**Key headers added by Spring Kafka to DLQ messages:**
- `kafka_original-topic` — Original topic
- `kafka_original-partition` — Original partition
- `kafka_original-offset` — Original offset
- `kafka_exception-message` — Error message
- `kafka_exception-fqcn` — Exception class name

---

### Q74: How do you implement Kafka transactions in Spring Boot?

**Answer:**

### Producer Configuration
```java
@Configuration
public class TransactionalProducerConfig {

    @Bean
    public ProducerFactory<String, OrderEvent> producerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class);
        props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "order-service-txn-1");
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        return new DefaultKafkaProducerFactory<>(props);
    }

    @Bean
    public KafkaTransactionManager<String, OrderEvent> transactionManager(
            ProducerFactory<String, OrderEvent> producerFactory) {
        return new KafkaTransactionManager<>(producerFactory);
    }

    @Bean
    public KafkaTemplate<String, OrderEvent> kafkaTemplate() {
        return new KafkaTemplate<>(producerFactory());
    }
}
```

### Transactional Producer
```java
@Service
public class TransactionalOrderService {

    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;

    public TransactionalOrderService(KafkaTemplate<String, OrderEvent> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    // Declarative transaction
    @Transactional
    public void processAndPublish(OrderRequest request) {
        // Database write (part of same transaction if using ChainedTransactionManager)
        OrderEntity entity = orderRepository.save(toEntity(request));

        // Kafka publish (part of Kafka transaction)
        kafkaTemplate.executeInTransaction(kt -> {
            kt.send("orders", entity.getId(), toEvent(entity));
            kt.send("order-audit", entity.getId(), toAuditEvent(entity));
            return true;
        });
    }
}
```

### Chained Transaction Manager (Kafka + Database)
```java
@Bean
public ChainedTransactionManager chainedTransactionManager(
        DataSourceTransactionManager dbTransactionManager,
        KafkaTransactionManager<String, OrderEvent> kafkaTransactionManager) {
    return new ChainedTransactionManager(kafkaTransactionManager, dbTransactionManager);
}
```

**Important note:** `ChainedTransactionManager` provides best-effort 1PC (one-phase commit), not true 2PC. If the DB commit succeeds but the Kafka commit fails, there can be inconsistency. For true exactly-once across DB and Kafka, use the **Outbox Pattern** or **Transactional Outbox with Debezium CDC**.

### Consumer Configuration (Read Committed)
```yaml
spring:
  kafka:
    consumer:
      properties:
        isolation.level: read_committed
```

---

### Q75: How do you use Spring Kafka's ConcurrentKafkaListenerContainerFactory?

**Answer:**

```java
@Configuration
@EnableKafka
public class KafkaConsumerConfig {

    @Bean
    public ConsumerFactory<String, OrderEvent> consumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, 
                  JsonDeserializer.class);
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-service");
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        props.put(JsonDeserializer.TRUSTED_PACKAGES, "*");
        props.put(JsonDeserializer.VALUE_DEFAULT_TYPE, 
                  "com.example.OrderEvent");
        return new DefaultKafkaConsumerFactory<>(props);
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> 
            kafkaListenerContainerFactory() {
        ConcurrentKafkaListenerContainerFactory<String, OrderEvent> factory =
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory());
        
        // Concurrency = number of threads (should be <= number of partitions)
        factory.setConcurrency(3);
        
        // Manual acknowledgment mode
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL_IMMEDIATE);
        
        // Error handler
        factory.setCommonErrorHandler(errorHandler());
        
        // Batch listener (for processing batches)
        // factory.setBatchListener(true);
        // factory.getContainerProperties().setAckMode(
        //     ContainerProperties.AckMode.BATCH);
        
        return factory;
    }
}
```

**`concurrency` explained:**
- Creates N `KafkaMessageListenerContainer` instances
- Each container is a separate consumer thread
- If topic has 6 partitions and concurrency=3, each thread gets 2 partitions
- If concurrency > partitions, some threads will be idle
- Each thread has its own `KafkaConsumer` instance

---

## Section 17: Kafka in Microservices Architecture

### Q76: How do you implement event-driven communication between microservices using Kafka?

**Answer:**

**Event-driven architecture (EDA)** with Kafka replaces synchronous REST/gRPC calls with asynchronous event propagation.

**Patterns:**

### 1. Event Notification
```java
// Order Service publishes event
orderCreatedEvent = new OrderCreatedEvent(orderId, items, total);
kafkaTemplate.send("order-events", orderId, orderCreatedEvent);

// Inventory Service consumes and reacts
@KafkaListener(topics = "order-events")
public void handleOrderCreated(OrderCreatedEvent event) {
    inventoryService.reserveStock(event.getItems());
}
```

### 2. Event-Carried State Transfer
```java
// Event contains all needed data — no callback needed
CustomerUpdatedEvent event = new CustomerUpdatedEvent(
    customer.getId(), customer.getName(), customer.getEmail(), 
    customer.getAddress() /* full address object */
);
kafkaTemplate.send("customer-events", customer.getId(), event);

// Shipping Service doesn't need to call Customer Service
@KafkaListener(topics = "customer-events")
public void handleCustomerUpdate(CustomerUpdatedEvent event) {
    // Has all data locally — no synchronous call
    shippingService.updateCustomerCache(event);
}
```

### 3. CQRS (Command Query Responsibility Segregation)
```
Write Side:                    Read Side:
Commands → Service A → Kafka → Projection Service → Read DB
                                (builds materialized view)

Query Side:
Client → Read API → Read DB (optimized for queries)
```

### 4. Saga Pattern (Choreography)
```
Order Service → OrderCreated event → 
  Inventory Service → StockReserved event →
    Payment Service → PaymentCompleted event →
      Shipping Service → OrderShipped event →
        Order Service (order complete)
```

Each service publishes events and reacts to other services' events. No central orchestrator.

**Benefits:**
- Loose coupling — services don't need to know about each other
- Resilience — if a service is down, events queue up in Kafka
- Scalability — add new consumers without changing producers
- Audit trail — Kafka retains the complete event history

**Challenges:**
- Eventual consistency — not suitable for real-time consistency needs
- Debugging — distributed flow is harder to trace
- Ordering — no guaranteed ordering across services
- Duplicate handling — consumers must be idempotent

---

### Q77: What is the Outbox Pattern? Why do you need it with Kafka?

**Answer:**

**The Dual-Write Problem:**
```java
// This is dangerous!
public void createOrder(Order order) {
    orderRepository.save(order);          // DB write
    kafkaTemplate.send("orders", order);  // Kafka write
    // What if DB succeeds but Kafka fails? Inconsistency!
    // What if DB fails but Kafka succeeds? Inconsistency!
}
```

The Outbox Pattern solves this by using the database as the source of truth and CDC (Change Data Capture) to publish to Kafka.

**Pattern:**
```
1. Write to business table AND outbox table in same DB transaction
2. CDC tool (Debezium) captures outbox table changes
3. CDC publishes to Kafka
4. Kafka consumers process the event
```

**Implementation:**
```java
@Transactional
public void createOrder(Order order) {
    // 1. Save business data
    orderRepository.save(order);
    
    // 2. Save to outbox table (same transaction!)
    OutboxEvent event = OutboxEvent.builder()
        .aggregateId(order.getId())
        .aggregateType("Order")
        .eventType("OrderCreated")
        .payload(objectMapper.writeValueAsString(order))
        .build();
    outboxRepository.save(event);
    // No Kafka write here!
}

// Debezium captures outbox table inserts and publishes to Kafka
// Debezium connector configuration maps outbox events to Kafka topics
```

**Outbox Table Schema:**
```sql
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY,
    aggregate_type VARCHAR(100),
    aggregate_id VARCHAR(100),
    event_type VARCHAR(100),
    payload JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE
);
```

**Debezium Configuration:**
```json
{
  "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
  "database.hostname": "postgres",
  "database.dbname": "orderdb",
  "table.include.list": "public.outbox_events",
  "topic.prefix": "outbox",
  "transforms": "outbox",
  "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter",
  "transforms.outbox.route.by.field": "aggregate_type",
  "transforms.outbox.field.event.key": "aggregate_id",
  "transforms.outbox.field.event.type": "event_type",
  "transforms.outbox.field.payload": "payload"
}
```

**Benefits:**
- Atomic DB write + event publish (same transaction)
- No dual-write inconsistency
- Events are never lost (durable in DB before publishing)
- Natural event ordering per aggregate
- Easy replay by re-reading outbox table

---

### Q78: How do you implement saga pattern with Kafka?

**Answer:**

### Choreography-Based Saga
Each service publishes events and reacts to other events. No central coordinator.

```
Order Saga: Place Order → Reserve Stock → Charge Payment → Ship Order

Success Path:
Order Service --OrderCreated--> Inventory Service
Inventory Service --StockReserved--> Payment Service  
Payment Service --PaymentCompleted--> Shipping Service
Shipping Service --OrderShipped--> Order Service

Compensation Path (Payment Failed):
Payment Service --PaymentFailed--> Inventory Service
Inventory Service --StockReleased--> Order Service
Order Service --OrderCancelled--> Notification Service
```

```java
// Order Service
@KafkaListener(topics = "payment-events")
public void handlePaymentEvent(PaymentEvent event) {
    if (event.getType() == PaymentEvent.Type.COMPLETED) {
        orderService.confirmOrder(event.getOrderId());
    } else if (event.getType() == PaymentEvent.Type.FAILED) {
        orderService.cancelOrder(event.getOrderId());
        kafkaTemplate.send("order-events", event.getOrderId(),
            new OrderCancelledEvent(event.getOrderId(), "Payment failed"));
    }
}

// Inventory Service
@KafkaListener(topics = "order-events")
public void handleOrderEvent(OrderEvent event) {
    if (event.getType() == OrderEvent.Type.CREATED) {
        inventoryService.reserveStock(event.getOrderId(), event.getItems());
        kafkaTemplate.send("inventory-events", event.getOrderId(),
            new StockReservedEvent(event.getOrderId()));
    } else if (event.getType() == OrderEvent.Type.CANCELLED) {
        inventoryService.releaseStock(event.getOrderId());
        kafkaTemplate.send("inventory-events", event.getOrderId(),
            new StockReleasedEvent(event.getOrderId()));
    }
}
```

### Orchestration-Based Saga
A central orchestrator (Saga Orchestrator) manages the flow.

```java
@Service
public class OrderSagaOrchestrator {
    
    public void executeOrderSaga(Order order) {
        SagaDefinition saga = SagaDefinition.builder()
            .step()
                .invokeParticipant("inventory", "reserve", order)
                .onReply("FAILED", compensate("inventory", "release", order))
            .step()
                .invokeParticipant("payment", "charge", order)
                .onReply("FAILED", compensate("inventory", "release", order))
            .step()
                .invokeParticipant("shipping", "ship", order)
            .build();
        
        sagaExecutor.execute(saga);
    }
}
```

**Choreography vs Orchestration:**

| Aspect | Choreography | Orchestration |
|--------|--------------|---------------|
| Coupling | Loose | Tighter (orchestrator knows all) |
| Complexity | Grows with saga steps | Centralized, easier to understand |
| Debugging | Hard (distributed) | Easier (central log) |
| Single Point of Failure | No | Yes (orchestrator) |
| Best for | Simple sagas (2-4 steps) | Complex sagas (5+ steps) |

---

## Section 18: Exactly-Once Semantics & Transactions

### Q79: Explain Kafka's exactly-once semantics (EOS) implementation in detail.

**Answer:**

Kafka's EOS is the strongest delivery guarantee, ensuring that each record is processed exactly once even in the face of failures.

**Three pillars of EOS:**

### 1. Idempotent Producer
- Prevents duplicate writes during retries
- Each producer gets a PID (Producer ID) + sequence numbers per topic-partition
- Broker rejects duplicates (same PID + sequence number)
- Only works within a single producer session

### 2. Transactions
- Allows atomic writes across multiple partitions
- Consumer can