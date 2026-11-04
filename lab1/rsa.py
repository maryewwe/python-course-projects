'''
rsa.py - реализация ассиметричного шифрования RSA.

Функции:

    def gcd(a: int, b: int) -> int
        Вычисляет НОД двух чисел a и b с помощью алгоритма Евклида

    def is_prime(x: int) -> bool
        Проверяет, является ли число x простым. Если является, возвращает
        True, в обратном случае False

    def extended_euclid(a: int, b: int) -> int
        Реализует расширенный алгоритм Евклида  для нахождения
        коэффициентов Безу, которые используются для вычисления
        обратного по модулю элемента

    def multiplicative_inverse(e: int, phi: int) -> int
        Находит элемент d, обратный к е по модулю phi с использованием
        расширенного алгоритма Евклида

    def generate_keypair(p: int, q: int) -> tuple[tuple[int, int], tuple[int, int]]
        Генерирует 2 пары ключей: публичный (e, n) и приватный (d, n)
        на основе простых чисел p и q

    def encrypt(public_key: tuple[int, int], text: str) -> list[int]
        Шифрует текст с использованием публичного ключа.
        Возвращает зашифрованный текст в виде списка чисел

    def decrypt(private_key: tuple[int, int], cipher_list: list[int]) -> str
        Расшифровывает текст с использованием приватного ключа.
        Возвращает расшифрованныц текст в виде строки

'''
from random import randint

def gcd(a: int, b: int) -> int:
    while a != b:
        if a > b:
            a = a - b
        else:
            b = b - a
    return a


def is_prime(x: int) -> bool:
    dels = set()
    for num in range(1, int(x**0.5)+1):
        if x % num == 0:
            dels.add(num)
            dels.add(x // num)
    dels = sorted(dels)
    return len(dels) == 2


def extended_euclid(a: int, b: int) -> int:
    x0, x1, y0, y1 = 1, 0, 0, 1
    while b != 0:
        q = a // b
        a, b = b, a % b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return x0


def multiplicative_inverse(e: int, phi: int) -> int:
    d = extended_euclid(e, phi)
    return d % phi


def generate_keypair(p: int, q: int) -> tuple[tuple[int, int], tuple[int, int]]:
    n = p * q
    eulers_func = (p-1) * (q-1)
    e = eulers_func
    #генерируем число, являющееся взаимно простым с функцией эйлера
    while not(gcd(e, eulers_func) == 1):
        e = randint(100, eulers_func)
    d = multiplicative_inverse(e, eulers_func)
    return ((e, n), (d, n))


def encrypt(public_key: tuple[int, int], text: str) -> list[int]:
    e, n = public_key
    ciphertext = [(ord(symb)**e) % n for symb in text]
    return ciphertext


def decrypt(private_key: tuple[int, int], cipher_list: list[int]) -> str:
    d, n = private_key
    plaintext = ''.join([chr((char**d) % n) for char in cipher_list])
    return plaintext


p = 1
q = 1
# генерируем рандомные простые числа
while not(is_prime(q) and is_prime(p)):
    p = randint(100, 999)
    q = randint(100, 999)

public_key, private_key = generate_keypair(p, q)
