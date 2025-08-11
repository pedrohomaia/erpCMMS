

# ERP–CMMS Data Sync

Integração de Ordens de Serviço (OS) entre um ERP e um CMMS usando **mocks em FastAPI** e script de sincronização em Python.

## 📌 Visão Geral
Este projeto simula:
- Um **ERP mock** que expõe ordens de serviço.
- Um **CMMS mock** que recebe/atualiza ordens.
- Um **script de sincronização** com idempotência, retries e log em SQLite.

## 📂 Estrutura

erpCMMS/
├─ app/ # APIs mock ERP e CMMS
├─ sync/ # Script de sincronização
├─ docs/ # Documentação OpenAPI exportada
├─ requirements.txt
├─ .env.example
└─ README.md
