import json
import os
import random

ARQUIVO_USUARIOS = 'usuarios.json'

def carregar_usuarios():
    if os.path.exists(ARQUIVO_USUARIOS):
        try:
            with open(ARQUIVO_USUARIOS, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Arquivo corrompido. Resetando usuários.")
            return {}
    else:
        return {}

def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, 'w') as f:
        json.dump(usuarios, f, indent=4)

def validar_cpf(cpf):
    return cpf.isdigit() and len(cpf) == 11

def cadastrar_usuario(usuarios):
    print("\n=== Cadastro de Usuário ===")
    cpf = input("Digite seu CPF (somente números): ").strip()
    if not validar_cpf(cpf):
        print("CPF inválido. Deve conter 11 dígitos numéricos.")
        return None
    if cpf in usuarios:
        print("Já existe uma conta com esse CPF.")
        return None

    nome = input("Digite seu nome completo: ").strip()
    contato = input("Digite seu e-mail ou celular: ").strip()
    senha = input("Crie uma senha: ").strip()

    usuarios[cpf] = {
        "nome": nome,
        "contato": contato,
        "senha": senha,
        "saldo": 100.0,
        "transacoes": [],
        "corridas": []
    }

    salvar_usuarios(usuarios)
    print(f"Conta criada com sucesso para {nome}!")
    return cpf

def login(usuarios):
    print("\n=== Login ===")
    cpf = input("Digite seu CPF: ").strip()
    senha = input("Digite sua senha: ").strip()

    if cpf in usuarios and usuarios[cpf]['senha'] == senha:
        print(f"Login bem-sucedido. Bem-vindo, {usuarios[cpf]['nome']}!")
        return cpf
    else:
        print("CPF ou senha incorretos.")
        return None

def apostar(usuarios, cpf):
    usuario = usuarios[cpf]
    saldo = usuario["saldo"]
    print("\n=== Apostar ===")
    print("Animais: Tartaruga, Javali, Guepardo")
    apostas = {}

    while True:
        print(f"\nSaldo atual: R${saldo:.2f}")
        animal = input("Apostar em (ou 'parar'): ").capitalize()
        if animal == "Parar":
            break
        if animal not in ["Tartaruga", "Javali", "Guepardo"]:
            print("Animal inválido.")
            continue
        try:
            valor = float(input(f"Quanto deseja apostar no {animal}? R$"))
        except:
            print("Valor inválido.")
            continue
        if valor <= 0 or valor > saldo:
            print("Valor inválido ou saldo insuficiente.")
            continue
        apostas[animal] = apostas.get(animal, 0) + valor
        saldo -= valor

    if not apostas:
        print("Nenhuma aposta feita.")
        return

    print("\nCorrida iniciada!")
    mult = {
        "Tartaruga": round(random.uniform(1.1, 5.0), 2),
        "Javali": round(random.uniform(1.2, 7.0), 2),
        "Guepardo": round(random.uniform(1.5, 9.0), 2)
    }
    for a, m in mult.items():
        print(f"{a}: x{m}")

    ganho_total = 0
    print("\nResultado:")
    for animal, valor in apostas.items():
        ganho = round(valor * mult[animal], 2)
        print(f"{animal} → Apostou R${valor:.2f} → Ganhou R${ganho:.2f}")
        ganho_total += ganho

    usuario["saldo"] = saldo + ganho_total
    usuario["transacoes"].append({"tipo": "Aposta", "valor": f"+R${ganho_total:.2f}", "saldo": f"R${usuario['saldo']:.2f}"})
    usuario["corridas"].append({
        "multiplicadores": mult,
        "ganho": ganho_total,
        "saldo_apos": usuario["saldo"]
    })

    salvar_usuarios(usuarios)
    print(f"Saldo atualizado: R${usuario['saldo']:.2f}")

def depositar(usuarios, cpf):
    usuario = usuarios[cpf]
    print("\n=== Depósito ===")
    try:
        valor = float(input("Quanto deseja depositar? R$"))
        if valor < 5:
            print("Depósito mínimo é R$5,00.")
            return
    except:
        print("Valor inválido.")
        return
    usuario["saldo"] += valor
    usuario["transacoes"].append({"tipo": "Depósito", "valor": f"+R${valor:.2f}", "saldo": f"R${usuario['saldo']:.2f}"})
    salvar_usuarios(usuarios)
    print(f"Depósito feito. Saldo: R${usuario['saldo']:.2f}")

def sacar(usuarios, cpf):
    usuario = usuarios[cpf]
    print("\n=== Saque ===")
    try:
        valor = float(input("Quanto deseja sacar? R$"))
        if valor <= 0 or valor > usuario["saldo"]:
            print("Valor inválido ou saldo insuficiente.")
            return
    except:
        print("Valor inválido.")
        return
    usuario["saldo"] -= valor
    usuario["transacoes"].append({"tipo": "Saque", "valor": f"-R${valor:.2f}", "saldo": f"R${usuario['saldo']:.2f}"})
    salvar_usuarios(usuarios)
    print(f"Saque feito. Saldo: R${usuario['saldo']:.2f}")

def ver_transacoes(usuarios, cpf):
    print("\n=== Histórico de Transações ===")
    for t in usuarios[cpf]["transacoes"]:
        print(f"{t['tipo']}: {t['valor']} → Saldo: {t['saldo']}")

def ver_corridas(usuarios, cpf):
    print("\n=== Histórico de Corridas ===")
    for i, corrida in enumerate(usuarios[cpf]["corridas"], 1):
        print(f"\nCorrida {i}:")
        for animal, multi in corrida["multiplicadores"].items():
            print(f"{animal}: x{multi}")
        print(f"Ganho: R${corrida['ganho']:.2f}")
        print(f"Saldo após: R${corrida['saldo_apos']:.2f}")

def menu_principal(usuarios, cpf):
    while True:
        print(f"\n=== Menu Principal (Usuário: {usuarios[cpf]['nome']}) ===")
        print(f"Saldo: R${usuarios[cpf]['saldo']:.2f}")
        print("1. Apostar")
        print("2. Depositar")
        print("3. Sacar")
        print("4. Ver histórico de transações")
        print("5. Ver histórico de corridas")
        print("6. Sair")
        opcao = input("Escolha: ")

        if opcao == "1":
            apostar(usuarios, cpf)
        elif opcao == "2":
            depositar(usuarios, cpf)
        elif opcao == "3":
            sacar(usuarios, cpf)
        elif opcao == "4":
            ver_transacoes(usuarios, cpf)
        elif opcao == "5":
            ver_corridas(usuarios, cpf)
        elif opcao == "6":
            print("Volte sempre!")
            break
        else:
            print("Opção inválida.")

def menu_login():
    usuarios = carregar_usuarios()
    cpf_usuario = None

    while not cpf_usuario:
        print("\n=== Sistema de Apostas ===")
        print("1. Criar conta")
        print("2. Fazer login")
        print("3. Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            cpf_usuario = cadastrar_usuario(usuarios)
        elif escolha == "2":
            cpf_usuario = login(usuarios)
        elif escolha == "3":
            print("Saindo...")
            return
        else:
            print("Opção inválida.")

    menu_principal(usuarios, cpf_usuario)

if __name__ == "__main__":
    menu_login()