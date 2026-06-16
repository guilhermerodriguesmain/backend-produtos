from pydantic import BaseModel, Field


class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=1)
    preco: float = Field(..., gt=0)
    estoque: int = 0
    ativo: bool = True


class ProdutoResponse(ProdutoCreate):
    id: int

    class Config:
        from_attributes = True
        