valores = input()
(hotdog,pessoas) = [int(s) for s in valores.split()]
print("{:0.2f}".format(hotdog/pessoas))