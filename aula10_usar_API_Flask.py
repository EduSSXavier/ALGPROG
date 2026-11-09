import requests

# Endereço da API
url = "http://127.0.0.1:5000" + "/contar"

# Texto que será enviado
texto = input("Digite um texto: ")

# Envia a requisição GET
resposta = requests.get(
    url,
    params={"texto": texto}
)

# Exibe o resultado
if resposta.status_code == 200:

    resultado = resposta.json()

    print("\nResultado da análise")
    print("----------------------")
    print("Texto:", texto)
    print("Quantidade de vogais:", resultado["vogais"])
    print("Quantidade de consoantes:", resultado["consoantes"])
    print("Total de letras:", resultado["total_letras"])

else:
    print("Erro:", resposta.json())
