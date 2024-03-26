from doccano_transformer.datasets import NERDataset
from doccano_transformer.utils import read_jsonl
from curses.ascii import SP

dataset = read_jsonl(filepath='/Users/srinivas/Downloads/admin.jsonl', dataset=NERDataset, encoding='utf-8')
conll = dataset.to_conll2003(tokenizer=str.split)
sp = dataset.to_spacy(tokenizer=str.split)

print (conll)