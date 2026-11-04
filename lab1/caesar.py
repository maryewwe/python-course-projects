'''
Модуль caesar.py - реализация шифра Цезаря.
В этом модуле используются символы с кодами 32-126
таблицы ASCII.

Функции:
    def encrypt(plaintext: str, shift: int) -> str
        Зашифровывает текст пользователя plaintext шифром
        Цезаря,сдвигая символы на shift позиций вправо.

    def decrypt(ciphertext: str, shift: int) -> str
        Дешифрует текст ciphertext, сдвигая каждый символ
        на shift позиций влево.
'''
alphabet = ''

for chr_num in range(32, 127):
    alphabet += chr(chr_num)


def encrypt(plaintext: str, shift: int) -> str:
    result = ''
    for symbol in plaintext:
        index = alphabet.index(symbol)
        num = (index + shift) % 95
        result += alphabet[num]
    return result


def decrypt(ciphertext: str, shift: int) -> str:
    result = ''
    for symbol in ciphertext:
        index = alphabet.index(symbol)
        num = (index - shift) % 95
        result += alphabet[num]
    return result