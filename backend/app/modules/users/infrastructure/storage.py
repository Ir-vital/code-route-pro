"""
Implémentation Supabase Storage du service de stockage.
"""

from app.core.config import settings
from app.modules.users.application.use_cases import IStorageService


class SupabaseStorageService(IStorageService):
    """
    Upload vers Supabase Storage via la librairie supabase-py.
    """

    def __init__(self) -> None:
        try:
            from supabase import create_client
            self._client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        except ImportError:
            self._client = None

    async def upload(
        self,
        bucket: str,
        path: str,
        content: bytes,
        content_type: str,
    ) -> str:
        if not self._client:
            raise RuntimeError("Supabase client non disponible. Vérifiez les variables SUPABASE_URL et SUPABASE_KEY.")

        response = self._client.storage.from_(bucket).upload(
            path=path,
            file=content,
            file_options={"content-type": content_type, "upsert": "true"},
        )
        public_url = self._client.storage.from_(bucket).get_public_url(path)
        return public_url
