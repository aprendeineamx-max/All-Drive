import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
import os
from time import monotonic

# ===== MEJORA #48: Manejo de Errores Mejorado =====
try:
    from error_handler import handle_error, AuthenticationError, ConnectionError as CustomConnectionError
    ERROR_HANDLING_AVAILABLE = True
except ImportError:
    ERROR_HANDLING_AVAILABLE = False

# ===== MEJORA #47: Sistema de Logging =====
try:
    from logger_manager import get_logger
    logger = get_logger(__name__)
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False
    logger = None

class S3Handler:
    def __init__(self, access_key, secret_key, host_base, *, cache_enabled=True, cache_ttl=None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.host_base = host_base
        self.last_error = None

        self.cache_enabled = cache_enabled
        default_cache_ttl = {
            'list_buckets': 60,
            'get_bucket_size': 300,
        }
        if cache_ttl:
            default_cache_ttl.update(cache_ttl)
        self.cache_ttl = default_cache_ttl
        self._cache = {}

        # Validar credenciales antes de crear el cliente
        if not access_key or not secret_key:
            error_msg = "Credenciales vacías. Verifica tu perfil."
            self.last_error = error_msg
            if LOGGING_AVAILABLE:
                logger.error(error_msg)
            raise ValueError(error_msg)

        if not host_base:
            error_msg = "Host base no especificado. Verifica tu perfil."
            self.last_error = error_msg
            if LOGGING_AVAILABLE:
                logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            self.session = boto3.session.Session()
            self.client = self.session.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                endpoint_url=f'https://{host_base}',
                config=Config(s3={'addressing_style': 'virtual'})
            )
            if LOGGING_AVAILABLE:
                logger.debug(f"S3Handler inicializado para {host_base}")
        except Exception as e:
            error_msg = f"Error al inicializar cliente S3: {str(e)}"
            self.last_error = error_msg
            if LOGGING_AVAILABLE:
                logger.error(error_msg)
            raise

    def list_buckets(self, *, use_cache=True):
        """
        Listar buckets disponibles

        Args:
            use_cache: Si es True, usar resultados en caché cuando estén disponibles.
        """
        self.last_error = None

        cache_key = self._build_cache_key()
        if use_cache:
            cached = self._get_from_cache('list_buckets', cache_key)
            if cached is not None:
                return cached

        try:
            if LOGGING_AVAILABLE:
                logger.debug(f"Intentando listar buckets desde {self.host_base}")

            response = self.client.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]

            if LOGGING_AVAILABLE:
                logger.info(f"Encontrados {len(buckets)} buckets: {buckets}")

            result = (buckets, None)
            self._set_cache('list_buckets', cache_key, result)
            return result

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = e.response.get('Error', {}).get('Message', str(e))

            # Errores comunes de autenticación
            if error_code in ['InvalidAccessKeyId', 'SignatureDoesNotMatch']:
                message = f"Credenciales inválidas. Verifica tu Access Key y Secret Key.\n\nError: {error_msg}"
                self.last_error = message
                if LOGGING_AVAILABLE:
                    logger.error(f"Error de autenticación: {error_code} - {error_msg}")
                if ERROR_HANDLING_AVAILABLE:
                    error = handle_error(AuthenticationError(message), context="list_buckets")
                    return [], error.message
                return [], message

            # Error de conexión
            elif error_code in ['EndpointConnectionError', 'ConnectionError']:
                message = f"No se pudo conectar al servidor {self.host_base}.\n\nVerifica:\n- Tu conexión a Internet\n- Que el host base sea correcto\n\nError: {error_msg}"
                self.last_error = message
                if LOGGING_AVAILABLE:
                    logger.error(f"Error de conexión: {error_code} - {error_msg}")
                if ERROR_HANDLING_AVAILABLE:
                    error = handle_error(CustomConnectionError(message), context="list_buckets")
                    return [], error.message
                return [], message

            # Otros errores
            else:
                message = f"Error al listar buckets: {error_msg}\n\nCódigo de error: {error_code}"
                self.last_error = message
                if LOGGING_AVAILABLE:
                    logger.error(f"Error al listar buckets: {error_code} - {error_msg}")
                return [], message

        except NoCredentialsError as e:
            message = "No se encontraron credenciales. Verifica tu perfil."
            self.last_error = message
            if LOGGING_AVAILABLE:
                logger.error(f"Error de credenciales: {str(e)}")
            return [], message

        except EndpointConnectionError as e:
            message = f"No se pudo conectar al endpoint {self.host_base}.\n\nVerifica:\n- Tu conexión a Internet\n- Que el host base sea correcto (ej: ewr1.vultrobjects.com)"
            self.last_error = message
            if LOGGING_AVAILABLE:
                logger.error(f"Error de conexión al endpoint: {str(e)}")
            if ERROR_HANDLING_AVAILABLE:
                error = handle_error(CustomConnectionError(message), context="list_buckets")
                return [], error.message
            return [], message

        except Exception as e:
            message = f"Error inesperado al listar buckets: {str(e)}"
            self.last_error = message
            if LOGGING_AVAILABLE:
                logger.error(f"Error inesperado: {str(e)}", exc_info=True)
            if ERROR_HANDLING_AVAILABLE:
                error = handle_error(e, context="list_buckets")
                return [], error.message
            return [], message

    def upload_file(self, bucket_name, file_path, object_name=None):
        if object_name is None:
            object_name = os.path.basename(file_path)

        try:
            self.client.upload_file(file_path, bucket_name, object_name)
            print(f"File {file_path} uploaded to {bucket_name}/{object_name}")
            if self.cache_enabled:
                self.clear_cache('get_bucket_size', self._build_cache_key(bucket_name))
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False

    def list_objects(self, bucket_name, prefix=''):
        try:
            response = self.client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except Exception as e:
            print(f"Error listing objects: {e}")
            return []

    def get_bucket_size(self, bucket_name, *, use_cache=True):
        """
        Obtener el tamaño total usado en un bucket

        Args:
            bucket_name: Nombre del bucket
            use_cache: Si es True, utilizar resultados en caché cuando estén disponibles.

        Returns:
            tuple: (size_bytes, error_message)
                   size_bytes: Tamaño total en bytes, None si hay error
                   error_message: Mensaje de error si hubo problema, None si fue exitoso
        """
        cache_key = self._build_cache_key(bucket_name)
        if use_cache:
            cached = self._get_from_cache('get_bucket_size', cache_key)
            if cached is not None:
                return cached

        try:
            if LOGGING_AVAILABLE:
                logger.debug(f"Calculando tamaño del bucket '{bucket_name}'")

            total_size = 0
            paginator = self.client.get_paginator('list_objects_v2')

            for page in paginator.paginate(Bucket=bucket_name):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        total_size += obj.get('Size', 0)

            if LOGGING_AVAILABLE:
                logger.info(f"Tamaño del bucket '{bucket_name}': {total_size} bytes ({total_size / (1024*1024):.2f} MB)")

            result = (total_size, None)
            self._set_cache('get_bucket_size', cache_key, result)
            return result

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
            message = f"Error al obtener tamaño del bucket: {error_msg}"

            if LOGGING_AVAILABLE:
                logger.error(f"Error al obtener tamaño del bucket: {error_code} - {error_msg}")

            if ERROR_HANDLING_AVAILABLE:
                error = handle_error(e, context="get_bucket_size")
                return None, error.message
            return None, message

        except Exception as e:
            message = f"Error inesperado al obtener tamaño del bucket: {str(e)}"
            if LOGGING_AVAILABLE:
                logger.error(f"Error inesperado: {str(e)}", exc_info=True)
            if ERROR_HANDLING_AVAILABLE:
                error = handle_error(e, context="get_bucket_size")
                return None, error.message
            return None, message

    def delete_object(self, bucket_name, object_name):
        try:
            self.client.delete_object(Bucket=bucket_name, Key=object_name)
            print(f"Deleted {object_name} from {bucket_name}")
            if self.cache_enabled:
                self.clear_cache('get_bucket_size', self._build_cache_key(bucket_name))
            return True
        except Exception as e:
            print(f"Error deleting object: {e}")
            return False

    def delete_all_objects(self, bucket_name):
        try:
            # List all objects
            paginator = self.client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket_name)

            delete_us = []
            for page in pages:
                if 'Contents' in page:
                    delete_us.extend([{'Key': obj['Key']} for obj in page['Contents']])

            # Delete in batches of 1000 (S3 limit)
            if delete_us:
                for i in range(0, len(delete_us), 1000):
                    batch = delete_us[i:i+1000]
                    self.client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': batch}
                    )
                print(f"Deleted {len(delete_us)} objects from {bucket_name}")
                if self.cache_enabled:
                    self.clear_cache('get_bucket_size', self._build_cache_key(bucket_name))

            return True
        except Exception as e:
            print(f"Error deleting all objects: {e}")
            return False

    def download_file(self, bucket_name, object_name, file_path):
        try:
            self.client.download_file(bucket_name, object_name, file_path)
            print(f"Downloaded {object_name} to {file_path}")
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False

    def _build_cache_key(self, *args, **kwargs):
        if not args and not kwargs:
            return ()
        if kwargs:
            # Ordenar kwargs para consistencia
            kw_items = tuple(sorted(kwargs.items()))
        else:
            kw_items = ()
        return (args, kw_items)

    def _get_from_cache(self, namespace, key):
        if not self.cache_enabled:
            return None
        namespace_cache = self._cache.get(namespace)
        if not namespace_cache:
            return None
        entry = namespace_cache.get(key)
        if not entry:
            return None
        expires_at, value = entry
        if monotonic() > expires_at:
            # Expirado
            namespace_cache.pop(key, None)
            if not namespace_cache:
                self._cache.pop(namespace, None)
            return None
        return value

    def _set_cache(self, namespace, key, value):
        if not self.cache_enabled:
            return
        ttl = self.cache_ttl.get(namespace)
        if not ttl:
            return
        namespace_cache = self._cache.setdefault(namespace, {})
        namespace_cache[key] = (monotonic() + ttl, value)

    def clear_cache(self, namespace=None, key=None):
        if not self.cache_enabled:
            return
        if namespace is None:
            self._cache.clear()
            return
        namespace_cache = self._cache.get(namespace)
        if not namespace_cache:
            return
        if key is None:
            namespace_cache.clear()
        else:
            namespace_cache.pop(key, None)
        if not namespace_cache:
            self._cache.pop(namespace, None)
    
    # ===== NUEVO: Gestión de Buckets =====
    
    def create_bucket(self, bucket_name, region=None):
        """
        Crear nuevo bucket en Object Storage.
        
        Args:
            bucket_name: Nombre del bucket (debe ser S3-compliant)
            region: Región (opcional, usa la del endpoint si no se especifica)
        
        Returns:
            (bool, str): (éxito, mensaje de error/éxito)
        """
        self.last_error = None
        
        # Validar nombre de bucket
        if not self._is_valid_bucket_name(bucket_name):
            error_msg = (
                f"Nombre de bucket inválido: '{bucket_name}'\n\n"
                "Reglas:\n"
                "• Solo minúsculas (a-z), números (0-9) y guiones (-)\n"
                "• Entre 3 y 63 caracteres\n"
                "• Debe empezar y terminar con letra o número\n"
                "• No puede contener guiones consecutivos (--)"
            )
            self.last_error = error_msg
            if LOGGING_AVAILABLE:
                logger.warning(f"Intento de crear bucket con nombre inválido: {bucket_name}")
            return (False, error_msg)
        
        try:
            if LOGGING_AVAILABLE:
                logger.info(f"Creando bucket: {bucket_name}")
            
            # Crear bucket (sin especificar LocationConstraint para Vultr)
            # Vultr Object Storage usa la región del endpoint automáticamente
            self.client.create_bucket(Bucket=bucket_name)
            
            # Invalidar caché de lista de buckets
            self.clear_cache('list_buckets')
            
            success_msg = f"Bucket '{bucket_name}' creado exitosamente"
            if LOGGING_AVAILABLE:
                logger.info(success_msg)
            
            return (True, success_msg)
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'BucketAlreadyExists':
                error_msg = f"El bucket '{bucket_name}' ya existe (propiedad de otra cuenta)"
            elif error_code == 'BucketAlreadyOwnedByYou':
                error_msg = f"Ya tienes un bucket llamado '{bucket_name}'"
            elif error_code == 'InvalidBucketName':
                error_msg = f"Nombre de bucket inválido: {error_message}"
            else:
                error_msg = f"Error al crear bucket: {error_message}"
            
            self.last_error = error_msg
            if LOGGING_AVAILABLE:
                logger.error(f"Error al crear bucket '{bucket_name}': {error_msg}")
            
            return (False, error_msg)
        
        except EndpointConnectionError as e:
            error_msg = f"Error de conexión con {self.host_base}. Verifica tu conexión a internet."
            self.last_error = error_msg
            if LOGGING_AVAILABLE:
                logger.error(f"Error de conexión al crear bucket: {e}")
            return (False, error_msg)
        
        except Exception as e:
            error_msg = f"Error inesperado al crear bucket: {str(e)}"
            self.last_error = error_msg
            if LOGGING_AVAILABLE:
                logger.error(f"Error inesperado al crear bucket '{bucket_name}': {e}", exc_info=True)
            return (False, error_msg)
    
    def delete_bucket(self, bucket_name, force=False):
        """
        Eliminar bucket de Object Storage.
        
        Args:
            bucket_name: Nombre del bucket a eliminar
            force: Si es True, elimina el bucket incluso si contiene objetos
                  (PELIGROSO: elimina todos los objetos sin confirmación adicional)
        
        Returns:
            (bool, str): (éxito, mensaje de error/éxito)
        """
        self.last_error = None
        
        try:
            if LOGGING_AVAILABLE:
                logger.info(f"Eliminando bucket: {bucket_name} (force={force})")
            
            # Verificar si el bucket está vacío
            try:
                response = self.client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
                has_objects = 'Contents' in response
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchBucket':
                    error_msg = f"El bucket '{bucket_name}' no existe"
                    self.last_error = error_msg
                    return (False, error_msg)
                raise
            
            # Si contiene objetos y no se especificó force
            if has_objects and not force:
                error_msg = (
                    f"El bucket '{bucket_name}' contiene archivos.\n\n"
                    f"Para eliminarlo junto con su contenido, usa la opción 'Forzar eliminación'.\n"
                    f"⚠️ Esta acción es IRREVERSIBLE."
                )
                self.last_error = error_msg
                if LOGGING_AVAILABLE:
                    logger.warning(f"Intento de eliminar bucket no vacío sin force: {bucket_name}")
                return (False, error_msg)
            
            # Si force=True y hay objetos, eliminarlos todos primero
            if force and has_objects:
                if LOGGING_AVAILABLE:
                    logger.info(f"Eliminando todos los objetos del bucket {bucket_name}...")
                
                success = self.delete_all_objects(bucket_name)
                if not success:
                    error_msg = f"Error al eliminar los objetos del bucket '{bucket_name}'"
                    self.last_error = error_msg
                    return (False, error_msg)
            
            # Eliminar el bucket
            self.client.delete_bucket(Bucket=bucket_name)
            
            # Invalidar cachés relevantes
            self.clear_cache('list_buckets')
            self.clear_cache('get_bucket_size')
            
            success_msg = f"Bucket '{bucket_name}' eliminado exitosamente"
            if LOGGING_AVAILABLE:
                logger.info(success_msg)
            
            return (True, success_msg)
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'NoSuchBucket':
                error_msg = f"El bucket '{bucket_name}' no existe"
            elif error_code == 'BucketNotEmpty':
                error_msg = (
                    f"El bucket '{bucket_name}' aún contiene objetos. "
                    "Usa 'Forzar eliminación' para eliminar el bucket y su contenido."
                )
            else:
                error_msg = f"Error al eliminar bucket: {error_message}"
            
            self.last_error = error_msg
            if LOGGING_AVAILABLE:
                logger.error(f"Error al eliminar bucket '{bucket_name}': {error_msg}")
            
            return (False, error_msg)
        
        except Exception as e:
            error_msg = f"Error inesperado al eliminar bucket: {str(e)}"
            self.last_error = error_msg
            if LOGGING_AVAILABLE:
                logger.error(f"Error inesperado al eliminar bucket '{bucket_name}': {e}", exc_info=True)
            return (False, error_msg)
    
    def _is_valid_bucket_name(self, name):
        """
        Validar nombre de bucket según reglas S3.
        
        Reglas:
        - Longitud: 3-63 caracteres
        - Solo minúsculas, números y guiones
        - Debe empezar y terminar con letra o número
        - No puede contener guiones consecutivos
        - No puede ser una dirección IP
        
        Args:
            name: Nombre del bucket a validar
        
        Returns:
            bool: True si es válido, False en caso contrario
        """
        import re
        
        if not name or not isinstance(name, str):
            return False
        
        # Longitud: 3-63 caracteres
        if len(name) < 3 or len(name) > 63:
            return False
        
        # Solo minúsculas, números y guiones
        # Debe empezar y terminar con letra o número
        if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', name):
            # Caso especial: nombre de 3 caracteres sin guiones (ej: "abc")
            if len(name) == 3 and re.match(r'^[a-z0-9]+$', name):
                return True
            return False
        
        # No puede tener guiones consecutivos
        if '--' in name:
            return False
        
        # No puede ser una IP (formato xxx.xxx.xxx.xxx)
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', name):
            return False
        
        return True

