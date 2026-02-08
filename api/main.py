"""
FastAPI REST API para geração de conteúdo para redes sociais.
Expõe o workflow LangGraph para consumo via frontend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Literal, Optional
from pathlib import Path
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Content Generator API",
    description="API para geração de conteúdo para redes sociais usando agentes IA",
    version="1.0.0"
)

# CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caminho do frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


# ============ Schemas Pydantic ============

class GenerateRequest(BaseModel):
    """Payload para geração de conteúdo"""
    type_post: Literal["carousel", "description", "stories", "video"] = Field(
        ..., description="Tipo do post"
    )
    topic: str = Field(..., min_length=1, max_length=500)
    idea: str = Field(..., min_length=1, max_length=2000)
    tone: Literal[
        "professional", "educational", "confident",
        "friendly", "inspirational", "serious"
    ] = Field(..., description="Tom do conteúdo")
    slides: Optional[int] = Field(None, ge=1, le=20)


class ResearchResponse(BaseModel):
    """Resposta estruturada da pesquisa"""
    summary: str
    key_points: list[str]
    sources: Optional[list[str]] = None
    insights: Optional[list[str]] = None


class FinalReportResponse(BaseModel):
    """Conteúdo gerado final"""
    type_post: str
    title: Optional[str] = None
    texts: list[str]
    caption: Optional[str] = None
    hashtags: Optional[str] = None
    notes: Optional[str] = None


class GenerateResponse(BaseModel):
    """Resposta completa da geração"""
    success: bool = True
    research: Optional[ResearchResponse] = None
    content: Optional[FinalReportResponse] = None
    error: Optional[str] = None


# ============ Endpoints ============

@app.get("/api/health")
async def health_check():
    """Health check da API"""
    return {"status": "ok", "message": "API operacional"}


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest):
    """
    Gera conteúdo para redes sociais com base nos parâmetros informados.
    Executa o workflow de agentes (search + writer).
    """
    try:
        # Import aqui para evitar carregar LangGraph no startup
        from src.graph.workflow import graph

        # Validação: slides obrigatório para carousel
        slides = request.slides
        if request.type_post == "carousel" and not slides:
            slides = 3  # default para carousel

        input_data = {
            "type_post": request.type_post,
            "topic": request.topic.strip(),
            "idea": request.idea.strip(),
            "tone": request.tone,
            "slides": slides,
            "messages": []
        }

        logger.info(f"Iniciando geração: topic={request.topic[:50]}...")

        # Execução síncrona do workflow
        result = graph.invoke(input_data)

        # Extrai resultados
        research = result.get("result_research")
        final_report = result.get("final_report")

        if not final_report:
            logger.warning("Workflow finalizado sem final_report")
            return GenerateResponse(
                success=False,
                research=ResearchResponse(**research.model_dump()) if research else None,
                error="Conteúdo não foi gerado. Tente novamente."
            )

        # Converte para JSON-serializable
        research_response = None
        if research:
            research_response = ResearchResponse(
                summary=research.summary,
                key_points=research.key_points,
                sources=research.sources,
                insights=research.insights
            )

        content_response = FinalReportResponse(
            type_post=final_report.type_post,
            title=final_report.title,
            texts=final_report.texts,
            caption=final_report.caption,
            hashtags=final_report.hashtags,
            notes=final_report.notes
        )

        logger.info("Geração concluída com sucesso")

        return GenerateResponse(
            success=True,
            research=research_response,
            content=content_response
        )

    except Exception as e:
        logger.exception(f"Erro na geração de conteúdo: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar conteúdo: {str(e)}"
        )


# ============ Servir Frontend ============

@app.get("/")
async def serve_frontend():
    """Serve a página principal do frontend"""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Frontend não encontrado")


# Monta arquivos estáticos (CSS, JS)
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
