TITLE:
Supplier Rebate Claim Validation - Solution Architecture (Non-production)

USERS / CLIENTS:
Rebate Analysts
Finance Managers

IDENTITY & ENTRY POINTS: (e.g. Azure AD, App Gateway)
Azure AD (Entra ID)
App Gateway

APPLICATION SERVICES:
Web UI
Agreement Service
Calculation Service
Azure Function (Batch Scheduler)
APIM

AI SERVICES:
Azure Document Intelligence
Azure OpenAI

DATA STORES:
Azure Blob Storage
Azure PostgreSQL
Delta Lake EUDM/IAP (Databricks SQL)

INTEGRATION / MESSAGING:
Azure Function (Batch Scheduler)
APIM

EXTERNAL / ENTERPRISE SYSTEMS:
Delta Lake EUDM/IAP (Databricks SQL)

SUPPORTING SERVICES: (monitoring, CI/CD, secrets)
Datadog
GitHub Actions
Key Vault
Azure Monitor

CONNECTIONS: one line per arrow -> source -> target | label (protocol / auth / purpose)
Rebate Analysts -> App Gateway | HTTPS/443 AD/SSO  
Finance Managers -> App Gateway | HTTPS/443 AD/SSO  
Azure AD (Entra ID) -> App Gateway | HTTPS/443 AD/SSO / OAuth 2.0  
App Gateway -> Web UI | HTTPS/443  
Web UI -> Agreement Service | REST  
Web UI -> Calculation Service | run calculation  
Azure Function (Batch Scheduler) -> Agreement Service | month-end batch  
Agreement Service -> Azure Blob Storage | agreements  
Agreement Service -> Azure PostgreSQL | confirmed terms  
Calculation Service -> Azure PostgreSQL | results  
Calculation Service -> Delta Lake EUDM/IAP (Databricks SQL) | HTTPS/443 OAuth 2.0  
Agreement Service -> APIM | HTTPS/443 Managed Identity  
APIM -> Azure Document Intelligence | layout  
APIM -> Azure OpenAI | term extraction

ENVIRONMENT NOTES: (subscription, non-production, network boundaries)
Solution labeled as Non-production. Components are organized into: On-Premise (Rebate Analysts, Finance Managers), Shared Services Subscription (Azure AD (Entra ID), App Gateway), Non-production Subscription (Shared AKS Non-prod with Web UI, Agreement Service, Calculation Service; Integration & Eventing with Azure Function (Batch Scheduler); Data Stores), and Azure AI Landing Zone (APIM, Azure Document Intelligence, Azure OpenAI). Supporting services (Datadog, GitHub Actions, Key Vault, Azure Monitor) are shown in a separate Supporting Services boundary. Network/tenant boundaries are indicated by dashed boxes for On-Premise, Shared Services Subscription, Non-production Subscription, Azure AI Landing Zone, and Supporting Services.