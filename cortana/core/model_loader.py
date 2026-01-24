"""Model Loader - Load and manage AI models efficiently"""
import logging
import os
from typing import Dict, Any, Optional, List
import torch
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelLoader:
    """Loads and manages AI models with efficient memory usage"""
    
    def __init__(self, model_dir: str = "./models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.loaded_models = {}
        self.device = self._get_best_device()
        logger.info(f"ModelLoader initialized on {self.device}")
    
    def _get_best_device(self) -> str:
        """Determine best device for model loading"""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    
    def load_model(self, model_name: str, model_config: Dict[str, Any]) -> Any:
        """Load a model based on configuration"""
        if model_name in self.loaded_models:
            logger.info(f"Model {model_name} already loaded")
            return self.loaded_models[model_name]
        
        try:
            model_type = model_config.get('type', 'huggingface')
            
            if model_type == 'huggingface':
                model = self._load_huggingface_model(model_config)
            elif model_type == 'local':
                model = self._load_local_model(model_config)
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            
            self.loaded_models[model_name] = model
            logger.info(f"Successfully loaded model: {model_name}")
            return model
        
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            raise
    
    def _load_huggingface_model(self, config: Dict[str, Any]) -> Any:
        """Load model from Hugging Face"""
        from transformers import AutoModel, AutoTokenizer
        
        model_id = config['model_id']
        use_auth = config.get('use_auth_token', False)
        
        logger.info(f"Loading HuggingFace model: {model_id}")
        
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            use_auth_token=use_auth if use_auth else None
        )
        
        model = AutoModel.from_pretrained(
            model_id,
            use_auth_token=use_auth if use_auth else None,
            torch_dtype=torch.float16 if self.device != 'cpu' else torch.float32
        )
        
        model.to(self.device)
        model.eval()
        
        return {'model': model, 'tokenizer': tokenizer}
    
    def _load_local_model(self, config: Dict[str, Any]) -> Any:
        """Load model from local path"""
        model_path = self.model_dir / config['path']
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        logger.info(f"Loading local model: {model_path}")
        model = torch.load(model_path, map_location=self.device)
        model.eval()
        
        return {'model': model}
    
    def download_model(self, url: str, filename: str) -> Path:
        """Download a model from URL"""
        model_path = self.model_dir / filename
        
        if model_path.exists():
            logger.info(f"Model already exists: {filename}")
            return model_path
        
        logger.info(f"Downloading model from {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(model_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Downloaded model: {filename}")
        return model_path
    
    def unload_model(self, model_name: str) -> None:
        """Unload a model from memory"""
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            logger.info(f"Unloaded model: {model_name}")
    
    def get_loaded_models(self) -> List[str]:
        """Get list of loaded models"""
        return list(self.loaded_models.keys())
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            'device': self.device,
            'loaded_models': self.get_loaded_models(),
            'model_dir': str(self.model_dir),
            'cuda_available': torch.cuda.is_available()
        }
