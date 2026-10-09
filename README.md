# Fraud Detection Pipeline

A pipeline for generating synthetic e-commerce order data, both legitimate and fraudulent, and using it to build and evaluate fraud detection.

> **Status:** early development. The order generators are stubs. This documentation is a scaffold and will be filled in as the code is written. Items marked `TODO` are still to be decided or built.

## Repository layout

| Path | Description |
| --- | --- |
| `Normal Order Generator.ipynb` | Generates synthetic **legitimate** orders. *(stub)* |
| `Fraud Order Generator.ipynb` | Generates synthetic **fraudulent** orders. *(stub)* |
| `docs/` | Project documentation (see below). |

## Documentation

- [Architecture](docs/architecture.md): pipeline stages and how data moves between them.
- [Data generation](docs/data-generation.md): how the normal and fraud order generators work, plus the order schema.
- [Contributing](docs/contributing.md): environment setup and working conventions.

## Getting started

### Prerequisites

- Python 3 *(TODO: pin the version)*
- Jupyter (Notebook or Lab)
- TODO: list dependencies, ideally in a `requirements.txt` or `pyproject.toml`

### Running the generators

```bash
pip install jupyter   # plus project dependencies once listed
jupyter lab
```

Open each generator notebook and run all cells. TODO: record the output location and file format.

## Roadmap

- [ ] Implement the normal order generator
- [ ] Implement the fraud order generator
- [ ] Define a shared order schema
- [ ] Combine and label the datasets
- [ ] Feature engineering
- [ ] Model training and evaluation
- [ ] Scoring and inference
