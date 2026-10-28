TITLE:
Non-production Subscription

USERS / CLIENTS:
Admin Users
Wesco Users
Web UI

IDENTITY & ENTRY POINTS: (e.g. Azure AD, App Gateway)
Active Directory
AD/SSO (label: https/443 AD/SSO)
App Gateway
APIM (Shared)
APIM (in Azure AI Landing Zone)

APPLICATION SERVICES:
Web UI
Processing Service
Notification Service
File Service
Shared AKS Non-prod
App Gateway
Azure Function

AI SERVICES:
Azure OpenAI
Azure AI Foundry
Azure Foundry Agent Service
Azure Document Intelligence

DATA STORES:
Delta Lake EUDM/IAP
Azure PostgreSQL
Azure Blob Storage
File Service (listed as an application service but also a datastore)

INTEGRATION / MESSAGING:
Azure Service bus
Azure Event Grid
APIM (Shared)
APIM (in Azure AI Landing Zone)
Cloud Interconnect (to Google Cloud Non-Prod)
SendGrid

EXTERNAL / ENTERPRISE SYSTEMS:
On-Premise
Shared Services Subscription
Active Directory (in Shared Services Subscription)
SendGrid
Google Cloud Non-Prod
Google Vertex AI

SUPPORTING SERVICES: (monitoring, CI/CD, secrets)
DATADOG
GitHub Repo/Actions
Keyvault
Azure Devops
Azure Monitor

CONNECTIONS: one line per arrow -> source -> target | label (protocol / auth / purpose)
Admin Users -> Active Directory | https/443 AD/SSO
Wesco Users -> Active Directory | https/443 AD/SSO
Active Directory -> App Gateway | https/443 AD/SSO
App Gateway -> Web UI | (implicit HTTP/HTTPS for user traffic)
Web UI -> Processing Service | (internal HTTP, arrow present between Web UI and Processing Service)
Processing Service -> File Service | (internal HTTP, arrow present)
Processing Service -> Notification Service | (internal HTTP, arrow present)
Processing Service -> Shared AKS Non-prod | (internal cluster calls)
Processing Service -> APIM (Shared) | HTTPS/443 Managed Identity
APIM (Shared) -> Cloud Interconnect | HTTPS/443 Key-based auth
APIM (Shared) -> Google Vertex AI (via Cloud Interconnect) | HTTPS/443 Key-based auth
APIM (in Azure AI Landing Zone) -> Azure OpenAI | HTTPS/443 Managed Identity
APIM (in Azure AI Landing Zone) -> Azure Document Intelligence | HTTPS/443 Managed Identity
APIM (in Azure AI Landing Zone) -> Azure AI Foundry | HTTPS/443 Managed Identity
Azure AI Foundry -> Azure Foundry Agent Service | HTTPS/443 Managed Identity
Azure Foundry Agent Service -> Azure Service bus | HTTPS/443 Managed Identity
Azure Service bus -> Azure PostgreSQL | (data flow to persistence)
Azure Service bus -> Azure Blob Storage | (data flow to blob)
Azure Function -> Azure Event Grid | HTTPS/443 Azure AD Managed Identity
Azure Event Grid -> Processing Service | HTTPS/443 Managed Identity
Delta Lake EUDM/IAP -> Processing Service | HTTPS/443 (data access)
Supporting Services (DATADOG, GitHub Repo/Actions, Keyvault, Azure Devops, Azure Monitor) -> various application components | (CI/CD, monitoring, secrets management; labels visible as service names)
On-Premise -> Active Directory | (bidirectional arrow shown between On-Premise and Shared Services Subscription Active Directory)
SendGrid -> Notification Service | SMTP/587 (label visible near SendGrid)
Google Cloud Non-Prod (Google Vertex AI) -> Cloud Interconnect -> APIM (Shared) | HTTPS/443 Key-based auth

ENVIRONMENT NOTES: (subscription, non-production, network boundaries)
Non-production Subscription (main shaded boundary)
Shared Services Subscription (separate dotted boundary containing Active Directory and shared services)
Google Cloud Non-Prod (separate external boundary)
On-Premise (separate boundary)
Network boundaries depicted between On-Premise, Shared Services Subscription, Non-production Subscription, and Google Cloud Non-Prod
Labels indicate non-production environment (Shared AKS Non-prod, Google Cloud Non-Prod) and use of managed identities for inter-service auth where shown.