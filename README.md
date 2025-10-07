---
license: mit
application_name: dots_ocr
pipeline_tag: image-text-to-text
tags:
- image-to-text
- ocr
- document-parse
- layout
- table
- formula
language:
- en
- zh
- multilingual
---


# Run Dots.OCR locally with MacOS or Small GPU

**dots.ocr** is a powerful, multilingual document parser that unifies layout detection and content recognition within a single vision-language model while maintaining good reading order. The offical announced it's using 1.7B LLM foundation, that give us hope
to run it locally. However, in MacOS system, Pytorch transformers library lacks flash-attention implementation. And vllm and sglang 
both don't support MacOS. And there's another hidden detail in this model, that is its NaViT architecure vision encoder has another 1.2B parameters and consuming VRAM amount grows exponentially with the size of the input image. Even with vllm in CUDA device, it's
reported to requires at least 8GB VRAM to run.

**Dots.OCR.Runner** is created to solve these problems. Leveraged with llama.cpp's efficient attention implemention and other related operators, the peak RAM consumption in MacOS can be under 3GB. The speed is also comparable to CUDA device. It may be a little slower, because the trick is actually trading space with time. But the high quality performance and privacy assurance make the cost worthwhile.
