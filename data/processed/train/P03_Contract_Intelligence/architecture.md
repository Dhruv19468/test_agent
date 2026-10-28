TITLE:
Contract Intelligence – Solution Architecture (Non-production)

USERS / CLIENTS:
Legal Users
Customer Users
Admin Users

IDENTITY & ENTRY POINTS: (e.g. Azure AD, App Gateway)
Azure AD (Entra ID)
App Gateway

APPLICATION SERVICES:
Web UI
File Service
Processing Service
Notification Service
Azure Function

AI SERVICES:
APIM
Azure Document Intelligence
Azure OpenAI

DATA STORES:
Azure Blob Storage
Azure PostgreSQL

INTEGRATION / MESSAGING:
Azure Service Bus

EXTERNAL / ENTERPRISE SYSTEMS:
SendGrid

SUPPORTING SERVICES: (monitoring, CI/CD, secrets)
Datadog
GitHub Actions
Key Vault
Azure DevOps

CONNECTIONS: one line per arrow -> source -> target | label (protocol / auth / purpose)
Legal Users -> Azure AD (Entra ID) | HTTPS/443 AD/SSO
Customer Users -> Azure AD (Entra ID) | HTTPS/443 AD/SSO
Admin Users -> Azure AD (Entra ID) | HTTPS/443 AD/SSO
Azure AD (Entra ID) -> App Gateway | OAuth 2.0
App Gateway -> Web UI | HTTPS/443
Web UI -> File Service | upload
File Service -> Azure Service Bus | contract uploaded
File Service -> Azure Blob Storage | (visible connection, no label)
Azure Service Bus -> Processing Service | queue
Processing Service -> Azure Function | metadata, score/azure event
Azure Function -> Notification Service | notify
Processing Service -> APIM | HTTPS/443 Managed Identity
APIM -> Azure Document Intelligence | OCR/layout
APIM -> Azure OpenAI | clauses + RAG
Notification Service -> SendGrid | SMTP/587
Azure PostgreSQL -> Processing Service | (visible connection, no label)
Azure PostgreSQL -> Azure Function | (visible connection, no label)

ENVIRONMENT NOTES: (subscription, non-production, network boundaries)
Components are deployed in a Non-production Subscription. Azure AD and App Gateway are in a Shared Services Subscription. Web UI, File Service, Processing Service, Notification Service, Azure Service Bus, Azure Function, Azure Blob Storage, and Azure PostgreSQL are inside the Non-production Subscription boundary. APIM, Azure Document Intelligence, and Azure OpenAI are shown in an Azure AI Landing Zone within the Non-production environment. Supporting Services (Datadog, GitHub Actions, Key Vault, Azure DevOps) are shown externally as supporting services. External system SendGrid is outside the subscription boundary.