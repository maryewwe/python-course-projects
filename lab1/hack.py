'''
Модуль hack.py - реализация взлома шифра Цезаря с помощью
частотного криптоанализа.

Функции:

    def the_most_frequent(text: str) -> int
        Подсчитывает в строке количество символов,
        которые являются самыми частоиспользуемыми в английском
        языке.

    def hack(ciphertext: str) -> tuple[str, int]:
        Перебирает сдвиги от 1 до 25 включительно
        и находит среди них тот, при котором в
        расшифрованном тексте больше всего самых частоиспользуемых
        символов английского языка. Возвращает
        расшифрованный текст и подобранный сдвиг.

'''
from caesar import decrypt

the_most_frequent_eng = [' ', 'e', 't', 'a', 'o', 'i', 'n']


def the_most_frequent(text: str) -> int:
    sm = 0
    text = text.lower()
    for symb in text:
        if symb in the_most_frequent_eng:
            sm += 1
    return sm


def hack(ciphertext: str) -> tuple[str, int]:
    shift = 0
    mx = 0
    for i in range(1, 26):
        text = decrypt(ciphertext, i)
        amount_of_letters = the_most_frequent(text)
        if amount_of_letters > mx:
            mx = amount_of_letters
            shift = i
    return decrypt(ciphertext, shift), shift