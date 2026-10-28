TITLE:
Customer Quote Assistant - Solution Architecture (Non-production)

USERS / CLIENTS:
Inside Sales Users
Admin Users

IDENTITY & ENTRY POINTS: (e.g. Azure AD, App Gateway)
Azure AD (Entra ID)
App Gateway

APPLICATION SERVICES:
Web UI
RFQ Processing Service
Matching Service
APIM
Azure Function (Catalog Loader)

AI SERVICES:
Azure OpenAI
Azure AI Search

DATA STORES:
Azure Blob Storage
Azure Cosmos DB

INTEGRATION / MESSAGING:
Azure Event Grid

EXTERNAL / ENTERPRISE SYSTEMS:
Sales Mailbox (Graph API)
PIM Catalog Export
Salesforce CPQ (MVP2)

SUPPORTING SERVICES: (monitoring, CI/CD, secrets)
Datadog
GitHub Actions
Key Vault
Azure Monitor

CONNECTIONS: one line per arrow -> source -> target | label (protocol / auth / purpose)
Inside Sales Users -> App Gateway | HTTPS/443 AD/SSO
Admin Users -> App Gateway | HTTPS/443 AD/SSO
Azure AD (Entra ID) -> App Gateway | HTTPS/443 AD/SSO OAuth 2.0
App Gateway -> Web UI | HTTPS/443
Web UI -> RFQ Processing Service | REST
RFQ Processing Service -> Matching Service | attachments / extracted lines
RFQ Processing Service -> Sales Mailbox (Graph API) | Graph API
RFQ Processing Service -> Azure Event Grid | (arrow present to Event Grid; purpose: integration/eventing)
Azure Blob Storage -> RFQ Processing Service | attachments (storage)
Azure Cosmos DB -> Matching Service | draft quotes
Matching Service -> APIM | search
APIM -> Azure OpenAI | line extraction
APIM -> Azure AI Search | hybrid search
Matching Service -> Azure Event Grid | HTTPS/443 Managed Identity
Azure Event Grid -> Azure Function (Catalog Loader) | trigger
Azure Function (Catalog Loader) -> Azure AI Search | nightly index
PIM Catalog Export -> Azure Event Grid | file dropped
Azure Event Grid -> Salesforce CPQ (MVP2) | quote create

ENVIRONMENT NOTES: (subscription, non-production, network boundaries)
Non-production Subscription (boundary shown)
Shared Services Subscription (contains Azure AD (Entra ID) and App Gateway)
Shared AKS Non-prod area contains Web UI, RFQ Processing Service and Matching Service
Azure AI Landing Zone contains APIM, Azure OpenAI, Azure AI Search
Integration & Eventing area contains Azure Event Grid and Azure Function (Catalog Loader)
External / Enterprise Systems are outside the subscription boundary
Supporting Services are shown separately (Datadog, GitHub Actions, Key Vault, Azure Monitor)