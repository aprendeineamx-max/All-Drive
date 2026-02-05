"""
Gestor de tareas asincrónicas reutilizable basado en QThreadPool.

Permite ejecutar funciones en segundo plano sin bloquear la UI y propaga
resultados, errores y progreso mediante señales de Qt.
"""

from typing import Any, Callable, Optional

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal

try:
    from logger_manager import get_logger

    _logger = get_logger(__name__)
except ImportError:  # pragma: no cover - fallback defensivo
    _logger = None


class _WorkerSignals(QObject):
    """Señales emitidas por cada tarea."""

    success = pyqtSignal(object)
    error = pyqtSignal(object)
    finished = pyqtSignal()
    progress = pyqtSignal(int, object)


class _TaskWorker(QRunnable):
    """
    Envuelve la ejecución de una función en un QRunnable y expone señales.
    """

    def __init__(
        self,
        fn: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        description: Optional[str],
        logger,
        provide_progress: bool,
    ) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.description = description or fn.__name__
        self.signals = _WorkerSignals()
        self._logger = logger
        self._provide_progress = provide_progress

    def run(self) -> None:  # pragma: no cover - ejecutado en hilos
        """Ejecuta la función en un hilo del pool."""
        try:
            if self._provide_progress and "progress_callback" not in self.kwargs:
                self.kwargs["progress_callback"] = self.signals.progress

            result = self.fn(*self.args, **self.kwargs)
        except Exception as exc:  # noqa: BLE001
            if self._logger:
                self._logger.error(
                    "Tarea '%s' falló: %s", self.description, str(exc), exc_info=True
                )
            self.signals.error.emit(exc)
        else:
            self.signals.success.emit(result)
        finally:
            self.signals.finished.emit()


class TaskRunner(QObject):
    """
    Administrador ligero de tareas en segundo plano.

    Ejemplo de uso:

        runner = TaskRunner(self)
        runner.run(
            trabajo_largo,
            arg1,
            arg2,
            on_success=self._manejar_resultado,
            on_error=self._manejar_error,
            description="calcular_estadisticas",
        )
    """

    def __init__(self, parent: Optional[QObject] = None, max_workers: Optional[int] = None) -> None:
        super().__init__(parent)
        self._pool = QThreadPool(parent)
        if max_workers:
            self._pool.setMaxThreadCount(max_workers)
        self._logger = _logger

    def run(
        self,
        fn: Callable[..., Any],
        *args: Any,
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_finished: Optional[Callable[[], None]] = None,
        on_progress: Optional[Callable[[int, Any], None]] = None,
        description: Optional[str] = None,
        provide_progress: bool = False,
        **kwargs: Any,
    ) -> _TaskWorker:
        """
        Ejecuta una función en segundo plano y conecta los manejadores.

        Args:
            fn: Función a ejecutar.
            *args: Argumentos posicionales.
            on_success: Callback en hilo principal con el resultado.
            on_error: Callback en hilo principal con la excepción (objeto).
            on_finished: Callback cuando la tarea termina (éxito o error).
            on_progress: Callback para progreso (int, datos extra).
            description: Texto para logging/depuración.
            provide_progress: Inyecta progress_callback en kwargs si no existe.
            **kwargs: Argumentos nombrados para la función.

        Returns:
            Instancia de `_TaskWorker`, útil para inspección o pruebas.
        """

        worker = _TaskWorker(
            fn=fn,
            args=args,
            kwargs=kwargs,
            description=description,
            logger=self._logger,
            provide_progress=provide_progress or on_progress is not None,
        )

        if on_success:
            worker.signals.success.connect(on_success)
        if on_error:
            worker.signals.error.connect(on_error)
        if on_finished:
            worker.signals.finished.connect(on_finished)
        if on_progress:
            worker.signals.progress.connect(on_progress)

        if self._logger:
            self._logger.debug("Ejecutando tarea '%s'", worker.description)

        self._pool.start(worker)
        return worker

    def set_max_workers(self, count: int) -> None:
        """Permite ajustar dinámicamente el número de hilos."""
        self._pool.setMaxThreadCount(count)

    def active_tasks(self) -> int:
        """Retorna cuántas tareas están en ejecución actualmente."""
        return self._pool.activeThreadCount()

