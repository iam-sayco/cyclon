"""CLI entry point for Cyclon."""

from cyclon.app import CyclonApp
from cyclon.services import ConfigService, FileService, ProcessService


def main() -> None:
    config_service = ConfigService()
    file_service = FileService()
    process_service = ProcessService()
    
    app = CyclonApp(config_service, file_service, process_service)
    app.run()
