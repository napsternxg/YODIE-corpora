# coding: utf-8

from bs4 import BeautifulSoup
import json
from tqdm import tqdm
from glob import glob
from nltk.tokenize.casual import TweetTokenizer

tokenizer = TweetTokenizer()

def get_annotation_sets(soup):
    return [
            annotationset
            for annotationset in soup.find_all("annotationset")
            if annotationset.attrs.get("name")
            ]

def annotation2dict(annotation):
    data = {}
    data.update(annotation.attrs)
    data["features"] = {}
    for feature in annotation.find_all("feature"):
        name = feature.find("name").text
        value = feature.find("value").text
        data["features"][name] = value
    return data
    
def get_token_info(annotationset):
    tokens = []
    chunks = []
    start_mapping = {}
    end_mapping = {}
    for v in annotationset.find_all("annotation"):
        a = annotation2dict(v)
        if a["type"] == "Token" and a["features"]["length"] != "0":
            start_mapping[a["startnode"]] = len(tokens)
            end_mapping[a["endnode"]] = len(tokens)
            tokens.append(a)
        if "kind" in a["features"] and a["features"]["kind"] == "chunk":
            chunks.append(a)
    return tokens, chunks, start_mapping, end_mapping

def process_chunks(tokens, chunks, start_mapping, end_mapping):
    tags = ["O"]*len(tokens)
    for chunk in chunks:
        label = chunk["type"]
        start_idx = start_mapping[chunk["startnode"]]
        end_idx = end_mapping[chunk["endnode"]]
        boundary = "B"
        for i in range(start_idx, end_idx+1):
            tags[i] = "{}-{}".format(boundary, label)
            boundary = "I"
    return tags

def process_mention_chunks(tokens, chunks, start_mapping, end_mapping):
    tags = ["O"]*len(tokens)
    instances = ["O"]*len(tokens)
    for chunk in chunks:
        instance = chunk["features"]["inst"]
        label = ".".join(filter(lambda x: x, [chunk["features"].get(k) for k in ["class", "subclass"]]))
        start_idx = start_mapping[chunk["startnode"]]
        end_idx = end_mapping[chunk["endnode"]]
        boundary = "B"
        for i in range(start_idx, end_idx+1):
            tags[i] = "{}-{}".format(boundary, label)
            instances[i] = instance
            boundary = "I"
            instance = "I"
    return tags, instances


def xml2soup(input_file):
    with open(input_file) as fp:
        data = fp.read()
    soup = BeautifulSoup(data, "lxml")
    return soup


def process_gate_xml2json(soup):
    data = {}
    text = soup.find("textwithnodes").text
    data["text"] = text
    data["annotationsets"] = {}
    annotationsets = get_annotation_sets(soup)
    for annotationset in annotationsets:
        name = annotationset.attrs["name"]
        annotation_data = [
                annotation2dict(v)
                for v in annotationset.find_all("annotation")
                ]
        data["annotationsets"][name] = annotation_data
    return data


def get_sorted_annotations(annotations):
    sorted_annotations = []
    for annotation in annotations:
        instance = annotation["features"]["inst"]
        label = ".".join(filter(lambda x: x, [annotation["features"].get(k) for k in ["class", "subclass"]]))
        start_idx = int(annotation["startnode"])
        end_idx = int(annotation["endnode"])
        sorted_annotations.append((start_idx, end_idx, label, instance))
    sorted_annotations = sorted(sorted_annotations, key=lambda x: x[0])
    return sorted_annotations

def get_segments(sorted_annotations, text):
    segments = []
    last_idx = 0
    for start_idx, end_idx, label, instance in sorted_annotations:
        # process uuannotated starting segment 
        #if start_idx > 0 and last_idx == 0:
        #    segment = (text[:start_idx], 0, start_idx, "O", "O")
        #    segments.append(segment)
        # process segments for unannotated text between annotations
        if start_idx > last_idx:
            segment = (text[last_idx:start_idx], last_idx, start_idx, "O", "O")
            segments.append(segment)
        # process normal annotated segment
        segment = (text[start_idx:end_idx], start_idx, end_idx, label, instance)
        segments.append(segment)
        last_idx = end_idx
    # Ensure last remaining unannotated segment is included
    if last_idx < len(text):
        segment = (text[last_idx:], last_idx, len(text), "O", "O")
        segments.append(segment)
    return segments

def segment2tokens(segment_text, start_idx, end_idx, label, instance):
    boundary = "" if label == "O" else "B"
    token_list = []
    tokens = tokenizer.tokenize(segment_text)
    for token in tokens:
        processed_label = "O"
        if label != "O":
            processed_label = "{}-{}".format(boundary, label)
        token_list.append((token, start_idx, end_idx, processed_label, instance))
        if boundary == "B":
            boundary = "I"
        if instance != "O":
            instance = "PREV"
    return token_list

def get_seq_from_segments(segments):
    seq = []
    # convert annotated segments to tagged tokens
    for segment_text, start_idx, end_idx, label, instance in segments:
        if segment_text:
            token_list = segment2tokens(segment_text, start_idx, end_idx, label, instance)
            seq.extend(token_list)
    return seq

def process_gate_json2conll(gate_json):
    text = gate_json["text"]
    EXCLUDED_TYPES = set(["Token", "SpaceToken"])
    annotations = gate_json["annotationsets"]["Key"]
    sorted_annotations = get_sorted_annotations(annotations)
    segments = get_segments(sorted_annotations, text)
    seq = get_seq_from_segments(segments)
    return seq  

def process_line(i, line, add_comments_idx=False):
    if add_comments_idx:
        line = (i,) + line
    else:
        line = (line[0], line[3])
    return tuple([str(v) for v in line])

def sequence2string(seq, add_comments_idx=False):
    return "\n".join([
        "\t".join(process_line(i, line, add_comments_idx)) 
        for i, line in enumerate(seq)
        ])

def process_gate_dir(input_dir, output_file, output_format, add_comments_idx=False):
    xml_files = glob("{}/*.xml".format(input_dir))
    corrupted_files = 0
    with open(output_file, "w+") as fp:
        for filename in tqdm(xml_files):
            try:
                soup = xml2soup(filename)
                if output_format == "conll":
                    seq_json = process_gate_xml2json(soup)
                    seq = process_gate_json2conll(seq_json)
                    seq_str = sequence2string(seq, add_comments_idx)
                    if add_comments_idx:
                        print("# Source file: {}".format(filename), file=fp)
                        print("# Text: {}".format(seq_json["text"]), file=fp)
                    print(seq_str, end="\n\n", file=fp)
                elif output_format == "json":
                    seq = process_gate_xml2json(soup)
                    seq_str = json.dumps(seq)
                    print(seq_str, file=fp)
            except:
                print("File: {}, output: {}".format(filename, output_file))
                corrupted_files += 1
    print("Found {} corrupted files".format(corrupted_files))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", help="input directory")
    parser.add_argument("--output-file", help="output file for conll format")
    parser.add_argument("--output-format", choices=["json", "conll"], help="output file for conll format")
    parser.add_argument(
            "--add-comments-idx", 
            default=False, 
            action="store_true", 
            help="Pass to include original text as comment and index of each token"
            )
    args = parser.parse_args()
    process_gate_dir(args.input_dir, args.output_file, args.output_format, args.add_comments_idx)

