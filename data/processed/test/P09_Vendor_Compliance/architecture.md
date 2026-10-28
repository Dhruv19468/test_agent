TITLE:
Vendor Onboarding Compliance Screening - Solution Architecture (Non-production)

USERS / CLIENTS:
Supplier Risk Analysts
Compliance Managers

IDENTITY & ENTRY POINTS: (e.g. Azure AD, App Gateway)
Azure AD (Entra ID)
App Gateway

APPLICATION SERVICES:
Web UI
Document Service
Evidence Service
Screening Service
APIM

AI SERVICES:
Azure Document Intelligence

DATA STORES:
Azure Blob Storage (7-yr retention)
Azure PostgreSQL

INTEGRATION / MESSAGING:
Azure Service Bus

EXTERNAL / ENTERPRISE SYSTEMS:
Sanctions Screening API

SUPPORTING SERVICES: (monitoring, CI/CD, secrets)
Datadog
GitHub Actions
Key Vault
Azure Monitor

CONNECTIONS: one line per arrow -> source -> target | label (protocol / auth / purpose)
Supplier Risk Analysts -> App Gateway | HTTPS/443 AD/SSO MFA
Compliance Managers -> App Gateway | HTTPS/443 AD/SSO MFA
Azure AD (Entra ID) -> App Gateway | OAuth 2.0
App Gateway -> Web UI | HTTPS/443
Web UI -> Document Service | upload
Web UI -> Evidence Service | decision
Document Service -> Azure Service Bus | documents ready
Azure Service Bus -> Screening Service | queue
Screening Service -> APIM | screening
APIM -> Azure Document Intelligence | classify + extract
Evidence Service -> Azure Blob Storage (7-yr retention) | documents/evidence PDF
Screening Service -> Azure PostgreSQL | results
APIM -> Azure PostgreSQL | HTTPS/443 key-based auth
Azure PostgreSQL -> Sanctions Screening API | HTTPS/443 key-based auth

ENVIRONMENT NOTES: (subscription, non-production, network boundaries)
On-Premise: Supplier Risk Analysts, Compliance Managers (on-premise boundary shown)
Shared Services Subscription: Azure AD (Entra ID), App Gateway (shared services)
Non-production Subscription: contains Shared AKS Non-prod (Web UI, Document Service, Evidence Service), Azure AI Landing Zone (APIM, Azure Document Intelligence), Integration & Eventing (Azure Service Bus), Data Stores (Azure Blob Storage, Azure PostgreSQL), Screening Service
Supporting Services are shown external to subscription boundary (Datadog, GitHub Actions, Key Vault, Azure Monitor)