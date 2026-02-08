#!/usr/bin/env python3
"""
Script para iniciar o servidor da aplicação AI Content Generator.
Sobe a API FastAPI com o frontend integrado.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
