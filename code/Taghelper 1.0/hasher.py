from simhash import Simhash

a = "abced"
b = "12345"

foo = Simhash(a, f=32)
bar = Simhash(b, f=32)

print(foo.value)
print(bar.value)




def hashstr(inp, fv=32):
    return Simhash(inp, f=fv).value



print(hashstr(a))
print(hashstr(b))