# ReNoun
This is the self-implementation of [ReNoun: Fact Extraction for Nominal Attributes](https://www.aclweb.org/anthology/D14-1038.pdf), the representative noun-based OpenIE systems.

## Overview of ReNoun
- Noun-based OpenIE system: From the natural language text, extract triple whose relation is represented as a noun.
    + e.g. "Larry Page is the CEO of Google." -> (Google; CEO; Larry Page)
- How ReNoun extracts fact from the natural language text:
    1. Seed fact extraction: Extract plausible facts from the corpus based on simple rules
    2. Extraction pattern generation: Obtain the set of dependency patterns of the triples acquired at 1st step
    3. Candidate generation: Apply dependency patterns to the corpus and acquire the candidates of facts
    4. Scoring: Scoring the candidate facts
- Resources needed for running
    + Target corpus for extracting the fact
    + Datasets composed of Attributes (e.g. mother, CEO, birthdate, ...)

## Description of directories
- requirements.txt: packages needed for running
- renoun.py: implementation
- test_renoun.py: test with sample text

## Progress of implementation
Implementation itself is done, but there are some lacks for extracting rich facts:
- Preparation of attribute dataset: Biperpedia is used in the paper, but it is not released publicly. It would be possible to make use of labels extracted from some LOD such as DBpedia.
- Scoring is not yet implemented. This is because I don't have attribute dataset for now, which means we cannot extract enough triples for valid scoring.
