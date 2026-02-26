# 🔮 Grimório Digital — Secure Encrypted Spell Manager

Aplicação desktop desenvolvida em **Python** com interface moderna em **CustomTkinter**, integrada ao **MongoDB Atlas**, com sistema de criptografia forte **AES-256 (GCM)** para armazenamento seguro de dados.

Um projeto que demonstra domínio em **segurança aplicada**, **criptografia moderna**, **arquitetura funcional** e **integração com banco de dados em nuvem**.

---

# 📑 Sumário

- [📖 Sobre o Projeto](#-sobre-o-projeto)
- [✨ Principais Diferenciais](#-principais-diferenciais)
- [🧠 Arquitetura do Sistema](#-arquitetura-do-sistema)
- [🔐 Segurança e Criptografia](#-segurança-e-criptografia)
- [🖥️ Interface Gráfica](#️-interface-gráfica)
- [☁️ Integração com MongoDB](#️-integração-com-mongodb)
- [⚙️ Tecnologias Utilizadas](#️-tecnologias-utilizadas)
- [🚀 Como Executar o Projeto](#-como-executar-o-projeto)
- [📂 Estrutura do Projeto](#-estrutura-do-projeto)
- [📌 Possíveis Melhorias Futuras](#-possíveis-melhorias-futuras)
- [📄 Licença](#-Licença)
- [👥 Créditos & Contatos](#-créditos--contatos)

---

# 📖 Sobre o Projeto

O **Grimório Digital** é uma aplicação desktop segura para gerenciamento de dados criptografados por usuário.

Cada usuário possui sua própria chave (derivada da senha real), utilizada para:

- 🔐 Criptografar seus registros  
- 🔓 Descriptografar seus próprios dados  
- 🛡️ Garantir que nenhuma informação sensível seja armazenada em texto puro  

O sistema inclui:

- Sistema de login criptografado  
- Armazenamento seguro em nuvem  
- Criptografia individual por usuário  
- Interface gráfica moderna  
- Migração automática de dados criptografados com chave antiga  

---

# ✨ Principais Diferenciais

- 🔐 Criptografia real com **AES-256 em modo GCM**
- 🔑 Derivação de chave segura com **PBKDF2 (200.000 iterações)**
- 🧂 Salt aleatório para cada criptografia
- 🧠 Migração automática de registros antigos
- 🎨 Interface moderna em modo escuro
- ☁️ Integração com MongoDB Atlas
- 🧩 Organização clara entre segurança, persistência e UI

---

# 🧠 Arquitetura do Sistema

O projeto está organizado em quatro camadas principais:

## 1️⃣ Camada de Criptografia

Responsável por:

- Derivação de chave com **PBKDF2-HMAC-SHA256**
- Criptografia com **AES-GCM**
- Serialização segura em JSON + Base64

### 🔄 Fluxo

1. Geração de salt aleatório  
2. Derivação da chave com PBKDF2  
3. Criptografia AES-GCM  
4. Armazenamento estruturado no banco  

### 📦 Formato armazenado

```json
{
  "salt": "...",
  "iv": "...",
  "tag": "...",
  "dados": "..."
}
```

---

## 2️⃣ Camada de Persistência

- Conexão com MongoDB Atlas via PyMongo  
- Banco: `Grimorio`  
- Coleções:
  - `login`
  - `feiticos`
- Atualização automática de registros migrados  

---

## 3️⃣ Camada de Sessão

- Controle do usuário autenticado  
- Gerenciamento da chave ativa  
- Controle de estado da aplicação  

---

## 4️⃣ Camada de Interface (UI)

Construída com CustomTkinter, incluindo:

- Tela de login  
- Menu principal  
- Cadastro de registros  
- Visualização individual  
- Visualização administrativa  
- Logout com reinicialização segura  

---

# 🔐 Segurança e Criptografia

O sistema utiliza:

- **AES (Advanced Encryption Standard)**
- **Modo GCM (Galois/Counter Mode)** — confidencialidade + integridade
- **PBKDF2-HMAC-SHA256**
- 200.000 iterações
- Salt de 16 bytes
- IV de 12 bytes
- Tag de autenticação

## 🛡️ Garantias

✔️ Nenhum dado sensível armazenado em texto puro  
✔️ Cada usuário possui sua própria chave  
✔️ Proteção contra modificação de dados  
✔️ Migração automática de dados antigos  

---

# 🖥️ Interface Gráfica

Interface moderna desenvolvida com:

- CustomTkinter  
- Tema escuro  
- Componentes estilizados  
- Navegação dinâmica entre telas  

## Funcionalidades disponíveis

- 🪄 Login seguro  
- 📘 Adicionar registros  
- 📖 Visualizar registros do usuário  
- 🔍 Visualização administrativa  
- 🧹 Logout  

---

# ☁️ Integração com MongoDB

O sistema utiliza MongoDB Atlas para armazenamento em nuvem.

## Estrutura

Banco: `Grimorio`

- `login` → usuários (senha criptografada)  
- `feiticos` → dados criptografados por usuário  

Cada documento pertence a um proprietário (`dono`) e seus campos são criptografados individualmente.

---

# ⚙️ Tecnologias Utilizadas

- Python 3  
- PyMongo  
- MongoDB Atlas  
- CustomTkinter  
- Pillow (PIL)  
- Cryptography  
- AES-256 (GCM)  
- PBKDF2-HMAC-SHA256  

---

# 🚀 Como Executar o Projeto

## 1️⃣ Clonar o repositório

```bash
git clone https://github.com/seu-usuario/grimorio-digital.git
cd grimorio-digital
```

## 2️⃣ Instalar dependências

```bash
pip install pymongo customtkinter pillow cryptography
```

## 3️⃣ Configurar a URI do MongoDB

Edite no código:

```python
uri = "SUA_URI_DO_MONGODB"
```

## 4️⃣ Executar

```bash
python main.py
```

---

# 📂 Estrutura do Projeto

```
grimorio-digital/
│
├── main.py
├── grimorio_bg.jpg
└── README.md
```

---

# 📌 Possíveis Melhorias Futuras

- 🔒 Implementar hash de senha com bcrypt  
- 🧩 Separar em arquitetura MVC  
- 🧪 Adicionar testes automatizados  
- 📦 Empacotar como executável (.exe)  
- 🌐 Criar versão Web com FastAPI  
- 🔐 Implementar autenticação multifator

# 📄 Licença

Projeto desenvolvido para fins educacionais.

---

# 👥 Créditos & contatos

1. <b>Mateus Todeschini</b> - GitHub: https://github.com/Todeschiniii<br>
2. <b>Heitor Pinheiro</b> - GitHub: https://github.com/HeitorPinheiro11<br>
3. <b>Davi Dancuart</b> - GitHub: https://github.com/DaviDancuart<br>

Repositório: https://github.com/Todeschiniii/Grimorio-Digital
