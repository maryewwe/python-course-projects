import pytest
import sys
import os

# Add lab1 to the path so we can import the modules
sys.path.insert(0, os.path.dirname(__file__))

# Try to import modules individually
caesar = None
vigenere = None
rsa = None
hack = None

try:
    import caesar
except ImportError:
    pass

try:
    import vigenere
except ImportError:
    pass

try:
    import rsa
except ImportError:
    pass

try:
    import hack
except ImportError:
    pass


class TestCaesar:
    """Tests for Caesar cipher implementation."""
    
    @pytest.mark.skipif(caesar is None, reason="caesar module not found")
    def test_caesar_encrypt_basic(self):
        """Test basic Caesar cipher encryption."""
        result = caesar.encrypt("Hello, World!", 3)
        expected = "Khoor/#Zruog$"
        assert result == expected, f"Expected {expected}, got {result}"
    
    @pytest.mark.skipif(caesar is None, reason="caesar module not found")
    def test_caesar_decrypt_basic(self):
        """Test basic Caesar cipher decryption."""
        result = caesar.decrypt("Khoor/#Zruog$", 3)
        expected = "Hello, World!"
        assert result == expected, f"Expected {expected}, got {result}"
    
    @pytest.mark.skipif(caesar is None, reason="caesar module not found")
    def test_caesar_encrypt_negative_shift(self):
        """Test Caesar encryption with negative shift."""
        plaintext = "ABC"
        result = caesar.encrypt(plaintext, -1)
        # Should shift backwards in ASCII range
        assert result != plaintext
        # Test that decrypt reverses it
        decrypted = caesar.decrypt(result, -1)
        assert decrypted == plaintext
    
    @pytest.mark.skipif(caesar is None, reason="caesar module not found")
    def test_caesar_full_ascii_range(self):
        """Test Caesar cipher works with all printable ASCII characters."""
        # Test with characters from ASCII 32-126
        test_chars = ''.join(chr(i) for i in range(32, 127))
        encrypted = caesar.encrypt(test_chars, 5)
        decrypted = caesar.decrypt(encrypted, 5)
        assert decrypted == test_chars
    
    @pytest.mark.skipif(caesar is None, reason="caesar module not found")
    def test_caesar_wraparound(self):
        """Test that Caesar cipher wraps around correctly."""
        # Test character near end of printable range
        result = caesar.encrypt("~", 1)  # ASCII 126 + 1 should wrap to ASCII 32
        expected = " "  # ASCII 32 (space)
        assert result == expected
    
    @pytest.mark.skipif(caesar is None, reason="caesar module not found")
    def test_caesar_zero_shift(self):
        """Test Caesar cipher with zero shift."""
        plaintext = "No change expected!"
        result = caesar.encrypt(plaintext, 0)
        assert result == plaintext
        result = caesar.decrypt(plaintext, 0)
        assert result == plaintext



class TestVigenere:
    """Tests for Vigenere cipher implementation."""
    
    @pytest.mark.skipif(vigenere is None, reason="vigenere module not found")
    def test_vigenere_encrypt_basic(self):
        """Test basic Vigenere cipher encryption."""
        result = vigenere.encrypt("attack at dawn", "LEMON")
        expected = "lx!opv$m#-oe$|"
        assert result == expected, f"Expected {expected}, got {result}"
    
    @pytest.mark.skipif(vigenere is None, reason="vigenere module not found")
    def test_vigenere_decrypt_basic(self):
        """Test basic Vigenere cipher decryption."""
        result = vigenere.decrypt("lx!opv$m#-oe$|", "LEMON")
        expected = "attack at dawn"
        assert result == expected, f"Expected {expected}, got {result}"
    
    @pytest.mark.skipif(vigenere is None, reason="vigenere module not found")
    def test_vigenere_case_insensitive_key(self):
        """Test that Vigenere key is case insensitive."""
        plaintext = "test"
        upper_key = "KEY"
        lower_key = "key"
        result_upper = vigenere.encrypt(plaintext, upper_key)
        result_lower = vigenere.encrypt(plaintext, lower_key)
        assert result_upper == result_lower
    
    @pytest.mark.skipif(vigenere is None, reason="vigenere module not found")
    def test_vigenere_key_cycling(self):
        """Test that Vigenere key cycles correctly."""
        # Use a short key with longer text to test cycling
        plaintext = "abcdefghij"
        key = "XY"
        encrypted = vigenere.encrypt(plaintext, key)
        decrypted = vigenere.decrypt(encrypted, key)
        assert decrypted == plaintext
    
    @pytest.mark.skipif(vigenere is None, reason="vigenere module not found")
    def test_vigenere_non_alpha_key_ignored(self):
        """Test that non-alphabetic characters in key are ignored."""
        plaintext = "test"
        key_with_numbers = "K3E2Y1"
        key_clean = "KEY"
        result_with_numbers = vigenere.encrypt(plaintext, key_with_numbers)
        result_clean = vigenere.encrypt(plaintext, key_clean)
        assert result_with_numbers == result_clean
    
    @pytest.mark.skipif(vigenere is None, reason="vigenere module not found")
    def test_vigenere_empty_key(self):
        """Test behavior with empty or invalid key."""
        plaintext = "test"
        # This should handle gracefully or raise appropriate exception
        try:
            result = vigenere.encrypt(plaintext, "")
            # If it doesn't raise an exception, it should return something reasonable
            assert isinstance(result, str)
        except (ValueError, IndexError):
            # It's acceptable to raise an exception for empty key
            pass


class TestRSA:
    """Tests for RSA implementation."""
    
    @pytest.mark.skipif(rsa is None, reason="rsa module not found")
    def test_is_prime(self):
        """Test prime number detection."""
        assert rsa.is_prime(2) == True
        assert rsa.is_prime(3) == True
        assert rsa.is_prime(17) == True
        assert rsa.is_prime(97) == True
        assert rsa.is_prime(4) == False
        assert rsa.is_prime(15) == False
        assert rsa.is_prime(1) == False
        assert rsa.is_prime(0) == False
    
    @pytest.mark.skipif(rsa is None, reason="rsa module not found")
    def test_gcd(self):
        """Test greatest common divisor calculation."""
        assert rsa.gcd(48, 18) == 6
        assert rsa.gcd(17, 13) == 1
        assert rsa.gcd(100, 25) == 25
        assert rsa.gcd(7, 7) == 7
    
    @pytest.mark.skipif(rsa is None, reason="rsa module not found")
    def test_multiplicative_inverse(self):
        """Test multiplicative inverse calculation."""
        # Test known values
        result = rsa.multiplicative_inverse(3, 26)
        assert (3 * result) % 26 == 1
        
        result = rsa.multiplicative_inverse(7, 40)
        assert (7 * result) % 40 == 1
    
    @pytest.mark.skipif(rsa is None, reason="rsa module not found")
    def test_generate_keypair(self):
        """Test RSA key pair generation."""
        p, q = 17, 19  # Small primes for testing
        public_key, private_key = rsa.generate_keypair(p, q)
        
        # Check that keys have correct format
        assert len(public_key) == 2
        assert len(private_key) == 2
        
        e, n = public_key
        d, n2 = private_key
        
        # n should be the same in both keys
        assert n == n2
        assert n == p * q
        
        # Basic validation that e and d are multiplicative inverses
        phi = (p - 1) * (q - 1)
        assert (e * d) % phi == 1
    
    @pytest.mark.skipif(rsa is None, reason="rsa module not found")
    def test_rsa_encrypt_decrypt_basic(self):
        """Test basic RSA encryption and decryption."""
        p, q = 17, 19
        public_key, private_key = rsa.generate_keypair(p, q)
        
        plaintext = "Hello!"
        encrypted = rsa.encrypt(public_key, plaintext)
        decrypted = rsa.decrypt(private_key, encrypted)
        
        assert decrypted == plaintext
        assert isinstance(encrypted, list)
        assert all(isinstance(x, int) for x in encrypted)
    
    @pytest.mark.skipif(rsa is None, reason="rsa module not found")
    def test_rsa_various_characters(self):
        """Test RSA with various characters."""
        p, q = 61, 53  # Larger primes for more character support
        public_key, private_key = rsa.generate_keypair(p, q)
        
        test_strings = [
            "ABC",
            "123",
            "Hello, World!",
            "Special chars: @#$%^&*()",
        ]
        
        for text in test_strings:
            encrypted = rsa.encrypt(public_key, text)
            decrypted = rsa.decrypt(private_key, encrypted)
            assert decrypted == text, f"Failed for text: {text}"


class TestHack:
    """Tests for Caesar cipher hacking."""
    
    @pytest.mark.skipif(hack is None or caesar is None, reason="hack or caesar module not found")
    def test_hack_basic(self):
        """Test basic Caesar cipher hacking."""
        # Create a known encrypted message
        plaintext = "the quick brown fox jumps over the lazy dog"
        shift = 7
        ciphertext = caesar.encrypt(plaintext, shift)
        
        # Try to hack it
        result_text, result_shift = hack.hack(ciphertext)
        
        # Should recover original text and shift
        assert result_text == plaintext
        assert result_shift == shift
    
    @pytest.mark.skipif(hack is None or caesar is None, reason="hack or caesar module not found")
    def test_hack_common_english_text(self):
        """Test hacking with common English text."""
        plaintext = "this is a test message with common english words"
        shift = 13
        ciphertext = caesar.encrypt(plaintext, shift)
        
        result_text, result_shift = hack.hack(ciphertext)
        
        # Should be close to original
        assert result_shift == shift
        assert result_text == plaintext
    
    @pytest.mark.skipif(hack is None, reason="hack module not found")
    def test_hack_returns_valid_format(self):
        """Test that hack function returns correct format."""
        ciphertext = "encrypted text"
        result = hack.hack(ciphertext)
        
        # Should return tuple of (string, int)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], int)
        
        # Shift should be in valid range (1-25 for Caesar)
        assert 1 <= result[1] <= 25 or result[1] == 0


class TestIntegration:
    """Integration tests across multiple modules."""
    
    @pytest.mark.skipif(caesar is None, reason="caesar module not found")
    def test_caesar_roundtrip_various_shifts(self):
        """Test Caesar cipher roundtrip with various shifts."""
        plaintext = "Integration test message!"
        
        for shift in [-10, -1, 0, 1, 5, 13, 25, 50]:
            encrypted = caesar.encrypt(plaintext, shift)
            decrypted = caesar.decrypt(encrypted, shift)
            assert decrypted == plaintext, f"Failed for shift {shift}"
    
    @pytest.mark.skipif(vigenere is None, reason="vigenere module not found")
    def test_vigenere_roundtrip_various_keys(self):
        """Test Vigenere cipher roundtrip with various keys."""
        plaintext = "This is a longer message for testing purposes."
        keys = ["A", "KEY", "LONGERKEYWORD", "MiXeDcAsE"]
        
        for key in keys:
            encrypted = vigenere.encrypt(plaintext, key)
            decrypted = vigenere.decrypt(encrypted, key)
            assert decrypted == plaintext, f"Failed for key {key}"


# Additional utility tests
class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.skipif(caesar is None, reason="caesar module not found")
    def test_caesar_empty_string(self):
        """Test Caesar cipher with empty string."""
        result_encrypt = caesar.encrypt("", 5)
        assert result_encrypt == ""
        
        result_decrypt = caesar.decrypt("", 5)
        assert result_decrypt == ""
    
    @pytest.mark.skipif(vigenere is None, reason="vigenere module not found")
    def test_vigenere_empty_string(self):
        """Test Vigenere cipher with empty string."""
        result_encrypt = vigenere.encrypt("", "KEY")
        assert result_encrypt == ""
        
        result_decrypt = vigenere.decrypt("", "KEY")
        assert result_decrypt == ""
    
    @pytest.mark.skipif(rsa is None, reason="rsa module not found")
    def test_rsa_empty_string(self):
        """Test RSA with empty string."""
        p, q = 17, 19
        public_key, private_key = rsa.generate_keypair(p, q)
        
        encrypted = rsa.encrypt(public_key, "")
        assert encrypted == []
        
        decrypted = rsa.decrypt(private_key, [])
        assert decrypted == ""