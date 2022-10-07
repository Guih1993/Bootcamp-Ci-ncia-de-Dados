if salario <= 600.00:
  p = 0.17
  s = salario + (salario * p)
  r = s - salario
elif salario >= 601 and salario <= 900:
  p = 0.13
  s = salario + (salario * p)
  r = s - salario
elif salario >= 901 and salario <= 1500:
  p = 0.12
  s = salario + (salario * p)
  r = s - salario
elif salario >= 1501 and salario <= 2000:
  p = 0.1
  s = salario + (salario * p)
  r = s - salario
elif salario > 2001:
  p = 0.05
  s = salario + (salario * p)
  r = s - salario

novoSal = (s)
novoRe = (r)
print(f" Novo salario: {novoSal:.2f}\n Reajuste ganho: {novoRe:.2f}\n Em percentual: {p:.0%}")