from typing import Dict, List, Optional, Any
from fastapi.responses import JSONResponse
from fastapi import Response, Path, Query, Header, FastAPI, HTTPException, status, Depends
from fastapi import HTTPException
from pydantic import BaseModel
import httpx
from decouple import config
from fastapi import Body


# Configuração da chave de acesso
ASAAS_API_KEY = config('ASAAS_API_KEY', default=None)

app = FastAPI(
    title='FLASHAPI SISTEMA DE PAGAMENTOS',
    version='0.0.1',
    description='FlashApi Splits'
)


# Modelo de Split de pagamento
class SplitPagamento(BaseModel):
    id: str
    payment_id: str
    recipient_id: str
    amount: float
    percentage: float
    status: str


# Função para calcular a comissão do page_split de pagamento
def calculate_commission(amount: float, recipient_type: str, is_recurring: bool) -> float:
    if recipient_type == 'Parceiro':
        if is_recurring:
            return amount * 0.10  # 10% de recorrência
        else:
            return amount * 0.30  # 30% no ato da assinatura
    elif recipient_type == 'Colaborador':
        if is_recurring:
            return amount * 0.10  # 10% de recorrência
        else:
            return amount * 0.20  # 20% no ato da assinatura
    elif recipient_type == 'Consultor':
        if is_recurring:
            return amount * 0.10  # 10% de recorrência
        else:
            return amount * 0.10  # 10% no ato da assinatura
    else:
        raise ValueError("Tipo de receptor desconhecido")


# Função para fazer requisições à API do Asaas para splits de pagamento
async def fetch_payment_splits(payment_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'https://www.asaas.com/api/v3/payments/{payment_id}/splits',
            headers={'access_token': api_key}
        )
        response.raise_for_status()
        return response.json()


# Função para fazer requisições à API do Asaas para splits de pagamento
async def fetch_payment_splits(payment_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'https://www.asaas.com/api/v3/payments/{payment_id}/splits',
            headers={'access_token': api_key}
        )
        response.raise_for_status()
        return response.json()


@app.get('/payments/{payment_id}/splits',
         description='Retorna todos os splits de pagamento de um pagamento ou uma lista vazia.',
         summary='Retorna todos os splits de pagamento de um pagamento',
         response_model=List[SplitPagamento],
         response_description='Splits de pagamento encontrados com sucesso.')
async def get_payment_splits(payment_id: str = Path(default=None, title='ID do pagamento', description='ID do pagamento')):
    payment_splits = await fetch_payment_splits(payment_id)
    return payment_splits.get('data', [])


@app.get('/payments/{payment_id}/splits/{split_id}')
async def get_payment_split(payment_id: str = Path(default=None, title='ID do pagamento', description='ID do pagamento'),
                             split_id: str = Path(default=None, title='ID do page_split de pagamento', description='ID do page_split de pagamento')):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'https://www.asaas.com/api/v3/payments/{payment_id}/splits/{split_id}',
            headers={'access_token': api_key}
        )
        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='Split de pagamento não encontrado.'
            )
        response.raise_for_status()
        return response.json()


@app.post('/payments/{payment_id}/splits', status_code=status.HTTP_201_CREATED, response_model=SplitPagamento)
async def post_payment_split(payment_id: str = Path(default=None, title='ID do pagamento', description='ID do pagamento'),
                             split: SplitPagamento = Body(...)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'https://www.asaas.com/api/v3/payments/{payment_id}/splits',
            json=split.dict(),
            headers={'access_token': api_key}
        )
        response.raise_for_status()
        return response.json()


@app.put('/payments/{payment_id}/splits/{split_id}')
async def put_payment_split(payment_id: str = Path(default=None, title='ID do pagamento', description='ID do pagamento'),
                            split_id: str = Path(default=None, title='ID do page_split de pagamento', description='ID do page_split de pagamento'),
                            split: SplitPagamento = Body(...)):
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f'https://www.asaas.com/api/v3/payments/{payment_id}/splits/{split_id}',
            json=split.dict(),
            headers={'access_token': api_key}
        )
        if response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Não existe um page_split de pagamento com id {split_id}')
        response.raise_for_status()
        return response.json()


@app.delete('/payments/{payment_id}/splits/{split_id}')
async def delete_payment_split(payment_id: str = Path(default=None, title='ID do pagamento', description='ID do pagamento'),
                                split_id: str = Path(default=None, title='ID do page_split de pagamento', description='ID do page_split de pagamento')):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f'https://www.asaas.com/api/v3/payments/{payment_id}/splits/{split_id}',
            headers={'access_token': api_key}
        )
        if response.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Não existe um page_split de pagamento com id {split_id}')
        return Response(status_code=status.HTTP_204_NO_CONTENT)
