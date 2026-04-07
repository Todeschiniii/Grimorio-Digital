from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import customtkinter as ctk
from PIL import Image, ImageTk
import os, base64, json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
ITERATIONS = 200_000
KEY_LEN = 32
SALT_SIZE = 16
IV_SIZE = 12

def gerar_chave(senha_base: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LEN,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(senha_base.encode("utf-8"))

def criptografar(texto: str, senha_base: str) -> str:
    salt = os.urandom(SALT_SIZE)
    iv = os.urandom(IV_SIZE)
    chave = gerar_chave(senha_base, salt)
    aes = Cipher(algorithms.AES(chave), modes.GCM(iv), backend=default_backend()).encryptor()
    cipher = aes.update(texto.encode("utf-8")) + aes.finalize()
    payload = {
        "salt": base64.b64encode(salt).decode("utf-8"),
        "iv": base64.b64encode(iv).decode("utf-8"),
        "tag": base64.b64encode(aes.tag).decode("utf-8"),
        "dados": base64.b64encode(cipher).decode("utf-8")
    }
    return json.dumps(payload)

def _parse_payload(dados_armazenados):
    """Normaliza payload: aceita str JSON ou dict."""
    if isinstance(dados_armazenados, str):
        try:
            return json.loads(dados_armazenados)
        except Exception:
            raise ValueError("JSON inválido")
    if isinstance(dados_armazenados, dict):
        return dados_armazenados
    raise ValueError("Formato inválido do campo criptografado")

def descriptografar(dados_armazenados, senha_base: str) -> str:
    dados = _parse_payload(dados_armazenados)
    # suporte a chaves 'dados' ou 'senha'
    ciphertext_b64 = dados.get("dados") or dados.get("senha")
    if ciphertext_b64 is None:
        raise ValueError("Campo de ciphertext não encontrado")
    try:
        salt = base64.b64decode(dados["salt"])
        iv = base64.b64decode(dados["iv"])
        tag = base64.b64decode(dados["tag"])
        cipher = base64.b64decode(ciphertext_b64)
    except Exception as e:
        raise ValueError(f"Erro ao decodificar base64: {e}")
    chave = gerar_chave(senha_base, salt)
    aes = Cipher(algorithms.AES(chave), modes.GCM(iv, tag), backend=default_backend()).decryptor()
    plain = aes.update(cipher) + aes.finalize()
    return plain.decode("utf-8")

# ==========================
# ☁️ Conexão com MongoDB (ajuste URI para o seu cluster)
# ==========================
uri = "mongodb+srv://root:1234@cluster0.ighoxgz.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
meu_banco = client['Grimorio']
colecao = meu_banco['login']
magia = meu_banco['feiticos']

# ==========================
# 🔧 Configuração UI
# ==========================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
app = ctk.CTk()
app.title("🔮 Grimório Digital - Senha Arcana = Senha do Login")
app.geometry("900x600")
app.resizable(False, False)

bg_path = "grimorio_bg.jpg"
if os.path.exists(bg_path):
    bg_image = Image.open(bg_path).resize((850, 600))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = ctk.CTkLabel(app, image=bg_photo, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
else:
    app.configure(fg_color="#1b082b")

# ==========================
# Estado da sessão (usuário logado)
# ==========================
usuario_atual = {"nome": None, "senha_texto": None}  # senha_texto = senha em claro do usuário (usada como arcana)

# ==========================
# ----- UI: Login -----
# ==========================
titulo = ctk.CTkLabel(app, text="📜 Grimório Digital", font=("Cinzel Decorative", 34, "bold"), text_color="#C39BD3")
titulo.pack(pady=20)

frame_login = ctk.CTkFrame(app, fg_color="#2e1044", corner_radius=20)
frame_login.pack(pady=10, padx=50, fill="both", expand=False)

ctk.CTkLabel(frame_login, text="Nome do Bruxo:", font=("Georgia", 16, "bold"), text_color="#E6E6FA").pack(pady=(20, 5))
nome_entry = ctk.CTkEntry(frame_login, width=300, height=35, placeholder_text="Digite seu nome místico...")
nome_entry.pack(pady=5)

ctk.CTkLabel(frame_login, text="Senha:", font=("Georgia", 16, "bold"), text_color="#E6E6FA").pack(pady=(10, 5))
senha_entry = ctk.CTkEntry(frame_login, width=300, height=35, placeholder_text="Senha do login...", show="*")
senha_entry.pack(pady=5)

resultado_label = ctk.CTkLabel(frame_login, text="", font=("Georgia", 14))
resultado_label.pack(pady=10)

# ==========================
# Função para migrar feitiço (se estiver criptografado com senha_base_sistema)
# ==========================
senha_base_sistema = "ChaveSuperSecretaDoSistema"  # usada para descriptografar senhas armazenadas e para migrar feitiços antigos

def tentar_migrar_feitico(doc_id, campo_str, senha_usuario):
    doc = magia.find_one({"_id": doc_id})
    if doc is None:
        raise ValueError("Documento não encontrado")
    dados_armazenados = doc[campo_str]
    # 1) tentar com senha do usuário
    try:
        texto = descriptografar(dados_armazenados, senha_usuario)
        return texto
    except Exception:
        pass
    # 2) tentar com senha_base_sistema (feitiço antigo)
    try:
        texto = descriptografar(dados_armazenados, senha_base_sistema)
        # re-encrypt com senha_usuario e atualizar documento
        novo_cipher = criptografar(texto, senha_usuario)
        magia.update_one({"_id": doc_id}, {"$set": {campo_str: novo_cipher}})
        return texto
    except Exception as e:
        raise e

# ==========================
# Função de login (descriptografa a senha do usuário armazenada com senha_base_sistema)
# ==========================
def verificar_login():
    nome = nome_entry.get().strip()
    senha_digitada = senha_entry.get().strip()
    if not nome or not senha_digitada:
        resultado_label.configure(text="⚠️ Preencha todos os campos", text_color="orange")
        return

    usuario = colecao.find_one({"nome": nome})
    if not usuario:
        resultado_label.configure(text="❌ Usuário não encontrado", text_color="red")
        return

    # usuario["senha"] está criptografado com senha_base_sistema (ex: seu exemplo)
    try:
        senha_em_texto = descriptografar(usuario["senha"], senha_base_sistema)
    except Exception as e:
        resultado_label.configure(text=f"Erro ao ler senha armazenada: {e}", text_color="red")
        return

    # compara a senha digitada com a senha real do usuário
    if senha_digitada != senha_em_texto:
        resultado_label.configure(text="❌ Senha incorreta", text_color="red")
        return

    # login OK -> guarda a senha do usuário em texto para ser usada como arcana
    usuario_atual["nome"] = nome
    usuario_atual["senha_texto"] = senha_em_texto
    abrir_tela_principal(nome)

# ==========================
# Tela principal (menu)
# ==========================
def abrir_tela_principal(nome):
    for w in app.winfo_children():
        w.destroy()
    ctk.CTkLabel(app, text=f"✨ Bem-vindo, {nome}! ✨", font=("Cinzel Decorative", 28, "bold"), text_color="#E0BBFF").pack(pady=20)
    ctk.CTkButton(app, text="📘 Adicionar Feitiço", fg_color="#8e44ad", hover_color="#732d91", command=adicionar_magia).pack(pady=10)
    ctk.CTkButton(app, text="📖 Meus Feitiços", fg_color="#9b59b6", hover_color="#7d3c98", command=ver_meus_feiticos).pack(pady=10)
    ctk.CTkButton(app, text="🔍 Buscar Todos (admin)", fg_color="#6c3483", hover_color="#512e5f", command=ver_todos_feiticos).pack(pady=10)
    ctk.CTkButton(app, text="🧹 Sair", fg_color="#5e3370", hover_color="#4a245f", command=logout).pack(pady=20)

# ==========================
# Logout
# ==========================
def logout():
    usuario_atual["nome"] = None
    usuario_atual["senha_texto"] = None
    # reiniciar app (simples)
    python = os.sys.executable
    os.execl(python, python, *os.sys.argv)

# ==========================
# Adicionar feitiço (usa senha do usuário para criptografar)
# ==========================
def adicionar_magia():
    for w in app.winfo_children():
        w.destroy()
    ctk.CTkLabel(app, text="🔮 Adicionar Novo Feitiço", font=("Cinzel Decorative", 26, "bold"), text_color="#DAA0F0").pack(pady=20)

    nome_f = ctk.CTkEntry(app, width=400, placeholder_text="Nome do Feitiço")
    nome_f.pack(pady=8)
    dificuldade = ctk.CTkEntry(app, width=400, placeholder_text="Dificuldade")
    dificuldade.pack(pady=8)
    efeito = ctk.CTkEntry(app, width=400, placeholder_text="Efeito")
    efeito.pack(pady=8)

    resultado = ctk.CTkLabel(app, text="")
    resultado.pack(pady=10)

    def salvar():
        if not usuario_atual["nome"] or not usuario_atual["senha_texto"]:
            resultado.configure(text="❌ Você precisa estar logado!", text_color="red")
            return
        if not nome_f.get() or not dificuldade.get() or not efeito.get():
            resultado.configure(text="⚠️ Preencha todos os campos", text_color="orange")
            return
        try:
            senha_user = usuario_atual["senha_texto"]
            doc = {
                "dono": usuario_atual["nome"],
                "nome": criptografar(nome_f.get(), senha_user),
                "dificuldade": criptografar(dificuldade.get(), senha_user),
                "efeito": criptografar(efeito.get(), senha_user)
            }
            magia.insert_one(doc)
            resultado.configure(text="✅ Feitiço salvo!", text_color="green")
            nome_f.delete(0, "end"); dificuldade.delete(0, "end"); efeito.delete(0, "end")
        except Exception as e:
            resultado.configure(text=f"Erro ao salvar: {e}", text_color="red")

    ctk.CTkButton(app, text="✨ Salvar", fg_color="#9b59b6", command=salvar).pack(pady=8)
    ctk.CTkButton(app, text="⬅ Voltar", command=lambda: abrir_tela_principal(usuario_atual["nome"])).pack(pady=6)

# ==========================
# Ver apenas os feitiços do usuário (tenta migrar antigos automaticamente)
# ==========================
def ver_meus_feiticos():
    for w in app.winfo_children():
        w.destroy()
    ctk.CTkLabel(app, text="📖 Meus Feitiços", font=("Cinzel Decorative", 26, "bold"), text_color="#C39BD3").pack(pady=12)

    if not usuario_atual["nome"] or not usuario_atual["senha_texto"]:
        ctk.CTkLabel(app, text="❌ Você precisa estar logado", text_color="red").pack(pady=10)
        ctk.CTkButton(app, text="⬅ Voltar", command=lambda: abrir_tela_principal(None)).pack(pady=10)
        return

    senha_user = usuario_atual["senha_texto"]
    dono = usuario_atual["nome"]
    docs = list(magia.find({"dono": dono}))

    if not docs:
        ctk.CTkLabel(app, text="📭 Nenhum feitiço encontrado.", text_color="yellow").pack(pady=20)
    else:
        for doc in docs:
            try:
                # tenta migrar (tentar_migrar_feitico já tenta com senha_user e com senha_base_sistema)
                nome_plain = tentar_migrar_feitico(doc["_id"], "nome", senha_user)
                diff_plain = tentar_migrar_feitico(doc["_id"], "dificuldade", senha_user)
                ef_plain = tentar_migrar_feitico(doc["_id"], "efeito", senha_user)

                texto = f"🪄 {nome_plain}  |  💀 {diff_plain}  |  ✨ {ef_plain}"
                ctk.CTkLabel(app, text=texto, wraplength=760, justify="left", text_color="#E6E6FA").pack(pady=4)
            except Exception as e:
                ctk.CTkLabel(app, text=f"Erro ao ler feitiço: {e}", text_color="red").pack(pady=4)

    ctk.CTkButton(app, text="⬅ Voltar", command=lambda: abrir_tela_principal(dono)).pack(pady=12)

def ver_todos_feiticos():
    for w in app.winfo_children():
        w.destroy()
    ctk.CTkLabel(app, text="📜 Todos os Feitiços (admin view)", font=("Cinzel Decorative", 24, "bold"), text_color="#C39BD3").pack(pady=12)

    docs = list(magia.find())
    if not docs:
        ctk.CTkLabel(app, text="📭 Nenhum feitiço no banco.", text_color="yellow").pack(pady=20)
    else:
        for doc in docs:
            dono = doc.get("dono", "<desconhecido>")
            try:
                senha_user = usuario_atual.get("senha_texto") or ""
                nome_plain = descriptografar(doc["nome"], senha_user) if senha_user else "<locked>"
                diff_plain = descriptografar(doc["dificuldade"], senha_user) if senha_user else "<locked>"
                ef_plain = descriptografar(doc["efeito"], senha_user) if senha_user else "<locked>"
                texto = f"{dono} → {nome_plain} | {diff_plain} | {ef_plain}"
            except Exception:
                texto = f"{dono} → <Encrypted>"
            ctk.CTkLabel(app, text=texto, wraplength=760, justify="left", text_color="#E6E6FA").pack(pady=3)

    ctk.CTkButton(app, text="⬅ Voltar", command=lambda: abrir_tela_principal(usuario_atual.get("nome"))).pack(pady=12)

# ==========================
# Botão de login na tela inicial
# ==========================
ctk.CTkButton(frame_login, text="🪄 Entrar", fg_color="#8e44ad", hover_color="#6c3483", command=verificar_login).pack(pady=18)

# Rodapé
ctk.CTkLabel(app, text="🕯️ Apenas quem possui a senha do grimório pode ler os feitiços.", text_color="#BFA0FF").pack(side="bottom", pady=10)

app.mainloop()