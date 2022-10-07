valores = input()
(tempo_gasto,velocidade_media) = [int(s) for s in valores.split()]
print("{:0.3f}".format(tempo_gasto*velocidade_media/12))