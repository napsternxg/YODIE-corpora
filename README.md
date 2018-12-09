Source: https://gate.ac.uk/applications/yodie.html

Gorrell, Genevieve, Johann Petrak, and Kalina Bontcheva. "Using @Twitter Conventions to Improve #LOD-based Named Entity Disambiguation." In The Semantic Web. Latest Advances and New Domains, pp. 171-186. Springer International Publishing, 2015.


The GATE XML files in data folder are created using GATE with Format FastInfo plugin. 
* Create a new corpus by right clicking on Language Resources
* Load the files in the corpus by right clickin on corpus and selecting populate and then selecting the directory of finf files
* Right click on corpus as click Save As ... > Gate XML. It should create a folder with all the Gate XML files. 


Save the exported gate XML files in `data/training_gate` and `data/testing_gate`

Run the following code to convert it into a conllU kind of format

```bash
for file_prefix in "training" "testing"; do
  python create_conll.py \
  --input-dir data/${file_prefix}_gate \
  --output-file data/${file_prefix}.conllu \
  --output-format conll;
done
```

This will create conllu style files in data folder. 

The conllU format is as follows:

* Lines starting with # are comments and denote input file and full text of the data
* Text is tokenized using `nltk.tokenize.casual.TweetTokenizer()`
* Columns are as follows:
  - Token index
  - Token text
  - start index of the annotated span (NOT TOKEN START INDEX)
  - end index of the annotated span (NOT TOKEN END INDEX)
  - BIO style named entity tags. The tag is `{boundary}-{class}.{subclass}`. Subclass only present for few cases. 
  - Named entity disambiguation tags. Link to DBpedia if first token in span, all following tokens of span are annotated as `PREV`. `NIL` is for non-disambiguated entities. 

YODIE data is distributed under http://creativecommons.org/licenses/by-nc-sa/4.0/

If using please cite the original paper: 
```
Gorrell, Genevieve, Johann Petrak, and Kalina Bontcheva. "Using @Twitter Conventions to Improve #LOD-based Named Entity Disambiguation." In The Semantic Web. Latest Advances and New Domains, pp. 171-186. Springer International Publishing, 2015.
```
