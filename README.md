# 🧾 Multimodal OCR Agent

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?style=flat-square&logo=huggingface&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-In%20Development-orange?style=flat-square)

**An agentic AI pipeline for digitizing and classifying insurance claim document IDs using multimodal learning (image + text).**

[Overview](#-overview) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Model](#-model) • [Results](#-results) • [Roadmap](#-roadmap)

</div>

---

## 📌 Overview

DigiNsure Inc. is digitizing historical insurance claim documents scanned from paper. Each document contains one or more IDs that must be:

1. **Extracted** from scanned document images via OCR
2. **Classified** as either a **Primary ID** or **Secondary ID**

This project solves that with an **agentic pipeline** that fuses two input modalities:

| Modality | Input | Purpose |
|----------|-------|---------|
| 🖼️ Image | Scanned document (JPG/PNG) | Visual context of the document |
| 📝 Text | Insurance type label | Domain-specific classification signal |

Supported insurance types: `home` · `life` · `auto` · `health` · `other`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              Multimodal OCR Agent                │
│                                                  │
│  Input: Scanned Image + Insurance Type           │
│          │                                       │
│    ┌─────▼──────┐                                │
│    │  OCR Tool  │  ← Tesseract / AWS Textract    │
│    └─────┬──────┘                                │
│          │ raw text                              │
│    ┌─────▼────────────┐                          │
│    │  ID Extractor    │  ← regex + pattern match │
│    └─────┬────────────┘                          │
│          │ candidate IDs                         │
│    ┌─────▼───────────────────┐                   │
│    │  Multimodal Classifier  │                   │
│    │  ┌──────────┐           │                   │
│    │  │  Image   │ CNN / ViT │                   │
│    │  │  Encoder │           │                   │
│    │  └────┬─────┘           │                   │
│    │       │  Fusion Layer   │                   │
│    │  ┌────▼─────┐           │                   │
│    │  │  Text    │ Embedding │                   │
│    │  │  Encoder │           │                   │
│    │  └────┬─────┘           │                   │
│    │       │  FC Head        │                   │
│    └───────┼─────────────────┘                   │
│            │                                     │
│    Output: PRIMARY / SECONDARY + confidence      │
└─────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Multimodal-OCR-Agent/
├── README.md
├── requirements.txt
├── .env.example                  # Environment variable template
├── agent/
│   ├── agent.py                  # Main agent orchestration loop
│   └── tools/
│       ├── __init__.py
│       ├── ocr_tool.py           # OCR extraction (Tesseract / Textract)
│       ├── id_extractor.py       # Regex pattern matching for ID candidates
│       └── classifier.py         # Calls multimodal model for labeling
├── model/
│   ├── multimodal_model.py       # Image + text fusion model (PyTorch)
│   ├── train.py                  # Training script with CLI args
│   ├── evaluate.py               # Evaluation metrics (F1, accuracy)
│   └── checkpoints/              # Saved model weights (gitignored)
├── data/
│   ├── sample_scans/             # Sample scanned document images
│   └── labels/                   # Ground truth CSV (image, type, label)
├── notebooks/
│   └── exploration.ipynb         # EDA, preprocessing, prototyping
├── tests/
│   ├── test_ocr_tool.py
│   ├── test_id_extractor.py
│   └── test_classifier.py
├── configs/
│   └── config.yaml               # Model and pipeline hyperparameters
└── Dockerfile                    # Container for reproducible inference
```

---

## ⚙️ Installation

### Prerequisites

- Python 3.10+
- Tesseract OCR installed on your system
- CUDA-compatible GPU (recommended for model training)

### 1. Clone the repo

```bash
git clone https://github.com/Moulica5374/Agentic-AI.git
cd Agentic-AI/Multimodal-OCR-Agent
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Tesseract

```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr

# macOS
brew install tesseract

# Windows — download installer from:
# https://github.com/UB-Mannheim/tesseract/wiki
```

### 5. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your AWS credentials if using Textract
```

---

## 🚀 Usage

### Run the agent on a single document

```bash
python agent/agent.py \
  --image data/sample_scans/claim_001.jpg \
  --insurance_type auto
```

### Run on a batch of documents

```bash
python agent/agent.py \
  --batch data/sample_scans/ \
  --insurance_type health \
  --output results/output.json
```

### Sample Output

```json
{
  "document": "claim_001.jpg",
  "insurance_type": "auto",
  "ids_found": [
    {
      "value": "CLM-2024-00482",
      "label": "PRIMARY",
      "confidence": 0.97
    },
    {
      "value": "POL-AUT-88231",
      "label": "SECONDARY",
      "confidence": 0.91
    }
  ],
  "processing_time_ms": 342
}
```

---

## 🧠 Model

### Multimodal Fusion Architecture

The classifier combines two modalities:

```
Image (scanned doc)  →  CNN / ViT Encoder  ──┐
                                              ├──► Concat ──► FC ──► Softmax
Insurance Type Text  →  Embedding Layer    ──┘
```

| Component | Options | Default |
|-----------|---------|---------|
| Image Encoder | ResNet-50, ViT-B/16 | ResNet-50 |
| Text Encoder | Embedding + MLP, BERT | Embedding + MLP |
| Fusion Strategy | Concatenation, Cross-Attention | Concatenation |
| Output Classes | Primary / Secondary | Binary |

### Training

```bash
python model/train.py \
  --data_dir data/ \
  --epochs 30 \
  --batch_size 32 \
  --lr 1e-4 \
  --image_encoder resnet50 \
  --output_dir model/checkpoints/
```

### Evaluation

```bash
python model/evaluate.py \
  --checkpoint model/checkpoints/best_model.pt \
  --test_data data/labels/test.csv
```

---

## 📊 Results

> ⚠️ Results will be updated as training data is collected and the model is trained.

| Insurance Type | Accuracy | F1 Score |
|----------------|----------|----------|
| Auto | — | — |
| Health | — | — |
| Home | — | — |
| Life | — | — |
| Other | — | — |
| **Overall** | **—** | **—** |

---

## 🔑 Label Reference

| Label | Description |
|-------|-------------|
| `PRIMARY` | Main identifier for the insurance claim (e.g., claim number) |
| `SECONDARY` | Supporting or reference ID on the same document (e.g., policy number) |

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 🐳 Docker

```bash
# Build
docker build -t multimodal-ocr-agent .

# Run
docker run --rm \
  -v $(pwd)/data:/app/data \
  multimodal-ocr-agent \
  --image /app/data/sample_scans/claim_001.jpg \
  --insurance_type auto
```

---

## 🗺️ Roadmap

- [x] Project scaffold and README
- [ ] OCR tool integration (Tesseract baseline)
- [ ] ID extractor with insurance-type-specific regex patterns
- [ ] Dataset collection and labeling pipeline
- [ ] Multimodal model training pipeline
- [ ] Agent orchestration with tool routing
- [ ] Evaluation metrics (accuracy, F1 per insurance type)
- [ ] REST API wrapper (FastAPI)
- [ ] Streamlit demo UI
- [ ] Docker containerization
- [ ] CI/CD with GitHub Actions

---

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss any changes.

```bash
# Fork → Clone → Create branch → Commit → PR
git checkout -b feature/your-feature-name
```

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

---

## 🔗 Part of

[**Agentic-AI**](https://github.com/Moulica5374/Agentic-AI) — A structured repo of AI agents from beginner to production-grade, built by [@Moulica5374](https://github.com/Moulica5374).
