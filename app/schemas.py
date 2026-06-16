from pydantic import BaseModel, Field, ConfigDict


class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=1)
    preco: float = Field(..., gt=0)
    estoque: int = 0
    ativo: bool = True


class ProdutoResponse(ProdutoCreate):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
        