TITLE:
Supplier Invoice Matching Automation - Solution Architecture (Non-production)

USERS / CLIENTS:
Admin Users
AP Users
Web UI

IDENTITY & ENTRY POINTS: (e.g. Azure AD, App Gateway)
Azure AD (Entra ID)
App Gateway

APPLICATION SERVICES:
Notification Service
Azure Function
Azure Service Bus
Ingestion Service
Matching Service
APIM
Web UI

AI SERVICES:
Azure Document Intelligence
Azure OpenAI

DATA STORES:
Azure Blob Storage
Azure PostgreSQL

INTEGRATION / MESSAGING:
Azure Service Bus
AP Shared Mailbox (Graph API)
SendGrid

EXTERNAL / ENTERPRISE SYSTEMS:
SAP S/4HANA
AP Shared Mailbox (Graph API)
SendGrid

SUPPORTING SERVICES: (monitoring, CI/CD, secrets)
Datadog
GitHub Actions
Key Vault
Azure Monitor

CONNECTIONS: one line per arrow -> source -> target | label (protocol / auth / purpose)
Azure Blob Storage -> Azure Function | Managed Identity
Azure Function -> Azure Service Bus | invoice received
Azure Service Bus -> Ingestion Service | queue
Ingestion Service -> Matching Service | extracted invoice
Ingestion Service -> Web UI | REST
Matching Service -> Azure PostgreSQL | match results
APIM -> Azure Document Intelligence | extract
APIM -> Azure OpenAI | normalise lines
APIM -> SAP S/4HANA | PO/GR via APIM
Web UI -> APIM | HTTPS/443 Managed Identity
App Gateway -> Web UI | HTTPS/443
Azure AD (Entra ID) -> App Gateway | OAuth 2.0
Admin Users -> App Gateway | HTTPS/443 AD/SSO
AP Users -> App Gateway | HTTPS/443 AD/SSO MFA
AP Shared Mailbox (Graph API) -> Notification Service | Graph API poll
Notification Service -> SendGrid | (SMTP/587)
SendGrid -> AP Shared Mailbox (Graph API) | SMTP/587

ENVIRONMENT NOTES: (subscription, non-production, network boundaries)
Non-production Subscription (labelled "Non-production Subscription")
Shared AKS Non-prod (dashed area; contains Notification Service)
Shared Services Subscription (contains Azure AD (Entra ID) and App Gateway)
Azure AI Landing Zone (dashed area containing APIM, Azure Document Intelligence, Azure OpenAI)
On-Premise boundary (contains Admin Users, AP Users, SAP S/4HANA)
Data Stores and Integration & Eventing components are inside the Non-production Subscription boundary
Supporting Services (Datadog, GitHub Actions, Key Vault, Azure Monitor) are shown as external supporting services outside the primary subscription boundaries