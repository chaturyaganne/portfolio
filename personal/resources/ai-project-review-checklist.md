# AI project review checklist

A practical review aid from Chaturya Ganne's portfolio. Choose the questions relevant to your project; this is not a substitute for a domain-specific review.

## Problem and scope

- [ ] Can someone explain the task and intended user after reading the introduction?
- [ ] Is the project clearly labeled as research, a prototype, or a deployed application?
- [ ] Is your contribution separate from framework, dataset, and collaborator contributions?

## Data and baselines

- [ ] Are the data source, permitted uses, and known limitations documented?
- [ ] Have you checked for overlap or leakage between development and evaluation data?
- [ ] Is there a meaningful baseline using the same evaluation conditions?
- [ ] Are preprocessing and split choices recorded?

## Model and retrieval behavior

- [ ] Are model versions, parameters, prompts, and index settings recorded where applicable?
- [ ] For RAG, can you inspect which evidence was retrieved before evaluating the final answer?
- [ ] Have you tested missing, irrelevant, conflicting, and stale context?
- [ ] Can the system communicate uncertainty or decline when evidence is insufficient?

## Evaluation and reporting

- [ ] Are metric definitions and the evaluation procedure clear?
- [ ] Are benchmark results distinguished from real-world business outcomes?
- [ ] Are latency and resource-use measurements tied to hardware, workload, and methodology?
- [ ] Are failure examples and known weak slices included?
- [ ] Are qualitative examples selected transparently rather than presented as aggregate evidence?

## Interface and reliability

- [ ] Are loading, empty, failure, and recovery states usable?
- [ ] Are controls labeled and keyboard interactions considered?
- [ ] Does the interface separate generated output from verified source material?
- [ ] Are sample data and simulated results visibly identified?

## Sharing and reproducibility

- [ ] Does the repository explain setup, evaluation, and available artifacts?
- [ ] Have private data, API keys, and environment secrets been excluded?
- [ ] Do outbound links work, and is there a useful fallback if a demo is unavailable?
- [ ] Are references, collaborators, and AI assistance credited?
- [ ] Is there a concrete next experiment rather than an unsupported claim of completeness?

---
Portfolio: https://chaturyaganne.github.io/portfolio/
You may copy and adapt this checklist. No performance, accessibility, or safety certification is implied.
