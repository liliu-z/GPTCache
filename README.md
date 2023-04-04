# GPT Cache

[![CI](https://github.com/zilliztech/gptcache/actions/workflows/CI_main.yaml/badge.svg)](https://github.com/zilliztech/gptcache/actions/workflows/CI_main.yaml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Discord](https://dcbadge.vercel.app/api/server/Q8C6WEjSWV?compact=true&style=flat)](https://discord.gg/Q8C6WEjSWV)

## 🤠 What is GPT Cache?

Large Language Models (LLMs) are a promising and transformative technology that has rapidly advanced in recent years. These models are capable of generating natural language text and have numerous applications, including chatbots, language translation, and creative writing. However, as the size of these models increases, so do the costs and performance requirements needed to utilize them effectively. This has led to significant challenges in developing on top of large models such as ChatGPT.

To address this issue, we have developed GPT Cache, a project that focuses on caching responses from language models, also known as a semantic cache. The system offers two major benefits:

1. Quick response to user requests: the caching system provides faster response times compared to large model inference, resulting in lower latency and faster response to user requests.
2. Reduced service costs: most LLM services are currently charged based on the number of tokens. If user requests hit the cache, it can reduce the number of requests and lower service costs.

## 🤔 Why would GPT Cache be helpful?

A good analogy for GptCache is to think of it as a more semantic version of Redis. In GptCache, hits are not limited to exact matches, but rather also include prompts and context similar to previous queries. We believe that the traditional cache design still works for AIGC applications for the following reasons:

- Locality is present everywhere. Like traditional application systems, AIGC applications also face similar hot topics. For instance, ChatGPT itself may be a popular topic among programmers.
- For purpose-built SaaS services, users tend to ask questions within a specific domain, with both temporal and spatial locality.
- By utilizing vector similarity search, it is possible to find a similarity relationship between questions and answers at a relatively low cost.

We provide [benchmarks](https://github.com/zilliztech/gpt-cache/blob/main/examples/benchmark/benchmark_sqlite_faiss_towhee.py) to illustrate the concept. In semantic caching, there are three key measurement dimensions: false positives, false negatives, and hit latency. With the plugin-style implementation, users can easily tradeoff these three measurements according to their needs.

## 😊 Quick Start

**Note**:

- You can quickly try GPT cache and put it into a production environment without heavy development. However, please note that the repository is still under heavy development.
- By default, only a limited number of libraries are installed to support the basic cache functionalities. When you need to use additional features, the related libraries will be **automatically installed**.
- Make sure that the Python version is 3.8.1 or higher.
- If you encounter issues installing a library due to a low pip version, run: `python -m pip install --upgrade pip`.

### pip install

```bash
pip install gptcache
```

### dev install

```bash
# clone gpt cache repo
git clone https://github.com/zilliztech/GPTCache.git
cd GPTCache

# install the repo
pip install -r requirements.txt
python setup.py install
```

### example usage

If you just want to achieve precise matching cache of requests, that is, two identical requests, you **ONLY** need **TWO** steps to access this cache

1. Cache init

```python
from gptcache.core import cache

cache.init()
# If you use the `openai.api_key = xxx` to set the api key, you need use `cache.set_openai_key()` to replace it.
# it will read the `OPENAI_API_KEY` environment variable and set it to ensure the security of the key.
cache.set_openai_key()
```

2. Replace the original openai package

```python
from gptcache.adapter import openai

# openai requests DON'T need ANY changes
answer = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "foo"}
    ],
)
```

If you want to experience vector similarity search cache locally, you can use the example [Sqlite + Faiss + Towhee](examples/sqlite_faiss_towhee/sqlite_faiss_towhee.py).

More Docs：

- [System Design, how it was constructed](docs/system.md)
- [Features, all features currently supported by the cache](docs/feature.md)
- [Examples, learn better custom caching](examples/example.md)

## 🤗 Modules

![GPTCache Struct](docs/GPTCacheStructure.png)

- **LLM Adapter**: 
The LLM Adapter is designed to integrate different LLM models by unifying their APIs and request protocols. GPTCache offers a standardized interface for this purpose, with current support for ChatGPT integration.
  - [x] Support OpenAI chatGPT API.
  - [ ] Support other LLMs, such as Hugging Face Hub, Bard, Anthropic, and self-hosted models like LLaMa.
- **Embedding Extractor**: 
This module is created to extract embeddings from requests for similarity search. GPTCache offers a generic interface that supports multiple embedding APIs, and presents a range of solutions to choose from. 
  - [x] Disable embedding. This will turn GPTCache into a keyword-matching cache.
  - [x] Support OpenAI embedding API.
  - [x] Support [Towhee](https://towhee.io/) with the paraphrase-albert-small-v2 model.
  - [ ] Support [Hugging Face](https://huggingface.co/) embedding API.
  - [ ] Support [Cohere](https://docs.cohere.ai/reference/embed) embedding API.
  - [ ] Support [fastText](https://fasttext.cc) embedding API.
  - [ ] Support [SentenceTransformers](https://www.sbert.net) embedding API.
- **Cache Storage**:
**Cache Storage** is where the response from LLMs, such as ChatGPT, is stored. Cached responses are retrieved to assist in evaluating similarity and are returned to the requester if there is a good semantic match. At present, GPTCache supports SQLite and offers a universally accessible interface for extension of this module.
  - [x] Support [SQLite](https://sqlite.org/docs.html).
  - [ ] Support [PostgreSQL](https://www.postgresql.org/).
  - [ ] Support [MySQL](https://www.mysql.com/).
  - [ ] Support [MongoDB](https://www.mongodb.com/).
  - [ ] Support [MariaDB](https://mariadb.org/).
  - [ ] Support [SQL Server](https://www.microsoft.com/en-us/sql-server/).
  - [ ] Support [Oracle](https://www.oracle.com/).
  - [ ] Support [Redis](https://redis.io/).
  - [ ] Support [Minio](https://min.io/).
  - [ ] Support [Habse](https://hbase.apache.org//).
  - [ ] Support [ElasticSearch](https://www.elastic.co/)
  - [ ] Support [zincsearch](https://zinc.dev/)
  - [ ] Support other storages
- **Vector Store**:
The **Vector Store** module helps find the K most similar requests from the input request's extracted embedding. The results can help assess similarity. GPTCache provides a user-friendly interface that supports various vector stores, including Milvus, Zilliz Cloud, and FAISS. More options will be available in the future.
  - [x] Support [Milvus](https://milvus.io/).
  - [x] Support [Zilliz Cloud](https://cloud.zilliz.com/).
  - [x] Support [FAISS](https://faiss.ai/).
  - [ ] Support [Qdrant](https://qdrant.tech/)
  - [ ] Support [Chroma](https://www.trychroma.com/)
  - [ ] Support [PGVector](https://github.com/pgvector/pgvector)
  - [ ] Support other vector databases
- **Cache Manager**:
The **Cache Manager** is responsible for controlling the operation of both the **Cache Storage** and **Vector Store**.
  - **Eviction Policy**:
  Currently, GPTCache makes decisions about evictions based solely on the number of lines. This approach can result in inaccurate resource evaluation and may cause out-of-memory (OOM) errors. We are actively investigating and developing a more sophisticated strategy.
    - [x] LRU eviction policy
    - [x] FIFO eviction policy
    - [ ] More complicated eviction policies
- **Similarity Evaluator**: 
This module collects data from both the **Cache Storage** and **Vector Store**, and uses various strategies to determine the similarity between the input request and the requests from the **Vector Store**. Based on this similarity, it determines whether a request matches the cache. GPTCache provides a standardized interface for integrating various strategies, along with a collection of implementations to use. The following similarity definitions are currently supported or will be supported in the future:
  - [x] The distance we obtain from the **Vector Store**.
  - [x] A model-based similarity determined using the albert_duplicate model from [Towhee](https://towhee.io/).
  - [x] Exact matches between the input request and the requests obtained from the **Vector Store**.
  - [x] Distance represented by applying linalg.norm from numpy to the embeddings.
  - [ ] BM25 and other similarity measurements
  - [ ] Support other models
 
  
  **Note**:Not all combinations of different modules may be compatible with each other. For instance, if we disable the **Embedding Extractor**, the **Vector Store** may not function as intended. We are currently working on implementing a combination sanity check for **GPTCache**.

## 😆 Contributing

Would you like to contribute to the development of GPT Cache? Take a look at [our contribution guidelines](docs/contributing.md).
