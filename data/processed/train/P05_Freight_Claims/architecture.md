TITLE:
Freight Damage Claims Automation - Solution Architecture (Non-production)

USERS / CLIENTS:
Claims Specialists
Admin Users
Branch Users

IDENTITY & ENTRY POINTS: (e.g. Azure AD, App Gateway)
Azure AD (Entra ID)
App Gateway

APPLICATION SERVICES:
Web UI (responsive)
Claims Service
Packet Service
APIM
Azure Function

AI SERVICES:
Azure OpenAI (vision)

DATA STORES:
Azure PostgreSQL
Azure Blob Storage

INTEGRATION / MESSAGING:
Azure Service Bus

EXTERNAL / ENTERPRISE SYSTEMS:
TMS API
ERP Sales Order API
SendGrid

SUPPORTING SERVICES: (monitoring, CI/CD, secrets)
Datadog
GitHub Actions
Key Vault
Azure Monitor

CONNECTIONS: one line per arrow -> source -> target | label (protocol / auth / purpose)
Claims Specialists -> App Gateway | HTTPS/443 AD/SSO
Admin Users -> App Gateway | HTTPS/443
Branch Users -> App Gateway | HTTPS/443
Azure AD (Entra ID) -> App Gateway | OAuth 2.0
App Gateway -> Web UI (responsive) | HTTPS/443
Web UI (responsive) -> Claims Service | REST
Claims Service -> Azure PostgreSQL | claims
Claims Service -> Azure Blob Storage | photos
Claims Service -> APIM | HTTPS/443 Managed Identity
Claims Service -> Azure Service Bus | claim submitted
APIM -> Azure OpenAI (vision) | damage description
Packet Service -> Azure Blob Storage | packet PDF
Azure OpenAI (vision) -> Azure Function | send email
Azure Service Bus -> TMS API | unit/equipment lookup
Azure Service Bus -> ERP Sales Order API | (integration / queue)
Azure Function -> SendGrid | SMTP/587

ENVIRONMENT NOTES: (subscription, non-production, network boundaries)
- Diagram represents Non-production Subscription (blue boundary) with components deployed in a Shared AKS Non-prod and Azure AI Landing Zone.
- App Gateway and Azure AD (Entra ID) are shown in a Shared Services Subscription (separate dashed boundary).
- Users are shown as On-Premise.
- External / Enterprise Systems and Supporting Services are shown outside the Non-production Subscription boundaries.