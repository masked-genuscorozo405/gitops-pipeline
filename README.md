# GitOps Pipeline

![CI](https://github.com/Vinicius-Costa14/gitops-pipeline/actions/workflows/ci.yml/badge.svg)
![CD](https://github.com/Vinicius-Costa14/gitops-pipeline/actions/workflows/cd.yml/badge.svg)
![Security](https://github.com/Vinicius-Costa14/gitops-pipeline/actions/workflows/security-scan.yml/badge.svg)

![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat&logo=kubernetes&logoColor=white)
![ArgoCD](https://img.shields.io/badge/ArgoCD-EF7B4D?style=flat&logo=argo&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=github-actions&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)

Pipeline completo de **GitOps** com **GitHub Actions** para CI e **ArgoCD** para CD, deployando em **Kubernetes** com **Kustomize**.

---

## Diagrama do Pipeline

```
                         GitOps Pipeline
  ================================================================

  Developer        CI (GitHub Actions)              CD (ArgoCD)
  --------         -------------------              -----------

  [Code Push] ---> [Lint + Test] ---> [Build Image]
                                           |
                                    [Push to GHCR]
                                           |
                                  [Update Manifest]
                                           |
                                    [Git Commit] -----> [ArgoCD Detect]
                                                              |
                                                        [Sync to K8s]
                                                              |
                                                    [Staging] ---> [Production]

  ================================================================

  Fluxo detalhado:

  1. Push na main       -->  CI roda lint, testes, build
  2. Image no GHCR      -->  Tag com SHA do commit
  3. Manifest atualizado -->  kustomization.yaml com nova tag
  4. Commit automatico   -->  Dispara o CD pipeline
  5. ArgoCD detecta      -->  Sync automatico para staging
  6. Validacao           -->  kubeconform valida manifests
  7. Production          -->  Deploy com aprovacao manual
```

---

## Como Funciona o GitOps

**GitOps** usa o Git como fonte unica de verdade para a infraestrutura e aplicacoes. Tudo que esta no repositorio e o estado desejado do cluster.

### Principios aplicados neste projeto:

1. **Declarativo**: Todos os recursos Kubernetes sao definidos em YAML
2. **Versionado**: Cada mudanca e um commit no Git com historico completo
3. **Automatizado**: CI atualiza manifests, ArgoCD aplica no cluster
4. **Auto-healing**: ArgoCD corrige drift entre o cluster e o Git

### Diferenca do CI/CD tradicional:

| Tradicional | GitOps |
|-------------|--------|
| CI faz deploy direto no cluster | CI apenas atualiza manifests no Git |
| Credenciais do cluster no CI | Apenas ArgoCD tem acesso ao cluster |
| Estado do deploy e opaco | Git e a fonte de verdade |
| Rollback manual | Rollback = `git revert` |

---

## Workflows

### CI Pipeline (`ci.yml`)

Disparado em push na `main` (exceto mudancas em `k8s/`):

| Job | Descricao |
|-----|-----------|
| **lint** | flake8, black, isort para qualidade de codigo |
| **test** | pytest com coverage (matrix: Python 3.11 + 3.12) |
| **build-and-push** | Build multi-arch, push para GHCR, atualiza manifest |

### CD Pipeline (`cd.yml`)

Disparado por mudancas no diretorio `k8s/`:

| Job | Descricao |
|-----|-----------|
| **validate-manifests** | kubeconform valida base, staging e production |
| **diff-manifests** | Mostra o diff dos manifests renderizados |
| **sync-argocd** | Documenta sync do ArgoCD (auto-sync habilitado) |

### Security Scan (`security-scan.yml`)

Disparado em push, PR e semanalmente (segunda 06:00 UTC):

| Job | Descricao |
|-----|-----------|
| **trivy-image-scan** | Scan de vulnerabilidades na imagem Docker |
| **trivy-config-scan** | Scan de configuracoes IaC (Dockerfile, K8s manifests) |
| **dependency-audit** | pip-audit + safety para dependencias Python |

### Release (`release.yml`)

Disparado por tags `v*.*.*`:

| Job | Descricao |
|-----|-----------|
| **release-image** | Build e push da imagem com tag semantica |
| **create-release** | Cria GitHub Release com changelog automatico |

---

## Estrutura Kustomize

O projeto usa **Kustomize** para gerenciar configuracoes por ambiente:

```
k8s/
  base/                    # Configuracao base (compartilhada)
    deployment.yaml        # Deploy com probes, security context
    service.yaml           # ClusterIP service
    ingress.yaml           # Ingress nginx
    hpa.yaml               # HorizontalPodAutoscaler
    kustomization.yaml     # Imagem + labels comuns
  overlays/
    staging/               # Customizacoes para staging
      kustomization.yaml   # Namespace: gitops-pipeline-staging
      patch-replicas.yaml  # 1 replica
    production/            # Customizacoes para producao
      kustomization.yaml   # Namespace: gitops-pipeline-production
      patch-replicas.yaml  # 3 replicas
      patch-resources.yaml # Mais CPU/memoria
```

### Renderizar manifests:

```bash
# Staging
kustomize build k8s/overlays/staging

# Production
kustomize build k8s/overlays/production
```

---

## Como Configurar

### Pre-requisitos

- Cluster Kubernetes (K3s, EKS, GKE, etc.)
- ArgoCD instalado no cluster
- Docker / Podman
- `kubectl` e `kustomize` CLI

### 1. Fork e clone

```bash
git clone https://github.com/Vinicius-Costa14/gitops-pipeline.git
cd gitops-pipeline
```

### 2. Secrets do GitHub

Configure no repositorio em **Settings > Secrets and variables > Actions**:

| Secret | Descricao |
|--------|-----------|
| `GITHUB_TOKEN` | Automatico - usado para push no GHCR |

> O `GITHUB_TOKEN` ja e fornecido automaticamente pelo GitHub Actions. Para o ArgoCD, as credenciais ficam no cluster, nao no CI.

### 3. Instalar ArgoCD

```bash
chmod +x scripts/setup-argocd.sh
./scripts/setup-argocd.sh
```

### 4. Testar localmente

```bash
cd app
pip install -r requirements.txt
python main.py

# Testes
pip install pytest
pytest tests/ -v
```

### 5. Build Docker local

```bash
docker build -t gitops-pipeline:local ./app
docker run -p 8080:8080 gitops-pipeline:local
curl http://localhost:8080/health
```

---

## Estrutura do Projeto

```
gitops-pipeline/
├── .github/workflows/
│   ├── ci.yml                 # CI: lint, test, build, push
│   ├── cd.yml                 # CD: validate, sync ArgoCD
│   ├── security-scan.yml      # Trivy + pip-audit
│   └── release.yml            # Semantic release
├── app/
│   ├── main.py                # Flask API
│   ├── tests/test_main.py     # Testes unitarios
│   ├── requirements.txt       # Dependencias Python
│   └── Dockerfile             # Multi-stage build
├── k8s/
│   ├── base/                  # Manifests base
│   └── overlays/              # Staging + Production
├── argocd/
│   ├── application.yaml       # ArgoCD Applications
│   └── project.yaml           # ArgoCD AppProject + RBAC
├── scripts/
│   ├── update-image-tag.sh    # Atualiza tag da imagem
│   └── setup-argocd.sh        # Instala ArgoCD
└── README.md
```

---

## Endpoints da API

| Endpoint | Descricao |
|----------|-----------|
| `GET /` | Informacoes da aplicacao |
| `GET /health` | Health check (liveness) |
| `GET /ready` | Readiness check |
| `GET /version` | Versao, commit, data do build |
| `GET /metrics` | Uptime e contagem de requests |

---

## Tecnologias

- **Python 3.12** + Flask - API REST
- **GitHub Actions** - CI/CD pipelines
- **ArgoCD** - GitOps continuous delivery
- **Kubernetes** - Orquestracao de containers
- **Kustomize** - Gerenciamento de configuracao
- **Docker** - Containerizacao (multi-stage build)
- **GHCR** - Container registry
- **Trivy** - Scan de seguranca
- **kubeconform** - Validacao de manifests

### Resultados e Impacto

- **Zero deploys manuais** — CI/CD automatizado elimina erros de deploy e garante consistência
- **Rastreabilidade total** — Cada mudança em produção é rastreável via Git, facilitando auditorias
- **Rollback instantâneo** — Reversão de deploy em segundos via Git revert, sem downtime
- **Ambientes consistentes** — Kustomize garante que staging e produção sejam idênticos
- **Velocidade de entrega** — De commit a produção em minutos, não em dias
