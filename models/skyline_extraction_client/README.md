# Exported
Exported from https://gitlab.com/wds-co/SnowWatch-SODALITE/blob/master/SkylineExtraction-training/peaklens-optimized-training.ipynb
with:

```
export = exporter.Exporter(tf.train.Saver())
export.init(named_graph_signatures={
    "inputs": exporter.generic_signature({"input": x}),
    "outputs": exporter.generic_signature({"output": softmax})
})
export.export('./export/', tf.constant(123), sess)
```