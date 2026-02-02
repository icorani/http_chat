#!/usr/bin/env python3
"""
Запуск сервера
"""
import os
import uvicorn

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "6088"))
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True
    )