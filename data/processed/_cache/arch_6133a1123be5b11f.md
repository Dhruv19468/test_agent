TITLE:
Product Data Enrichment - Solution Architecture (Non-production)

USERS / CLIENTS:
Content Users
Admin Users

IDENTITY & ENTRY POINTS: (e.g. Azure AD, App Gateway)
Azure AD (Entra ID)
App Gateway

APPLICATION SERVICES:
Web UI
Extraction Service
Export Service
APIM
Azure Function

AI SERVICES:
Azure Document Intelligence
Azure OpenAI

DATA STORES:
Azure SQL Database
Azure Blob Storage

INTEGRATION / MESSAGING:
Azure Function

EXTERNAL / ENTERPRISE SYSTEMS:
PIM (CSV import)

SUPPORTING SERVICES: (monitoring, CI/CD, secrets)
Datadog
GitHub Actions
Key Vault

CONNECTIONS: one line per arrow -> source -> target | label (protocol / auth / purpose)
Content Users -> App Gateway | HTTPS/443 AD/SSO
Admin Users -> App Gateway | HTTPS/443 AD/SSO
Azure AD (Entra ID) -> App Gateway | OAuth 2.0
App Gateway -> Web UI | HTTPS/443
Web UI -> Extraction Service | REST
Web UI -> Export Service | approve export
Extraction Service -> APIM | HTTPS/443 Managed Identity
Extraction Service -> Azure SQL Database | attributes
Extraction Service -> Azure Blob Storage | PDFs
APIM -> Azure Document Intelligence | layout
APIM -> Azure OpenAI | attribute mapping
Export Service -> Azure Function | build CSV
Azure Function -> PIM (CSV import) | SFTP drop

ENVIRONMENT NOTES: (subscription, non-production, network boundaries)
Diagram title and borders indicate "Non-production". App Gateway and Azure AD (Entra ID) are shown in "Shared Services Subscription". Web UI, Extraction Service, Export Service and Data Stores are inside the "Non-production Subscription" (Shared AKS Non-prod contains Web UI; Azure AI Landing Zone contains APIM and AI services). External / Enterprise Systems (PIM) and Supporting Services are shown outside the Non-production subscription boundary.