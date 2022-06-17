use std::env;

struct HexString(String);

impl HexString {
    pub fn from_string(s: String) -> Result<HexString, String> {
        if s.chars()
            .all(|c| (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9'))
        {
            Ok(HexString(s))
        } else {
            Err("Invalid char!".to_string())
        }
    }
}

fn main() -> Result<(), String> {
    let hex_value = HexString::from_string(env::args().nth(1).unwrap_or(
        "49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d".to_string()
    ))?;

    // Validate that this is ascii
    let binary_value = to_binary(&hex_value).ok_or("Unable to create binary value!".to_string())?;
    let binary_value_padded = add_padding(&binary_value, 3);
    let splitted = split_binary(binary_value_padded, 6);
    let mut result = String::new();

    for i in splitted {
        let index = u8::from_str_radix(i.as_str(), 2).unwrap();
        result.push_str(convert_u8_b64_value(index));
    }
    println!("{}", result);
    Ok(())
}

fn to_binary(hex: &HexString) -> Option<String> {
    let mut result_binary = String::from("");
    // https://doc.rust-lang.org/std/primitive.str.html
    for c in hex.0.chars() {
        match convert_hex_char_to_binary(c.to_ascii_uppercase()) {
            Some(v) =>         result_binary.push_str(v),
            None => return None
        }
    }
    let zero_unfilled = result_binary.trim_start_matches('0');
    return Some(zero_unfilled.to_owned());
}

fn add_padding(binary_raw: &str, modulus: usize) -> String {
    //Wanted to mke modulus u8 not usize...
    let chunk_len = binary_raw.chars().count();
    let module = chunk_len % modulus;
    let padding_length = 3 - module;
    let mut prefix = "0".repeat(padding_length);
    prefix.push_str(binary_raw);
    return prefix;
}

fn split_binary(data: String, length: u8) -> Vec<String> {
    data.as_str()
        .chars()
        .collect::<Vec<_>>()
        .chunks(length as _)
        .map(|v| v.into_iter().collect())
        .collect::<Vec<String>>()
}

fn convert_hex_char_to_binary(c: char) -> Option<&'static str> {
    match c {
        '0' => Some("0000"),
        '1' => Some("0001"),
        '2' => Some("0010"),
        '3' => Some("0011"),
        '4' => Some("0100"),
        '5' => Some("0101"),
        '6' => Some("0110"),
        '7' => Some("0111"),
        '8' => Some("1000"),
        '9' => Some("1001"),
        'A' => Some("1010"),
        'B' => Some("1011"),
        'C' => Some("1100"),
        'D' => Some("1101"),
        'E' => Some("1110"),
        'F' => Some("1111"),
        _ => None,
    }
}

fn convert_u8_b64_value(index: u8) -> &'static str {
    let map_value = [
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R",
        "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
        "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1",
        "2", "3", "4", "5", "6", "7", "8", "9", "+", "/",
    ];
    map_value[index as usize]
}
