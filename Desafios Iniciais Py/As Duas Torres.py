entrada = input()
(distancia,diametro1,diametro2) = [int(s) for s in entrada.split()]
print("{:0.2f}".format(distancia/(diametro1+diametro2)))