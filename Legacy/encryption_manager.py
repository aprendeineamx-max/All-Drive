"""
Gestor de Encriptación - VultrDrive Desktop
Mejora #36: Encriptación de credenciales antes de guardar
"""

import os
import base64
import hashlib
import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

class EncryptionManager:
    """
    Gestor de encriptación para credenciales
    
    Usa Fernet (AES-128 en modo CBC) para encriptación simétrica
    La clave se deriva de información del sistema del usuario
    """
    
    def __init__(self, salt=None):
        """
        Inicializar gestor de encriptación
        
        Args:
            salt: Salt personalizado (None = usar salt basado en usuario)
        """
        self.salt = salt or self._generate_salt()
        self._key = None
    
    def _generate_salt(self):
        """Generar salt único basado en usuario del sistema"""
        username = getpass.getuser()
        machine_name = os.environ.get('COMPUTERNAME', 'unknown')
        combined = f"{username}:{machine_name}:VultrDrive"
        return hashlib.sha256(combined.encode()).digest()[:16]
    
    def _get_key(self):
        """Obtener o generar clave de encriptación"""
        if self._key is None:
            # Derivar clave de información del sistema
            username = getpass.getuser()
            machine_id = os.environ.get('COMPUTERNAME', 'unknown')
            
            # Material para derivar clave
            password = f"{username}:{machine_id}:VultrDrive:2025"
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=100000,
                backend=default_backend()
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            self._key = Fernet(key)
        
        return self._key
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encriptar texto plano
        
        Args:
            plaintext: Texto a encriptar
            
        Returns:
            Texto encriptado (base64)
        """
        if not plaintext:
            return ""
        
        try:
            key = self._get_key()
            encrypted = key.encrypt(plaintext.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            raise EncryptionError(f"Error al encriptar: {str(e)}")
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Desencriptar texto
        
        Args:
            ciphertext: Texto encriptado (base64) o texto plano en base64
            
        Returns:
            Texto desencriptado o decodificado
        """
        if not ciphertext:
            return ""
        
        # PASO 1: Verificar si es base64 estándar (puede contener Fernet encriptado)
        # Las credenciales pueden estar: base64(Fernet(texto)) o base64(texto)
        if len(ciphertext) > 50 and ('=' in ciphertext or ciphertext.replace('+', '').replace('/', '').replace('=', '').replace('-', '').replace('_', '').isalnum()):
            try:
                # Intentar decodificar como base64 estándar primero
                decoded_bytes = base64.b64decode(ciphertext)
                decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
                
                # PASO 2: Si el resultado decodificado empieza con "gAAAAA" es un token Fernet
                # Intentar desencriptar con Fernet
                if decoded_str.startswith('gAAAAA'):
                    try:
                        key = self._get_key()
                        # El token Fernet ya está decodificado, solo necesitamos desencriptarlo
                        decrypted = key.decrypt(decoded_bytes)
                        return decrypted.decode('utf-8')
                    except Exception:
                        # No se pudo desencriptar con nuestra clave (puede ser de otra computadora)
                        # En este caso, las credenciales fueron encriptadas en otra máquina
                        # Devolver None o lanzar error para que el usuario reingrese las credenciales
                        raise EncryptionError("Las credenciales fueron encriptadas en otra computadora. Por favor, reingresa las credenciales originales.")
                
                # PASO 2.5: Si el resultado decodificado parece ser base64 también (empieza con "Z0FB")
                # Puede ser base64(base64(texto)) o base64(Fernet) que no se pudo desencriptar
                if decoded_str.startswith('Z0FB') and len(decoded_str) > 100:
                    # Intentar decodificar nuevamente
                    try:
                        double_decoded = base64.b64decode(decoded_str)
                        double_decoded_str = double_decoded.decode('utf-8', errors='ignore')
                        # Si el resultado doble decodificado empieza con "gAAAAA", es Fernet
                        if double_decoded_str.startswith('gAAAAA'):
                            try:
                                key = self._get_key()
                                decrypted = key.decrypt(double_decoded)
                                return decrypted.decode('utf-8')
                            except Exception:
                                raise EncryptionError("Las credenciales fueron encriptadas en otra computadora. Por favor, reingresa las credenciales originales.")
                        # Si no es Fernet, puede ser texto plano
                        if any(c.isprintable() for c in double_decoded_str[:50]):
                            return double_decoded_str
                    except Exception:
                        pass
                
                # PASO 3: No es Fernet, es texto plano en base64
                if decoded_str and len(decoded_str) > 0:
                    if any(c.isprintable() for c in decoded_str[:50]):
                        return decoded_str
            except Exception:
                # No es base64 válido, continuar con otros métodos
                pass
        
        # PASO 4: Intentar como Fernet directo (base64 URL-safe)
        if self._is_encrypted(ciphertext):
            try:
                key = self._get_key()
                decoded = base64.urlsafe_b64decode(ciphertext.encode())
                decrypted = key.decrypt(decoded)
                return decrypted.decode()
            except Exception as e:
                raise EncryptionError(f"Error al desencriptar: {str(e)}")
        
        # PASO 5: Texto plano (compatibilidad con configuraciones antiguas)
        return ciphertext
    
    def _is_encrypted(self, text: str) -> bool:
        """
        Detectar si un texto está encriptado con nuestro sistema Fernet
        
        Args:
            text: Texto a verificar
            
        Returns:
            True si está encriptado con Fernet
        """
        if not text:
            return False
        
        # Los textos encriptados con Fernet tienen características específicas:
        # 1. Son base64 URL-safe
        # 2. Tienen una longitud mínima (Fernet tokens son ~150+ caracteres)
        # 3. Pueden ser desencriptados con nuestra clave
        
        # Verificar longitud mínima (Fernet tokens son largos)
        if len(text) < 100:
            return False
        
        # Intentar desencriptar para verificar
        try:
            key = self._get_key()
            decoded = base64.urlsafe_b64decode(text.encode())
            # Si puede decodificar base64 y tiene longitud razonable, intentar desencriptar
            if len(decoded) > 0:
                # Intentar desencriptar (si falla, no está encriptado con nuestra clave)
                try:
                    key.decrypt(decoded)
                    return True
                except:
                    # No está encriptado con nuestra clave, o es texto plano en base64
                    return False
        except:
            return False
        
        return False
    
    def encrypt_dict(self, data: dict, fields: list) -> dict:
        """
        Encriptar campos específicos de un diccionario
        
        Args:
            data: Diccionario con datos
            fields: Lista de campos a encriptar
            
        Returns:
            Diccionario con campos encriptados
        """
        encrypted_data = data.copy()
        
        for field in fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(encrypted_data[field])
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields: list) -> dict:
        """
        Desencriptar campos específicos de un diccionario
        
        Args:
            data: Diccionario con datos encriptados
            fields: Lista de campos a desencriptar
            
        Returns:
            Diccionario con campos desencriptados
        """
        decrypted_data = data.copy()
        
        for field in fields:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_value = self.decrypt(decrypted_data[field])
                    # Solo actualizar si se desencriptó/decodificó correctamente
                    if decrypted_value != decrypted_data[field] or not self._is_encrypted(decrypted_data[field]):
                        decrypted_data[field] = decrypted_value
                except EncryptionError:
                    # Si falla con Fernet, intentar decodificar base64 directamente
                    try:
                        import base64
                        original = decrypted_data[field]
                        if len(original) > 50:
                            decoded = base64.b64decode(original)
                            decoded_str = decoded.decode('utf-8', errors='ignore')
                            if decoded_str and any(c.isprintable() for c in decoded_str[:50]):
                                decrypted_data[field] = decoded_str
                    except:
                        # Si todo falla, mantener el valor original
                        pass
        
        return decrypted_data


class EncryptionError(Exception):
    """Excepción personalizada para errores de encriptación"""
    pass


# Singleton global
_encryption_manager_instance = None

def get_encryption_manager() -> EncryptionManager:
    """Obtener instancia global del gestor de encriptación"""
    global _encryption_manager_instance
    if _encryption_manager_instance is None:
        _encryption_manager_instance = EncryptionManager()
    return _encryption_manager_instance

