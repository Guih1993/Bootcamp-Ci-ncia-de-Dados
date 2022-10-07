letra = input() 
num = 0
soma = 0
# TODO: De acordo com a entrada, imprima a posição dessa letra no Alfabeto;
num = ord(letra)
for i in range(65,91):
  soma = soma + 1
  if i == num:
    print(soma)
    break