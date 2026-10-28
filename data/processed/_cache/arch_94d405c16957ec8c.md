TITLE:
Email Purchase Order Entry Automation - Solution Architecture (Non-production)

USERS / CLIENTS:
CSR Users
Admin Users

IDENTITY & ENTRY POINTS: (e.g. Azure AD, App Gateway)
Azure AD (Entra ID)
App Gateway

APPLICATION SERVICES:
APIM
Order Extraction Service
Order Creation Service
Web UI (Review Queue)

AI SERVICES:
Azure Document Intelligence
Azure OpenAI
Azure AI Search

DATA STORES:
Azure Blob Storage
Azure Cosmos DB

INTEGRATION / MESSAGING:
Azure Event Grid
Azure Service Bus

EXTERNAL / ENTERPRISE SYSTEMS:
Branch Mailboxes (Graph API)
SAP S/4HANA

SUPPORTING SERVICES: (monitoring, CI/CD, secrets)
Datadog
GitHub Actions
Key Vault
Azure Monitor

CONNECTIONS: one line per arrow -> source -> target | label (protocol / auth / purpose)
CSR Users -> App Gateway | HTTPS/443 AD/SSO
Admin Users -> App Gateway | HTTPS/443 AD/SSO
Azure AD (Entra ID) -> App Gateway | HTTPS/443 AD/SSO / OAuth 2.0
App Gateway -> APIM | HTTPS/443
APIM -> Azure Document Intelligence | extract
APIM -> Azure OpenAI | map fields
APIM -> Azure AI Search | item search
APIM -> Azure Blob Storage | HTTPS/443 Managed Identity
Branch Mailboxes (Graph API) -> Azure Event Grid | new mail
Azure Event Grid -> Azure Service Bus | event
Azure Service Bus -> Order Extraction Service | queue
Order Extraction Service -> Azure Blob Storage | email copy
Order Extraction Service -> Web UI (Review Queue) | email copy
Order Extraction Service -> Order Creation Service | extracted PO
Web UI (Review Queue) -> Azure Cosmos DB | queue
Order Creation Service -> Azure Cosmos DB | drafts
Order Creation Service -> SAP S/4HANA | validate + draft order via APIM

ENVIRONMENT NOTES: (subscription, non-production, network boundaries)
Non-production Subscription (contains Azure AI Landing Zone, Shared AKS Non-prod, Data Stores, Integration & Eventing)
Shared Services Subscription (contains Azure AD (Entra ID) and App Gateway)
On-Premise (contains CSR Users and Admin Users)
Shared AKS Non-prod (label visible around Order Extraction Service, Order Creation Service, Web UI (Review Queue))
Azure AI Landing Zone (contains APIM, Azure Document Intelligence, Azure OpenAI, Azure AI Search)
External / Enterprise Systems and Supporting Services are outside the Non-production Subscription boundary as shown.