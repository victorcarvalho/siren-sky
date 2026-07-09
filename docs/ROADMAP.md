# SirenSky project roadmap

This roadmap outlines the milestones achieved so far and planned future improvements for the SirenSky platform.

## 🚀 Completed milestones
- [x] **Base classification pipeline**: Integrated OpenAI Vision client with a local simulation fallback.
- [x] **API and shared logic refactoring**: Extracted core orchestration into `classification_service.py` to support both the REST API and Streamlit.
- [x] **Robust error handling**: Added `tenacity` retries for transient OpenAI errors and implemented standard exception mappings in the FastAPI wrapper.
- [x] **Streamlit UI styling**: Externalized CSS styling and implemented colored badges for alert statuses.

## 🗺️ Future roadmap

### Phase 1: Pipeline optimization (near-term)
- [ ] **Concurrent classifications**: Implement asynchronous request processing (via Python's `asyncio` or threading pools) to process batch uploads concurrently instead of sequentially.
- [ ] **Local model fallback**: Implement the placeholder `classify_image_local` function to support lightweight local neural network classifiers (e.g., ONNX, MobileNet) when offline.

### Phase 2: User experience and map upgrades (mid-term)
- [ ] **Interactive status overrides**: Allow users to click on the pydeck map markers and manually override/resolve warnings/alerts directly.
- [ ] **Multi-language support**: Implement standard localization configurations (Portuguese and English).

### Phase 3: Analytics and advanced reporting (long-term)
- [ ] **MLflow dashboard enhancements**: Log confusion matrices and custom visual artifacts directly to MLflow runs.
- [ ] **Exportable reports**: Add PDF/CSV export functionality for generated alerts.
