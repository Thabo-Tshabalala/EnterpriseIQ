
# Pattern: Prototype
# Use Case: Cloning pre-configured VectorEmbedding templates.
# Justification: Generating a real embedding vector is computationally expensive
# (it requires a full forward pass through the embedding model). In testing and
# batch processing scenarios, it is more efficient to clone a pre-configured
# VectorEmbedding prototype and only change the chunk-specific attributes
# (chunk_text, chunk_index, page_number), reusing the existing vector structure.

import copy
from src.models import VectorEmbedding, NamespaceId


class EmbeddingPrototypeCache:
    """
    Stores pre-configured VectorEmbedding prototypes keyed by namespace.
    Returns deep clones to avoid sharing mutable state between instances.
    """

    def __init__(self):
        self._prototypes: dict = {}
        self._initialise_prototypes()

    def _initialise_prototypes(self) -> None:
        """Creates one baseline prototype per namespace at startup."""
        for namespace in NamespaceId:
            prototype = VectorEmbedding(
                embedding_id=f"prototype-{namespace.value}",
                document_id="prototype-doc",
                namespace=namespace,
                chunk_text="",
                chunk_index=0,
                page_number=1
            )
            # Pre-generate a stub vector on the prototype
            prototype.generate("prototype text")
            self._prototypes[namespace] = prototype

    def get_clone(self, namespace: NamespaceId, embedding_id: str,
                  document_id: str, chunk_text: str,
                  chunk_index: int, page_number: int) -> VectorEmbedding:
        """
        Returns a deep clone of the namespace prototype,
        with chunk-specific attributes updated.
        """
        if namespace not in self._prototypes:
            raise ValueError(f"No prototype registered for namespace: {namespace}")

        cloned = self._prototypes[namespace].clone()
        # Update chunk-specific attributes on the clone
        cloned._embedding_id = embedding_id
        cloned._document_id = document_id
        cloned._chunk_text = chunk_text
        cloned._chunk_index = chunk_index
        cloned._page_number = page_number
        return cloned

    def register_prototype(self, namespace: NamespaceId, prototype: VectorEmbedding) -> None:
        """Allows registering a custom prototype for a namespace."""
        self._prototypes[namespace] = prototype
