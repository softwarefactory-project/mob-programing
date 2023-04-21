LLM survey
==========

# Taxonomy

LLM : Large Language Model
GPT : Generative Pre-Trained Transformer
Transformer : It is a machine learning model introduced in 2017
Parameter: Neuron weight?

Formula to convert parameters count to disk size:

modelSize = λ params: params * 1e9 * 32  / (8 * 1024 * 1024 * 1024)
                                     ^- assuming 32bits float

For example, a 7B module is:

>>> modelSize(7)
 26 # GiB
>>> modelSize(175)
651 # GiB


# Models

- GPT-3      (175B)
- PaLM       (540B)
- Chinchilla ( 70B)
- LLaMa      (  7B up to 65B)


# Training data

- C4        (783 GiB)
- GitHub    (328 GiB)
- Wikipedia ( 83 GiB)


# Evaluation dataset

- BoolQ:

  Is Berlin the smallest city of Germany?

    Yes
    No

- HellaSwag:

  A woman is outside with a bucket and a dog. The dog is running around trying to avoid a bath. She

    a) rinses the bucket off with soap and blow dries the dog's head.
    b) uses a hose to keep it from getting soapy.
    c) gets the dog wet, then it runs away again.
    d) gets into the bath tub with the dog.

- BigBench: https://github.com/google/big-bench


# Reference papers

- Attention is All you need: https://arxiv.org/abs/1706.03762
- https://research.facebook.com/file/1574548786327032/LLaMA--Open-and-Efficient-Foundation-Language-Models.pdf
- Spark Of AGI: https://arxiv.org/pdf/2303.12712
