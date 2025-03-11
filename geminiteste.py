import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import google.generativeai as genai
import openai
import json
import os
from dotenv import load_dotenv

# --- Configuração das APIs (Chaves de API) ---
load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

# Configuração do Google Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("A variável de ambiente GOOGLE_API_KEY não está definida no arquivo .env")
genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')

# Configuração do OpenAI ChatGPT (substitua com sua chave real)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("A variável de ambiente OPENAI_API_KEY não está definida no arquivo .env")
openai.api_key = OPENAI_API_KEY


# --- Funções de Interação com as APIs ---

def obter_resposta_gemini(pergunta):
    """Obtém a resposta do Google Gemini."""
    try:
        response = gemini_model.generate_content(pergunta)
        return response.text
    except Exception as e:
        return f"Erro Gemini: {str(e)}"

def obter_resposta_chatgpt(pergunta):
    """Obtém a resposta do OpenAI ChatGPT."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # ou outro modelo, como "gpt-4"
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": pergunta},
            ]
        )
        # A resposta está dentro de choices[0].message.content
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro ChatGPT: {str(e)}"



# --- Funções do Aplicativo ---

def enviar_pergunta():
    """Envia a pergunta para as APIs e exibe as respostas."""
    pergunta = pergunta_entry.get()
    if not pergunta.strip():  # Verifica se a pergunta não está vazia
        messagebox.showwarning("Aviso", "Por favor, insira uma pergunta.")
        return

    # Desabilita o botão durante o processamento
    enviar_button.config(state=tk.DISABLED)
    
    # Limpa as áreas de resposta
    resposta_chatgpt_text.delete('1.0', tk.END)
    resposta_gemini_text.delete('1.0', tk.END)
    
    # Mostra um indicador de carregamento (opcional)
    status_label.config(text="Processando...")
    root.update_idletasks()  # Atualiza a interface para mostrar o status

    # Obtém as respostas
    try:
        resposta_chatgpt = obter_resposta_chatgpt(pergunta)
        resposta_gemini = obter_resposta_gemini(pergunta)
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao obter as respostas: {e}")
        resposta_chatgpt = "Erro ao obter resposta"
        resposta_gemini = "Erro ao obter resposta"
    
    # Exibe as respostas
    resposta_chatgpt_text.insert(tk.END, resposta_chatgpt)
    resposta_gemini_text.insert(tk.END, resposta_gemini)

    # Salva no histórico
    salvar_no_historico(pergunta, resposta_chatgpt, resposta_gemini)

    # Reabilita o botão e limpa o status
    enviar_button.config(state=tk.NORMAL)
    status_label.config(text="")
    pergunta_entry.delete(0, 'end') #Limpa a entrada após enviar.

def salvar_no_historico(pergunta, resposta_chatgpt, resposta_gemini):
    """Salva a pergunta e as respostas em um arquivo JSON."""
    try:
        with open("historico.json", "r", encoding='utf-8') as f:
            historico = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        historico = []

    historico.append({
        "pergunta": pergunta,
        "chatgpt": resposta_chatgpt,
        "gemini": resposta_gemini,
    })

    with open("historico.json", "w", encoding='utf-8') as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)

    atualizar_historico_listbox()  # Atualiza a exibição do histórico


def carregar_historico():
    """Carrega o histórico do arquivo JSON."""
    try:
        with open("historico.json", "r", encoding='utf-8') as f:
            historico = json.load(f)
            return historico
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
def exibir_pergunta_historico(event):
    """Exibe a pergunta e respostas selecionadas do histórico."""
    try:
        index = historico_listbox.curselection()[0]
        item = historico_listbox.get(index)
        
        # Encontrar a entrada correspondente no histórico
        for entry in carregar_historico():
             if f"Pergunta: {entry['pergunta']}" == item:
                pergunta = entry['pergunta']
                resposta_chatgpt = entry['chatgpt']
                resposta_gemini = entry['gemini']
                break
        else: # Item não encontrado
            return


        #Abre uma nova janela
        detalhes_window = tk.Toplevel(root)
        detalhes_window.title("Detalhes do Histórico")
        detalhes_window.geometry("600x400")
        
        #Exibe detalhes
        tk.Label(detalhes_window, text=f"Pergunta:", wraplength=580, justify=tk.LEFT, font=("Arial", 12, "bold")).pack(pady=5, anchor='w')
        tk.Label(detalhes_window, text=pergunta, wraplength=580, justify=tk.LEFT, font=("Arial", 10)).pack(pady=5, anchor='w')

        tk.Label(detalhes_window, text="Resposta ChatGPT:", wraplength=580, justify=tk.LEFT, font=("Arial", 12, "bold")).pack(pady=5, anchor='w')
        tk.Label(detalhes_window, text=resposta_chatgpt, wraplength=580, justify=tk.LEFT, font=("Arial", 10)).pack(pady=5, anchor='w')

        tk.Label(detalhes_window, text="Resposta Gemini:", wraplength=580, justify=tk.LEFT, font=("Arial", 12, "bold")).pack(pady=5, anchor='w')
        tk.Label(detalhes_window, text=resposta_gemini, wraplength=580, justify=tk.LEFT, font=("Arial", 10)).pack(pady=5, anchor='w')

    except IndexError:  # Nenhum item selecionado
        pass


def atualizar_historico_listbox():
    """Atualiza o Listbox do histórico."""
    historico_listbox.delete(0, tk.END)
    for item in carregar_historico():
        historico_listbox.insert(tk.END, f"Pergunta: {item['pergunta']}")

def limpar_historico():
    """Limpa o arquivo de histórico e o Listbox."""
    if messagebox.askyesno("Confirmação", "Tem certeza que deseja apagar todo o histórico?"):
        try:
            os.remove("historico.json")
        except FileNotFoundError:
            pass
        atualizar_historico_listbox()
        messagebox.showinfo("Histórico", "Histórico apagado com sucesso.")



# --- Criação da Interface Gráfica com Tkinter ---

root = tk.Tk()
root.title("Ferramenta de Estudo - Comparação ChatGPT e Gemini")
root.geometry("800x600")  # Tamanho inicial da janela
root.resizable(True, True) # Permite redimensionamento

# Frame principal para organizar o layout
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)


# --- Elementos da Interface ---

# 1. Entrada de Pergunta
pergunta_label = ttk.Label(main_frame, text="Digite sua pergunta:")
pergunta_label.pack(pady=5, anchor='w')  # Adicionado padding e alinhamento

pergunta_entry = ttk.Entry(main_frame, width=80)
pergunta_entry.pack(pady=5, fill=tk.X)  # Preenche horizontalmente
pergunta_entry.focus_set()  # Define o foco inicial na caixa de entrada


# 2. Botão de Enviar
enviar_button = ttk.Button(main_frame, text="Enviar Pergunta", command=enviar_pergunta)
enviar_button.pack(pady=10)

# Rótulo de status (opcional)
status_label = ttk.Label(main_frame, text="")
status_label.pack()


# --- Frames para Respostas ---
respostas_frame = ttk.Frame(main_frame)
respostas_frame.pack(pady=10, fill=tk.BOTH, expand=True)

# 3. Resposta ChatGPT
chatgpt_frame = ttk.LabelFrame(respostas_frame, text="Resposta do ChatGPT", padding=5)
chatgpt_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5) #Expande e preenche, com padding

resposta_chatgpt_text = scrolledtext.ScrolledText(chatgpt_frame, wrap=tk.WORD, width=40, height=10)
resposta_chatgpt_text.pack(fill=tk.BOTH, expand=True)

# 4. Resposta Gemini
gemini_frame = ttk.LabelFrame(respostas_frame, text="Resposta do Gemini", padding=5)
gemini_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5) #Expande e preenche, com padding

resposta_gemini_text = scrolledtext.ScrolledText(gemini_frame, wrap=tk.WORD, width=40, height=10)
resposta_gemini_text.pack(fill=tk.BOTH, expand=True)


# --- Histórico ---
historico_frame = ttk.LabelFrame(root, text="Histórico de Perguntas", padding="10")
historico_frame.pack(fill=tk.BOTH, expand=False, pady=10)


historico_listbox = tk.Listbox(historico_frame, width=50, height=10)
historico_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
historico_listbox.bind("<<ListboxSelect>>", exibir_pergunta_historico)  # Chama a função ao clicar

# Scrollbar para o histórico
scrollbar = ttk.Scrollbar(historico_frame, orient="vertical", command=historico_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
historico_listbox.config(yscrollcommand=scrollbar.set)

# Botão para limpar o histórico
limpar_historico_button = ttk.Button(historico_frame, text="Limpar Histórico", command=limpar_historico)
limpar_historico_button.pack(pady=5)

#Inicializar a lista do histórico
atualizar_historico_listbox()


# --- Layout com Grid (Alternativa ao Pack - Mais Controle) ---
# Descomente o código abaixo e comente as linhas .pack() acima para usar o layout Grid
# main_frame.columnconfigure(0, weight=1)
# main_frame.rowconfigure(3, weight=1)

# pergunta_label.grid(row=0, column=0, sticky='w', pady=5)
# pergunta_entry.grid(row=1, column=0, sticky='ew', pady=5)
# enviar_button.grid(row=2, column=0, pady=10)
# status_label.grid(row=2, column=1, pady=10)
# respostas_frame.grid(row=3, column=0, sticky='nsew') #Ocupa todo espaço disponível
# chatgpt_frame.grid(row=0, column=0, sticky='nsew', padx=5)
# gemini_frame.grid(row=0, column=1, sticky='nsew', padx=5)
# resposta_chatgpt_text.grid(row=0, column=0, sticky='nsew')  # Expande em todas as direções
# resposta_gemini_text.grid(row=0, column=0, sticky='nsew')    # Expande em todas as direções

# historico_frame.grid(row=4, column=0, sticky='ew', pady=10) #Expande horizontal
# historico_listbox.grid(row=0, column=0, sticky='nsew')
# scrollbar.grid(row=0, column=1, sticky='ns')

# --- Inicialização ---
root.mainloop()
