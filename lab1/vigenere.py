'''
vigenere.py - реализация шифра Виженера

Функции:

    def encrypt(plaintext: str, keyword: str) -> str
        Зашифровывает заданный текст plaintext с использованием
        ключевого слова keyword

    def decrypt(ciphertext: str, keyword: str) -> str
        Дешифрует зашифрованный текст ciphertext с помощью
        ключевого слова keyword

'''
alphabet = ''
letters = 'abcdefghijklmnopqrstuvwxyz'
for chr_num in range(32, 127):
    alphabet += chr(chr_num) #заполняем алфавит нужными символами таблицы ascii


def encrypt(plaintext: str, keyword: str) -> str:
    result = ''
    keyword = ''.join(filter(lambda x: x in letters, keyword.lower()))
    if keyword == '':
        return plaintext
    st = keyword * (len(plaintext)//len(keyword)) + keyword[:len(plaintext) % len(keyword)]
    for letter in range(len(plaintext)):
        new_index = (alphabet.index(plaintext[letter]) + letters.index(st[letter])) % 95
        result += alphabet[new_index]
    return result


def decrypt(ciphertext: str, keyword: str) -> str:
    result = ''
    keyword = ''.join((filter(lambda x: x in letters, keyword.lower())))
    if keyword == '':
        return ciphertext
    st = keyword * (len(ciphertext) // len(keyword)) + keyword[:len(ciphertext) % len(keyword)]
    for letter in range(len(ciphertext)):
        new_index = (alphabet.index(ciphertext[letter]) - letters.index(st[letter])) % 95
        result += alphabet[new_index]
    return result