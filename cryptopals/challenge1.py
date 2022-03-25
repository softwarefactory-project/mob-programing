map_array = ["A","B","C","D","E","F", "G", "H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","0","1","2","3","4","5","6","7","8","9","+","/"]

def add_padding(data: str) -> str:
    length = len(data)
    modulo = length % 3
    return ("0" * (3 - modulo)) + data

def to_binary(data: str, scale: int, num_bits: int) -> str:
    add_padding(bin(int(data, scale))[2:].zfill(num_bits))
    return add_padding(bin(int(data, scale))[2:].zfill(num_bits))

def split_binary(data):
    return (data[i:i+6] for i in range(0, len(data), 6))

def obtain_b64_index(chunk) -> int:
    return(int(chunk, 2))

def solve(prompt):
    generator = split_binary(to_binary(prompt, 16, 8))
    result = ""
    for i in generator:
        result = result + map_array[obtain_b64_index(i)]
    return result


if __name__ == "__main__":
    inp = "49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d"
    res = solve("zz")
    expected = "SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hyb29t"
    if res == expected:
        print("OK")
    else:
        print("KO, got: " + res)
