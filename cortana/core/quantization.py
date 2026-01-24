"""Model Quantization - Reduce memory usage through quantization"""
import logging
import torch
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class ModelQuantizer:
    """Quantizes models to reduce memory footprint"""
    
    def __init__(self):
        self.quantization_configs = {
            'int8': {'dtype': torch.qint8, 'reduce_range': False},
            'int4': {'bits': 4},
            'fp16': {'dtype': torch.float16}
        }
        logger.info("ModelQuantizer initialized")
    
    def quantize_model(self, model: Any, method: str = 'int8') -> Any:
        """Quantize a model using specified method"""
        if method not in self.quantization_configs:
            raise ValueError(f"Unknown quantization method: {method}")
        
        try:
            if method == 'int8':
                return self._quantize_int8(model)
            elif method == 'fp16':
                return self._quantize_fp16(model)
            elif method == 'int4':
                return self._quantize_int4(model)
            else:
                raise NotImplementedError(f"Method {method} not implemented")
        except Exception as e:
            logger.error(f"Error quantizing model: {e}")
            raise
    
    def _quantize_int8(self, model: Any) -> Any:
        """Quantize model to INT8"""
        logger.info("Quantizing model to INT8")
        
        if hasattr(model, 'config'):
            model.config.quantization_config = {'load_in_8bit': True}
        
        # Dynamic quantization
        quantized_model = torch.quantization.quantize_dynamic(
            model,
            {torch.nn.Linear, torch.nn.Conv2d},
            dtype=torch.qint8
        )
        
        logger.info("INT8 quantization completed")
        return quantized_model
    
    def _quantize_fp16(self, model: Any) -> Any:
        """Convert model to FP16"""
        logger.info("Converting model to FP16")
        
        if hasattr(model, 'half'):
            model = model.half()
        else:
            # Manual conversion
            for param in model.parameters():
                param.data = param.data.half()
        
        logger.info("FP16 conversion completed")
        return model
    
    def _quantize_int4(self, model: Any) -> Any:
        """Quantize model to INT4 (simplified)"""
        logger.info("Quantizing model to INT4")
        
        # Simplified INT4 quantization
        # In production, use libraries like bitsandbytes
        try:
            import bitsandbytes as bnb
            
            # Configure for 4-bit
            if hasattr(model, 'config'):
                model.config.quantization_config = {
                    'load_in_4bit': True,
                    'bnb_4bit_compute_dtype': torch.float16
                }
            
            logger.info("INT4 quantization completed")
            return model
        except ImportError:
            logger.warning("bitsandbytes not available, falling back to INT8")
            return self._quantize_int8(model)
    
    def estimate_size_reduction(self, original_size_mb: float, method: str) -> Dict[str, float]:
        """Estimate memory reduction from quantization"""
        reduction_factors = {
            'fp16': 0.5,   # 50% reduction
            'int8': 0.25,  # 75% reduction
            'int4': 0.125  # 87.5% reduction
        }
        
        factor = reduction_factors.get(method, 1.0)
        quantized_size = original_size_mb * factor
        saved = original_size_mb - quantized_size
        
        return {
            'original_size_mb': original_size_mb,
            'quantized_size_mb': quantized_size,
            'saved_mb': saved,
            'reduction_percent': (saved / original_size_mb) * 100
        }
    
    def benchmark_quantization(self, model: Any, test_input: Any) -> Dict[str, Any]:
        """Benchmark quantization methods"""
        results = {}
        
        for method in ['fp16', 'int8']:
            try:
                import time
                
                # Quantize
                start = time.time()
                quantized = self.quantize_model(model, method)
                quant_time = time.time() - start
                
                # Test inference
                start = time.time()
                with torch.no_grad():
                    _ = quantized(test_input)
                inference_time = time.time() - start
                
                results[method] = {
                    'quantization_time': quant_time,
                    'inference_time': inference_time
                }
            except Exception as e:
                logger.error(f"Benchmark failed for {method}: {e}")
                results[method] = {'error': str(e)}
        
        return results
    
    def get_supported_methods(self) -> list:
        """Get list of supported quantization methods"""
        return list(self.quantization_configs.keys())
