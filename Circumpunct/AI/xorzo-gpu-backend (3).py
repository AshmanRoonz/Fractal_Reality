#!/usr/bin/env python3
"""
XORZO GPU BACKEND
==================
Real semantic embeddings + fast similarity search using GPU

Requirements (Windows or Linux):
    pip install torch sentence-transformers websockets numpy

Optional (Linux only, faster search):
    pip install faiss-gpu  # or faiss-cpu

Run:
    python xorzo-gpu-backend.py

Then open xorzo-modular.html and enable the GPU module.
"""

import asyncio
import json
import numpy as np
from pathlib import Path
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try imports
torch = None
try:
    import torch
    DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info(f"PyTorch device: {DEVICE}")
    if DEVICE == 'cuda':
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
except ImportError:
    logger.error("PyTorch not installed. Run: pip install torch")
    DEVICE = 'cpu'

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDER = None  # Lazy load
except ImportError:
    logger.error("sentence-transformers not installed. Run: pip install sentence-transformers")
    EMBEDDER = None

try:
    import faiss
    FAISS_AVAILABLE = True
    FAISS_GPU = hasattr(faiss, 'StandardGpuResources')
    logger.info(f"FAISS available: {FAISS_AVAILABLE}, GPU: {FAISS_GPU}")
except ImportError:
    logger.warning("FAISS not installed. Using PyTorch for similarity search (still fast with GPU)")
    faiss = None
    FAISS_AVAILABLE = False
    FAISS_GPU = False

try:
    import websockets
except ImportError:
    logger.error("websockets not installed. Run: pip install websockets")
    websockets = None


class XorzoGPUBackend:
    """GPU-accelerated backend for Xorzo"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.embedder = None
        self.memories = []  # List of (text, source, time, relevance)
        self.embeddings = None  # numpy array of embeddings
        self.embeddings_tensor = None  # PyTorch tensor for GPU search (when no FAISS)
        self.index = None  # FAISS index or 'pytorch' flag
        self.dim = 384  # Embedding dimension for all-MiniLM-L6-v2
        self.center = None  # Computed centroid
        self.goal_vec = None
        
    def load_model(self):
        """Load the embedding model (lazy load for faster startup)"""
        if self.embedder is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.embedder = SentenceTransformer(self.model_name, device=DEVICE)
            logger.info("Model loaded!")
        return self.embedder
    
    def embed(self, texts: list[str]) -> np.ndarray:
        """Embed texts using the model"""
        self.load_model()
        embeddings = self.embedder.encode(
            texts, 
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 100,
            device=DEVICE
        )
        return embeddings.astype('float32')
    
    def embed_single(self, text: str) -> np.ndarray:
        """Embed a single text"""
        return self.embed([text])[0]
    
    def build_index(self):
        """Build index for fast similarity search"""
        if len(self.memories) == 0:
            self.index = None
            return
            
        if self.embeddings is None:
            # Embed all memories
            texts = [m['text'] for m in self.memories]
            self.embeddings = self.embed(texts)
        
        # Normalize for cosine similarity
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        self.embeddings = self.embeddings / (norms + 1e-8)
        
        if FAISS_AVAILABLE:
            # Build FAISS index
            self.index = faiss.IndexFlatIP(self.dim)  # Inner product (cosine on normalized)
            
            # Move to GPU if available
            if FAISS_GPU and DEVICE == 'cuda':
                res = faiss.StandardGpuResources()
                self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
            
            self.index.add(self.embeddings)
            logger.info(f"Built FAISS index with {len(self.memories)} memories")
        else:
            # Use PyTorch tensor for GPU-accelerated search
            self.embeddings_tensor = torch.tensor(self.embeddings, device=DEVICE)
            self.index = 'pytorch'  # Flag that we're using PyTorch
            logger.info(f"Built PyTorch index with {len(self.memories)} memories on {DEVICE}")
    
    def add_memory(self, text: str, source: str = 'direct', time: float = None, relevance: float = 1.0):
        """Add a single memory"""
        import time as time_module
        if time is None:
            time = time_module.time() * 1000
            
        self.memories.append({
            'text': text,
            'source': source,
            'time': time,
            'relevance': relevance
        })
        
        # Embed and add to index
        vec = self.embed_single(text)
        vec = vec / (np.linalg.norm(vec) + 1e-8)  # Normalize
        vec = vec.reshape(1, -1)
        
        if self.embeddings is None:
            self.embeddings = vec
        else:
            self.embeddings = np.vstack([self.embeddings, vec])
        
        # Update index
        if FAISS_AVAILABLE and self.index is not None and self.index != 'pytorch':
            self.index.add(vec.astype('float32'))
        elif self.index == 'pytorch':
            # Rebuild PyTorch tensor
            self.embeddings_tensor = torch.tensor(self.embeddings, device=DEVICE)
    
    def add_memories_batch(self, memories: list[dict], rebuild_index: bool = True):
        """Add multiple memories efficiently"""
        if not memories:
            return 0
            
        import time as time_module
        now = time_module.time() * 1000
        
        logger.info(f"Processing {len(memories)} memories...")
        
        texts = []
        for m in memories:
            self.memories.append({
                'text': m.get('text', ''),
                'source': m.get('source', 'import'),
                'time': m.get('time', now),
                'relevance': m.get('relevance', 1.0)
            })
            texts.append(m.get('text', ''))
        
        # Batch embed - this is the slow part
        logger.info(f"Embedding {len(texts)} texts...")
        start = time_module.time()
        new_embeddings = self.embed(texts)
        elapsed = time_module.time() - start
        logger.info(f"Embedding complete: {elapsed:.2f}s ({len(texts)/max(elapsed,0.001):.0f} texts/sec)")
        
        # Normalize
        norms = np.linalg.norm(new_embeddings, axis=1, keepdims=True)
        new_embeddings = new_embeddings / (norms + 1e-8)
        
        if self.embeddings is None:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])
        
        # Optionally rebuild index (skip during chunked uploads)
        if rebuild_index:
            logger.info("Building search index...")
            self.build_index()
            logger.info("Index built!")
        
        return len(memories)
    
    def compute_center(self):
        """Compute center as centroid of all memories"""
        if self.embeddings is None or len(self.embeddings) == 0:
            self.center = None
            logger.info("No embeddings to compute center from")
            return
        
        self.center = np.mean(self.embeddings, axis=0)
        # Normalize
        norm = np.linalg.norm(self.center)
        if norm > 0:
            self.center /= norm
        
        logger.info(f"Computed center from {len(self.memories)} memories (|c| = {norm:.4f})")
    
    def search(self, query: str, k: int = 10, threshold: float = 0.1) -> list[dict]:
        """Search for similar memories"""
        if self.index is None or len(self.memories) == 0:
            return []
        
        # Embed query
        query_vec = self.embed_single(query)
        query_vec = query_vec / (np.linalg.norm(query_vec) + 1e-8)  # Normalize
        
        k = min(k, len(self.memories))
        
        if FAISS_AVAILABLE and self.index != 'pytorch':
            # Use FAISS
            query_vec = query_vec.reshape(1, -1).astype('float32')
            similarities, indices = self.index.search(query_vec, k)
            similarities = similarities[0]
            indices = indices[0]
        else:
            # Use PyTorch GPU-accelerated search
            query_tensor = torch.tensor(query_vec, device=DEVICE)
            
            # Cosine similarity (embeddings already normalized)
            similarities = torch.matmul(self.embeddings_tensor, query_tensor)
            
            # Get top-k
            top_k = torch.topk(similarities, k)
            similarities = top_k.values.cpu().numpy()
            indices = top_k.indices.cpu().numpy()
        
        results = []
        for sim, idx in zip(similarities, indices):
            if sim >= threshold and idx < len(self.memories):
                mem = self.memories[idx].copy()
                mem['similarity'] = float(sim)
                mem['index'] = int(idx)
                
                # Add center similarity if available
                if self.center is not None:
                    center_sim = float(np.dot(self.embeddings[idx], self.center))
                    mem['center_similarity'] = center_sim
                
                results.append(mem)
        
        return results
    
    def respond(self, query: str, k: int = 10) -> dict:
        """Generate a response based on similar memories with coherence"""
        matches = self.search(query, k=k)
        
        if not matches:
            return {
                'response': "I need more knowledge about that.",
                'matches': [],
                'center_magnitude': 0
            }
        
        # Sort by combined score (similarity + center coherence)
        for m in matches:
            center_sim = m.get('center_similarity', 0)
            m['score'] = m['similarity'] * 0.7 + center_sim * 0.3
        
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        # Extract and embed sentences from top matches
        candidate_sentences = []
        
        for match in matches[:8]:
            text = match['text']
            # Better sentence splitting
            import re
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            for sent in sentences:
                sent = sent.strip()
                # Skip garbage
                if len(sent) < 20 or len(sent) > 300:
                    continue
                if '{' in sent or '}' in sent or '<' in sent or '>' in sent:
                    continue
                if sent.count('|') > 2 or sent.count('-') > 10:
                    continue
                    
                candidate_sentences.append({
                    'text': sent,
                    'source_sim': match['similarity'],
                    'source': match.get('source', 'unknown')
                })
        
        if not candidate_sentences:
            return {
                'response': "I'm having trouble forming a clear response.",
                'matches': matches[:5],
                'center_magnitude': 0
            }
        
        # Embed query for coherence checking
        query_emb = self.embed([query])[0]
        query_emb = query_emb / (np.linalg.norm(query_emb) + 1e-8)
        
        # Score candidates by similarity to query
        for cand in candidate_sentences:
            cand_emb = self.embed([cand['text']])[0]
            cand_emb = cand_emb / (np.linalg.norm(cand_emb) + 1e-8)
            cand['direct_sim'] = float(np.dot(query_emb, cand_emb))
            cand['total_score'] = cand['direct_sim'] * 0.6 + cand['source_sim'] * 0.4
        
        # Sort by total score
        candidate_sentences.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Build coherent response
        response_parts = []
        used_prefixes = set()
        last_emb = query_emb
        
        for cand in candidate_sentences:
            # Skip duplicates
            prefix = cand['text'][:40].lower()
            if prefix in used_prefixes:
                continue
            
            # Check coherence with last sentence
            cand_emb = self.embed([cand['text']])[0]
            cand_emb = cand_emb / (np.linalg.norm(cand_emb) + 1e-8)
            coherence = float(np.dot(last_emb, cand_emb))
            
            # First sentence: must be similar to query (>0.3)
            # Subsequent: must flow from previous (>0.2)
            threshold = 0.3 if len(response_parts) == 0 else 0.2
            
            if coherence > threshold or (len(response_parts) == 0 and cand['direct_sim'] > 0.4):
                response_parts.append(cand['text'])
                used_prefixes.add(prefix)
                last_emb = cand_emb
                
                if len(response_parts) >= 3:
                    break
        
        # Capitalize first letter of each sentence
        response_parts = [s[0].upper() + s[1:] if len(s) > 1 else s for s in response_parts]
        
        response = ' '.join(response_parts)
        if response and not response.endswith(('.', '!', '?')):
            response += '.'
        
        center_mag = float(np.linalg.norm(self.center)) if self.center is not None else 0
        
        return {
            'response': response,
            'matches': matches[:5],
            'center_magnitude': center_mag,
            'memory_count': len(self.memories),
            'candidates_considered': len(candidate_sentences)
        }
    
    def get_stats(self) -> dict:
        """Get backend statistics"""
        search_method = 'none'
        if self.index == 'pytorch':
            search_method = f'pytorch-{DEVICE}'
        elif FAISS_AVAILABLE and self.index is not None:
            search_method = 'faiss-gpu' if (FAISS_GPU and DEVICE == 'cuda') else 'faiss-cpu'
        
        gpu_name = None
        if torch is not None and DEVICE == 'cuda':
            gpu_name = torch.cuda.get_device_name(0)
        
        return {
            'device': DEVICE,
            'gpu_name': gpu_name,
            'model': self.model_name,
            'embedding_dim': self.dim,
            'memory_count': len(self.memories),
            'index_size': len(self.memories) if self.index else 0,
            'search_method': search_method,
            'faiss_available': FAISS_AVAILABLE,
            'center_computed': self.center is not None
        }
    
    def clear(self):
        """Clear all memories"""
        count = len(self.memories)
        self.memories = []
        self.embeddings = None
        self.embeddings_tensor = None
        self.index = None
        self.center = None
        return count


# WebSocket Server
backend = XorzoGPUBackend()


async def handle_message(websocket, message: dict) -> dict:
    """Handle incoming WebSocket messages"""
    import asyncio
    action = message.get('action')
    
    if action == 'embed':
        # Embed text(s) - run in executor to not block
        texts = message.get('texts', [message.get('text', '')])
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(None, backend.embed, texts)
        return {'embeddings': embeddings.tolist()}
    
    elif action == 'add_memory':
        # Add single memory
        backend.add_memory(
            text=message.get('text', ''),
            source=message.get('source', 'direct'),
            time=message.get('time'),
            relevance=message.get('relevance', 1.0)
        )
        return {'success': True, 'count': len(backend.memories)}
    
    elif action == 'add_memories':
        # Batch add memories - this is heavy, run in executor
        memories = message.get('memories', [])
        rebuild = message.get('rebuild_index', True)
        logger.info(f"Received {len(memories)} memories to add (rebuild={rebuild})")
        
        # Run the heavy work in a thread pool
        loop = asyncio.get_event_loop()
        count = await loop.run_in_executor(None, lambda: backend.add_memories_batch(memories, rebuild))
        logger.info(f"Added {count} memories, total: {len(backend.memories)}")
        
        return {
            'success': True, 
            'added': count, 
            'total': len(backend.memories),
            'center_computed': backend.center is not None
        }
    
    elif action == 'finalize':
        # Build index and compute center after chunked upload
        loop = asyncio.get_event_loop()
        logger.info(f"Finalizing: building index for {len(backend.memories)} memories...")
        await loop.run_in_executor(None, backend.build_index)
        logger.info("Computing center...")
        await loop.run_in_executor(None, backend.compute_center)
        logger.info(f"Finalized! Center computed: {backend.center is not None}")
        return {
            'success': True,
            'total': len(backend.memories),
            'center_computed': backend.center is not None
        }
    
    elif action == 'search':
        # Search for similar memories
        results = backend.search(
            query=message.get('query', ''),
            k=message.get('k', 10),
            threshold=message.get('threshold', 0.1)
        )
        return {'results': results}
    
    elif action == 'respond':
        # Generate response
        result = backend.respond(
            query=message.get('query', ''),
            k=message.get('k', 10)
        )
        return result
    
    elif action == 'compute_center':
        backend.compute_center()
        mag = float(np.linalg.norm(backend.center)) if backend.center is not None else 0
        return {'success': True, 'magnitude': mag}
    
    elif action == 'stats':
        return backend.get_stats()
    
    elif action == 'clear':
        count = backend.clear()
        return {'success': True, 'cleared': count}
    
    elif action == 'ping':
        return {'pong': True, **backend.get_stats()}
    
    else:
        return {'error': f'Unknown action: {action}'}


async def websocket_handler(websocket, path=None):
    """Handle WebSocket connections"""
    logger.info(f"Client connected")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_id = data.get('_id')  # Capture the message ID
                action = data.get('action', 'unknown')
                logger.info(f"Received: {action} (id: {msg_id})")
                
                response = await handle_message(websocket, data)
                if msg_id is not None:
                    response['_id'] = msg_id  # Echo it back!
                
                logger.info(f"Responding: {action} (id: {msg_id})")
                await websocket.send(json.dumps(response))
            except json.JSONDecodeError:
                await websocket.send(json.dumps({'error': 'Invalid JSON'}))
            except Exception as e:
                logger.error(f"Error: {e}")
                await websocket.send(json.dumps({'error': str(e)}))
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected")


async def main():
    """Main entry point"""
    # Pre-load model
    logger.info("Starting Xorzo GPU Backend...")
    backend.load_model()
    
    # Start WebSocket server
    host = 'localhost'
    port = 8765
    
    logger.info(f"Starting WebSocket server on ws://{host}:{port}")
    
    async with websockets.serve(websocket_handler, host, port):
        logger.info("Server running! Waiting for connections...")
        logger.info(f"Stats: {backend.get_stats()}")
        await asyncio.Future()  # Run forever


if __name__ == '__main__':
    asyncio.run(main())
