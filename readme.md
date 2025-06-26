# Project - Criação Automatizada de AWS Lambda Layers

## 👨‍💻 Projeto desenvolvido por: 
[Rafael Torres Nantes](https://github.com/rafael-torres-nantes)

## Índice

* 📚 Contextualização do projeto
* 🛠️ Tecnologias/Ferramentas utilizadas
* 🖥️ Funcionamento do sistema
   * 🧩 Controlador de Build
   * 🔑 Gerenciamento de Credenciais AWS
* 🔀 Arquitetura da aplicação
* 📁 Estrutura do projeto
* 📌 Como executar o projeto
* ⚙️ Configuração
* 🕵️ Dificuldades Encontradas

## 📚 Contextualização do projeto

O projeto tem como objetivo **automatizar a criação e publicação de AWS Lambda Layers** a partir de um arquivo requirements.txt. O sistema foi desenvolvido para simplificar o processo de empacotamento de dependências Python e sua publicação na AWS, eliminando a necessidade de executar comandos manuais complexos. A solução é especialmente útil para desenvolvedores que trabalham com múltiplas funções Lambda que compartilham as mesmas dependências.

## 🛠️ Tecnologias/Ferramentas utilizadas

[<img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white">](https://www.python.org/)
[<img src="https://img.shields.io/badge/Visual_Studio_Code-007ACC?logo=visual-studio-code&logoColor=white">](https://code.visualstudio.com/)
[<img src="https://img.shields.io/badge/AWS-Lambda-FF9900?logo=amazonaws&logoColor=white">](https://aws.amazon.com/lambda/)
[<img src="https://img.shields.io/badge/AWS-CLI-FF9900?logo=amazonaws&logoColor=white">](https://aws.amazon.com/cli/)
[<img src="https://img.shields.io/badge/Boto3-0073BB?logo=amazonaws&logoColor=white">](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
[<img src="https://img.shields.io/badge/Python-dotenv-2B5B84?logo=python&logoColor=white">](https://pypi.org/project/python-dotenv/)
[<img src="https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white">](https://github.com/)

## 🖥️ Funcionamento do sistema

### 🧩 Controlador de Build

O núcleo do sistema está no arquivo builder_layer.py, que contém a classe `BuilderLayer`. Esta classe orquestra todo o processo de criação da Layer através de quatro etapas principais:

* **Criação da estrutura**: Gera a estrutura de diretórios necessária (`build/python/`) conforme exigido pela AWS
* **Instalação de dependências**: Utiliza pip para instalar as dependências do requirements.txt com configurações específicas para ambiente Linux
* **Empacotamento**: Cria um arquivo ZIP com a estrutura correta para upload na AWS
* **Publicação**: Utiliza AWS CLI para publicar a Layer na região configurada

### 🔑 Gerenciamento de Credenciais AWS

O sistema utiliza a classe `AWS_SERVICES` do arquivo import_aws_credentials.py para:

* **Carregamento seguro de credenciais**: Importa credenciais do arquivo .env usando python-dotenv
* **Validação de sessão**: Verifica se as credenciais AWS são válidas antes de executar operações
* **Criação de sessão boto3**: Estabelece uma sessão autenticada com a AWS para operações programáticas

## 🔀 Arquitetura da aplicação

O sistema segue uma arquitetura modular simples, onde:

1. **main.py**: Ponto de entrada que configura e inicia o processo
2. **Controller**: `BuilderLayer` gerencia o fluxo de trabalho completo
3. **Utils**: `AWS_SERVICES` fornece funcionalidades de autenticação AWS
4. **Configuração**: Variáveis de ambiente no .env para credenciais sensíveis

## 📁 Estrutura do projeto

A estrutura do projeto é organizada da seguinte maneira:

```
.
├── .env                          # Credenciais AWS (não versionado)
├── .env.example                  # Exemplo de configuração de credenciais
├── .gitignore                    # Arquivos ignorados pelo Git
├── main.py                       # Ponto de entrada da aplicação
├── requirements.txt              # Dependências que serão empacotadas na Layer
├── controller/
│   └── builder_layer.py          # Classe principal de orquestração
└── utils/
    └── import_aws_credentials.py # Gerenciamento de credenciais AWS
```

## 📌 Como executar o projeto

Para executar o projeto localmente, siga as instruções abaixo:

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd Project-CreateLayerInLambda
   ```

2. **Configure as credenciais AWS:**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas credenciais AWS válidas
   ```

3. **Instale as dependências do projeto:**
   ```bash
   pip install boto3 python-dotenv
   ```

4. **Configure as variáveis no main.py:**
   - `LAYER_NAME`: Nome da sua Layer na AWS
   - `PYTHON_VERSION`: Versão do Python (ex: "3.13")
   - `REQUIREMENTS_FILE`: Caminho para o requirements.txt
   - `REGION_NAME`: Região AWS (padrão: "sa-east-1")

5. **Execute o projeto:**
   ```bash
   python main.py
   ```

## ⚙️ Configuração

### Credenciais AWS
Configure o arquivo .env com suas credenciais AWS:

```env
AWS_ACCESS_KEY_ID="sua-access-key"
AWS_SECRET_ACCESS_KEY="sua-secret-key"
AWS_SESSION_TOKEN="seu-session-token"
```

### Dependências da Layer
Edite o arquivo requirements.txt com as dependências que deseja incluir na Layer:

```txt
pandas
numpy
requests
```

### Configurações do Build
No arquivo main.py, ajuste as configurações conforme sua necessidade:

```python
LAYER_NAME = "minha-lambda-layer"
PYTHON_VERSION = "3.13"
REQUIREMENTS_FILE = "requirements.txt"
REGION_NAME = "sa-east-1"
```

## 🕵️ Dificuldades Encontradas

Durante o desenvolvimento do projeto, algumas dificuldades foram enfrentadas, como:

- **Compatibilidade de plataforma**: Configuração correta do pip para gerar pacotes compatíveis com o ambiente Lambda (Linux) quando executado em Windows
- **Gerenciamento de credenciais**: Implementação segura do carregamento de credenciais AWS temporárias usando variáveis de ambiente
- **Estrutura de diretórios**: Criação da estrutura exata de pastas (`build/python/`) exigida pela AWS para Lambda Layers
- **Tratamento de erros de encoding**: Resolução de problemas de codificação de caracteres na saída de comandos subprocess em ambientes Windows
- **Limpeza de arquivos temporários**: Garantia de que arquivos de build sejam sempre removidos, mesmo em caso de erro durante o processo