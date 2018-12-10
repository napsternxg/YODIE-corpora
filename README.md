# YODIE data processor

## Getting the data
Source: https://gate.ac.uk/applications/yodie.html

Gorrell, Genevieve, Johann Petrak, and Kalina Bontcheva. "Using @Twitter Conventions to Improve #LOD-based Named Entity Disambiguation." In The Semantic Web. Latest Advances and New Domains, pp. 171-186. Springer International Publishing, 2015.

```bash

bash download.sh
```

## Converting FastInfoset format to GATE XML

The GATE XML files in data folder are created using GATE with Format FastInfo plugin. 
* Create a new corpus by right clicking on Language Resources
* Load the files in the corpus by right clickin on corpus and selecting populate and then selecting the directory of finf files
* Right click on corpus as click Save As ... > Gate XML. It should create a folder with all the Gate XML files. 


Save the exported gate XML files in `data/training_gate` and `data/testing_gate`


## Converting GATE XML to conll format

Run the following code to convert it into a conllU kind of format

```bash
for file_prefix in "training" "testing"; do
  python create_conll.py \
  --input-dir data/${file_prefix}_gate \
  --output-file data/${file_prefix}.conll \
  --output-format conll;
done
```

This will create conllu style files in data folder. 

The conllU format is as follows:

* Lines starting with # are comments and denote input file and full text of the data. `requires --add-comments-idx`
* Text is tokenized using `nltk.tokenize.casual.TweetTokenizer()`. `requires --add-comments-idx`
* Columns are as follows:
  - Token index. `requires --add-comments-idx`
  - Token text
  - start index of the annotated span (NOT TOKEN START INDEX). `requires --add-comments-idx`
  - end index of the annotated span (NOT TOKEN END INDEX). `requires --add-comments-idx`
  - BIO style named entity tags. The tag is `{boundary}-{class}.{subclass}`. Subclass only present for few cases. 
  - Named entity disambiguation tags. Link to DBpedia if first token in span, all following tokens of span are annotated as `PREV`. `NIL` is for non-disambiguated entities. `requires --add-comments-idx`

## Citation and License

YODIE data is distributed under http://creativecommons.org/licenses/by-nc-sa/4.0/

If using please cite the original paper: 

> Gorrell, Genevieve, Johann Petrak, and Kalina Bontcheva. "Using @Twitter Conventions to Improve #LOD-based Named Entity Disambiguation." In The Semantic Web. Latest Advances and New Domains, pp. 171-186. Springer International Publishing, 2015.

## Help

```
usage: create_conll.py [-h] [--input-dir INPUT_DIR]
                       [--output-file OUTPUT_FILE]
                       [--output-format {json,conll}] [--add-comments-idx]

optional arguments:
  -h, --help            show this help message and exit
  --input-dir INPUT_DIR
                        input directory
  --output-file OUTPUT_FILE
                        output file for conll format
  --output-format {json,conll}
                        output file for conll format
  --add-comments-idx    Pass to include original text as comment and index of
                        each token
```
