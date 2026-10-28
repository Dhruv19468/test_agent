TITLE:
Warranty Returns (RMA) Assistant – Solution Architecture (Non-production)

USERS / CLIENTS:
Returns Coordinators
Returns Managers
Policy Admins

IDENTITY & ENTRY POINTS: (e.g. Azure AD, App Gateway)
Azure AD (Entra ID)
App Gateway

APPLICATION SERVICES:
Web UI
Returns Service
Policy Ingestion Service
Notification Service
APIM

AI SERVICES:
Azure Document Intelligence
Azure OpenAI
Azure AI Search

DATA STORES:
Azure PostgreSQL
Azure Blob Storage

INTEGRATION / MESSAGING:
Azure Service Bus

EXTERNAL / ENTERPRISE SYSTEMS:
Returns Mailbox (Graph API)
SAP S/4HANA
SendGrid

SUPPORTING SERVICES: (monitoring, CI/CD, secrets)
Datadog
GitHub Actions
Key Vault
Azure Monitor

CONNECTIONS: one line per arrow -> source -> target | label (protocol / auth / purpose)
Returns Coordinators -> App Gateway | HTTPS/443 AD/SSO
Returns Managers -> App Gateway | HTTPS/443 AD/SSO
Policy Admins -> App Gateway | HTTPS/443 AD/SSO
Azure AD (Entra ID) -> App Gateway | OAuth 2.0
App Gateway -> Web UI | HTTPS/443
Web UI -> Returns Service | REST
Web UI -> Policy Ingestion Service | policy upload
Returns Service -> Azure Service Bus | RMA created
Azure Service Bus -> Notification Service | queue
Returns Service -> APIM | HTTPS/443 Managed Identity
APIM -> Azure OpenAI | recommendation
Policy Ingestion Service -> Returns Mailbox (Graph API) | Graph API
Policy Ingestion Service -> Azure Document Intelligence | layout
Policy Ingestion Service -> Azure AI Search | policy retrieval
Azure Document Intelligence -> Azure AI Search | index chunks
Azure AI Search -> Azure PostgreSQL | decisions
Azure Document Intelligence -> Azure Blob Storage | policy PDFs
Returns Service -> Azure Blob Storage | invoice + RMA
Azure Blob Storage -> SAP S/4HANA | invoice + RMA
Notification Service -> SendGrid | SMTP/587

ENVIRONMENT NOTES: (subscription, non-production, network boundaries)
Shared Services Subscription contains Azure AD (Entra ID) and App Gateway. Non-production Subscription contains Shared AKS Non-prod (Web UI, Returns Service, Policy Ingestion Service, Notification Service), Azure AI Landing Zone (APIM, Azure Document Intelligence, Azure OpenAI, Azure AI Search), Data Stores (Azure PostgreSQL, Azure Blob Storage), and Integration & Eventing (Azure Service Bus). Diagram is explicitly labeled Non-production. Supporting Services (Datadog, GitHub Actions, Key Vault, Azure Monitor) and External / Enterprise Systems (Returns Mailbox (Graph API), SAP S/4HANA, SendGrid) are shown outside the main non-production subscription boundaries.