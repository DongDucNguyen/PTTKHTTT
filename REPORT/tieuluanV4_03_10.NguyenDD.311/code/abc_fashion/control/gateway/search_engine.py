# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.gateway.search_engine) -- do not edit the signatures.
from __future__ import annotations



class SearchEngine:
    """SearchEngine -- layer abc_fashion.control.gateway."""

    def search_by_image(self, image: bytes):
        raise NotImplementedError

    def search_by_voice(self, audio: bytes):
        raise NotImplementedError
